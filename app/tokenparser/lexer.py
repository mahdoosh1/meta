import sys
from enum import Enum, auto

class TokenType(Enum):
    IDENTIFIER = auto()  # TokenName, Category, SubToken
    STRING = auto()      # r"..."
    LBRACE = auto()      # {
    RBRACE = auto()      # }
    LBRACKET = auto()    # [
    RBRACKET = auto()    # ]
    COMMA = auto()       # ,
    UNKNOWN = auto()
    EOF = auto()

class Token:
    def __init__(self, type, value, line=0, column=0):
        self.type = type
        self.value = value
        self.line = line
        self.column = column

    def __repr__(self):
        return f"Token({self.type.name}, '{self.value}')"

class Lexer:
    """
    Lexer for the Token Description Language.
    Input: "Identifier { Special r'if' }"
    Output: Stream of Token objects.
    """
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.line = 1
        self.column = 1
        self.current_char = self.text[0] if self.text else ""

    def advance(self):
        if self.current_char == '\n':
            self.line += 1
            self.column = 0
        
        self.pos += 1
        if self.pos < len(self.text):
            self.current_char = self.text[self.pos]
            self.column += 1
        else:
            self.current_char = ""

    def skip_whitespace(self):
        while self.current_char != "" and self.current_char.isspace():
            self.advance()

    def read_identifier(self):
        result = ''
        while self.current_char != "" and (self.current_char.isalnum() or self.current_char == '_'):
            result += self.current_char
            self.advance()
        return Token(TokenType.IDENTIFIER, result, self.line, self.column)

    def read_string(self):
        # Expecting r"..."
        result = ''
        # Consume 'r'
        result += self.current_char
        self.advance()
        
        # Check for quote
        if self.current_char != '"':
            return Token(TokenType.UNKNOWN, result, self.line, self.column)
        
        result += self.current_char
        self.advance()

        while self.current_char != "" and self.current_char != '"':
            if self.current_char == '\\': # Handle escape
                result += self.current_char
                self.advance()
            result += self.current_char
            self.advance()

        if self.current_char == '"':
            result += self.current_char
            self.advance()
        
        return Token(TokenType.STRING, result, self.line, self.column)

    def get_next_token(self):
        while self.current_char != "":
            if self.current_char.isspace():
                self.skip_whitespace()
                continue

            if self.current_char.isalpha():
                # Check if it is start of r"..."
                if self.current_char == 'r' and self.pos + 1 < len(self.text) and self.text[self.pos+1] == '"':
                    return self.read_string()
                return self.read_identifier()

            if self.current_char == '{':
                self.advance()
                return Token(TokenType.LBRACE, '{', self.line, self.column)
            
            if self.current_char == '}':
                self.advance()
                return Token(TokenType.RBRACE, '}', self.line, self.column)

            if self.current_char == '[':
                self.advance()
                return Token(TokenType.LBRACKET, '[', self.line, self.column)

            if self.current_char == ']':
                self.advance()
                return Token(TokenType.RBRACKET, ']', self.line, self.column)

            if self.current_char == ',':
                self.advance()
                return Token(TokenType.COMMA, ',', self.line, self.column)

            # Unknown char
            char = self.current_char
            self.advance()
            return Token(TokenType.UNKNOWN, char, self.line, self.column)

        return Token(TokenType.EOF, '', self.line, self.column)

    def tokenize(self):
        tokens = []
        while True:
            token = self.get_next_token()
            tokens.append(token)
            if token.type == TokenType.EOF:
                break
        return tokens

