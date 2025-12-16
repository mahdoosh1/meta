from .highlighter import TokenDescHighlighter, metaclass_LexerTestHighlighter as metaclass
from .lexer import Lexer
from .parser import Parser, organize_pattern
from .use import use

def organizer(description):
    lexed = Lexer(description).tokenize()
    parsed = Parser(lexed).parse()
    organized = organize_pattern(parsed)
    return organized

def lexer(organized, text):
    return use(organized, text)

def metaclass_LexerTextHighlighter(organized):
    meta = metaclass(organized)
    return meta

def coord_token(lexed, line, column):
    i = 0
    current = lexed[i]
    max_len = len(lexed)
    while current[3] < line and i < max_len:
        i += 1
        current = lexed[i]
    while current[4] < column and i < max_len:
        i += 1
        current = lexed[i]
    return lexed[i-1]