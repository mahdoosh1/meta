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
patternpairtype = list[tuple[re.Pattern, str, str, str, str]]


class Parser:
    def __init__(self, lexed: list[Token]):
        self.lexed = lexed
        self.index = 0
        self.tree = None
    
    def current(self):
        if self.index < len(self.lexed):
            return self.lexed[self.index]
        return self.lexed[-1]
    
    def consume(self, tokentype:TokenType, current=None):
        if current is not None:
            if current.type != tokentype:
                raise Exception(f":{current.line}:{current.column} (pos: {current.position}) got {current.type}")
            return current
        current = self.current()
        if current.type == tokentype:
            self.index += 1
            return current
        raise Exception(f":{current.line}:{current.column} (pos: {current.position}) got {current.type}")
    
    def parse_pattern(self):
        pattern = self.consume(TokenType.STRING).value
        pattern = re.compile(ast.literal_eval(pattern))
        return {'pattern':pattern}
    
    def parse_color(self):
        color = self.consume(TokenType.COLOR).value
        return {'color': color}
    
    def parse_subtokens(self):
        self.consume(TokenType.LBRACKET)
        subtokens = {}
        while True:
            name = self.consume(TokenType.IDENTIFIER).value
            pattern = self.parse_pattern()
            if self.current().type == TokenType.COLOR:
                pattern.update(self.parse_color())
            subtokens[name] = pattern
            current = self.current()
            self.index += 1
            if current.type == TokenType.RBRACKET:
                break
            self.consume(TokenType.COMMA,current)
        return {'subtokens':subtokens}
    
    def parse_category(self):
        name = self.consume(TokenType.IDENTIFIER).value
        if self.current().type == TokenType.LBRACKET:
            info = self.parse_subtokens()
        else:
            info = self.parse_pattern()
        if self.current().type == TokenType.COLOR:
            info |= self.parse_color()
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
        categories = list(desc['categories'].items())
        categories.sort(key=lambda i:i[0]=='Special')
        for category, info in categories:
            catcolor = info.get('color') or ""
            if category == 'Normal':
                patterns.append((info['pattern'], name, category, "", catcolor))
                continue
            elif category == 'Special':
                for subtoken, subinfo in info['subtokens'].items(): # type: ignore
                    color = subinfo.get('color') or catcolor
                    patterns.append((subinfo['pattern'], name, category, subtoken, color))
            else:
                raise NotImplementedError()
    #patterns.sort(key=lambda i:i[2]=='Special')
    return patterns