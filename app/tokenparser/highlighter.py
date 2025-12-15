from PySide6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor # type: ignore
from PySide6.QtCore import QRegularExpression # type: ignore
from .parser import patternpairtype
import re

class TokenDescHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.rules = []

        # 1. Base Identifier (Skyblue) -> SubToken
        # We apply this first. Specific rules below will overwrite this.
        sub_token_fmt = QTextCharFormat()
        sub_token_fmt.setForeground(QColor("#9CDCFE")) # Skyblue
        self.rules.append((QRegularExpression(r'\b[a-zA-Z_]\w*\b[^"]'), sub_token_fmt))

        # 2. Categories (Purple) -> Special, Normal
        # Overwrites SubToken color for these specific words
        category_fmt = QTextCharFormat()
        category_fmt.setForeground(QColor("#C586C0")) # Purple
        self.rules.append((QRegularExpression(r'\b(Special|Normal)\b'), category_fmt))

        # 3. TokenName (Yellow)
        # Identifier followed by '{'. 
        # Regex: Identifier (?= lookahead for whitespace and {)
        token_name_fmt = QTextCharFormat()
        token_name_fmt.setForeground(QColor("#DCDCAA")) # Yellow
        self.rules.append((QRegularExpression(r'\b[a-zA-Z_]\w*\b(?=\s*\{)'), token_name_fmt))

        # 4. Symbols (White) -> { } [ ] ,
        # Overwrites previous if matched
        symbol_fmt = QTextCharFormat()
        symbol_fmt.setForeground(QColor("#FFFFFF")) # White
        self.rules.append((QRegularExpression(r'[\[\]{},]'), symbol_fmt))

        # 5. Pattern (Green) -> r"..."
        pattern_fmt = QTextCharFormat()
        pattern_fmt.setForeground(QColor("#6A9955")) # Green
        self.rules.append((QRegularExpression(r'"([^\"\\]|\\[\s\S])*"'), pattern_fmt))

        # 5. Pattern (Green) -> r"..."
        pattern_fmt = QTextCharFormat()
        pattern_fmt.setForeground(QColor("#CE6021")) # Green
        self.rules.append((QRegularExpression(r'#[0-9a-fA-F]{6}'), pattern_fmt))

    def highlightBlock(self, text):
        # Loop through rules. Later rules in the list overwrite earlier ones 
        # (if using setFormat on the same range).
        # Our order: SubToken -> Category -> TokenName -> Pattern -> Symbol
        for pattern, format in self.rules:
            iterator = pattern.globalMatch(text)
            while iterator.hasNext():
                match = iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), format)

def metaclass_LexerTestHighlighter(patternpair: patternpairtype):
    normals = []
    specials = []
    exceptional = []
    for pattern, _, category, _, color in patternpair:
        pattern = f"(?:{pattern.pattern})"
        if category == 'Normal' and color == "":
            normals.append(pattern)
        elif category == 'Special' and color == "":
            specials.append(pattern)
        elif color:
            exceptional.append((pattern, color))
    normal_re = ("|".join(normals)) if normals else r"(?!x)x"
    special_re = ("|".join(specials)) if specials else r"(?!x)x"
    class Highlighter(QSyntaxHighlighter):
        def __init__(self, parent=None):
            super().__init__(parent)
            self.rules = []

            #symbol_fmt = QTextCharFormat()
            #symbol_fmt.setForeground(QColor("#FFFFFF")) # White
            #self.rules.append((QRegularExpression(r'[\[\]{},]'), symbol_fmt))

            normal_token_fmt = QTextCharFormat()
            normal_token_fmt.setForeground(QColor("#DCDCAA")) # Yellow
            self.rules.append((QRegularExpression(normal_re), normal_token_fmt))
            
            for pattern, color in exceptional:
                exceptional_token_fmt = QTextCharFormat()
                exceptional_token_fmt.setForeground(QColor(color))
                self.rules.append((QRegularExpression(pattern), exceptional_token_fmt))

            special_token_fmt = QTextCharFormat()
            special_token_fmt.setForeground(QColor("#9CDCFE")) # Skyblue
            self.rules.append((QRegularExpression(special_re), special_token_fmt))


        def highlightBlock(self, text):
            # Loop through rules. Later rules in the list overwrite earlier ones 
            # (if using setFormat on the same range).
            # Our order: SubToken -> Category -> TokenName -> Pattern -> Symbol
            for pattern, format in self.rules:
                iterator = pattern.globalMatch(text)
                while iterator.hasNext():
                    match = iterator.next()
                    self.setFormat(match.capturedStart(), match.capturedLength(), format)
    return Highlighter
