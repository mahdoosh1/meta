from .lexer import Token, TokenType
from typing import Union
import ast, re

# patterntype = {'pattern': re.Pattern}
patterntype = dict[str, re.Pattern]

# parsetype = {tokenname: 
#   {'categories': 
#       {category: 
#           {'subtokens': 
#               {subtokenname: 
#                   patterntype
#               }
#           } |
#           patterntype
#       }
#   }
# }
parsetype = dict[str, dict[str, dict[str, Union[patterntype, dict[str, dict[str, patterntype]]]]]]

# [(pattern, tokenname, category, subtokenname)]
patternpairtype = list[tuple[re.Pattern, str, str, str]]


class Parser:
    def __init__(self, lexed: list[Token]):
        self.lexed = lexed
        self.index = 0
        self.tree = None
    
    def current(self):
        if self.index < len(self.lexed):
            return self.lexed[self.index]
        return self.lexed[-1]
    
    def consume(self, tokentype:TokenType):
        current = self.current()
        if current.type == tokentype:
            self.index += 1
            return current
        raise Exception()
    
    def parse_pattern(self):
        pattern = self.consume(TokenType.STRING).value
        pattern = re.compile(ast.literal_eval(pattern))
        return {'pattern':pattern}
    
    def parse_subtokens(self):
        self.consume(TokenType.LBRACKET)
        subtokens = {}
        while True:
            name = self.consume(TokenType.IDENTIFIER).value
            pattern = self.parse_pattern()
            subtokens[name] = pattern
            current = self.current()
            self.index += 1
            if current.type == TokenType.RBRACKET:
                break
        return {'subtokens':subtokens}
    
    def parse_category(self):
        name = self.consume(TokenType.IDENTIFIER).value
        if self.current().type == TokenType.LBRACKET:
            info = self.parse_subtokens()
        else:
            info = self.parse_pattern()
        return name, info
    
    def parse_token(self):
        name = self.consume(TokenType.IDENTIFIER).value
        self.consume(TokenType.LBRACE)
        categories = {}
        while self.current().type != TokenType.RBRACE:
            category_name, info = self.parse_category()
            categories[category_name] = info
        self.index += 1
        return name, {'categories': categories}
    
    def parse(self) -> parsetype:
        tokens = {}
        while self.current().type not in (TokenType.EOF,):
            name, desc = self.parse_token()
            tokens[name] = desc
        return tokens
    
def organize_pattern(tokens: parsetype) -> patternpairtype:
    patterns = []
    for name, desc in tokens.items():
        categories = desc['categories']
        for category, info in categories.items():
            if category == 'Normal':
                patterns.append((info['pattern'], name, category, ""))
                continue
            elif category == 'Special':
                for subtoken, pattern in info['subtokens'].items(): # type: ignore
                    patterns.append((pattern['pattern'], name, category, subtoken))
            else:
                raise NotImplementedError()
    return patterns