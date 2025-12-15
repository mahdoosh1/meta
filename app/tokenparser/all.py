from .highlighter import TokenDescHighlighter, metaclass_LexerTestHighlighter as metaclass
from .lexer import Lexer
from .parser import Parser, organize_pattern
# from .use import use

def metaclass_LexerTextHighlighter(description: str):
    return metaclass(organize_pattern(Parser(Lexer(description).tokenize()).parse()))