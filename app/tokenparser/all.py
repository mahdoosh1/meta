from .highlighter import TokenDescHighlighter, metaclass_LexerTestHighlighter as metaclass
from .lexer import Lexer
from .parser import Parser, organize_pattern
# from .use import use

def metaclass_LexerTextHighlighter(description: str):
    lexed = Lexer(description).tokenize()
    parsed = Parser(lexed).parse()
    organized = organize_pattern(parsed)
    meta = metaclass(organized)
    return meta