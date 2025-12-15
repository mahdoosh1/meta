import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QPushButton, QListWidget, QTabWidget, 
                               QSplitter, QPlainTextEdit, QLabel, QFrame)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QSyntaxHighlighter

# Assumes tokenparser package exists as per your import
from tokenparser.all import TokenDescHighlighter, metaclass_LexerTextHighlighter

class ActivityButton(QPushButton):
    def __init__(self, text, active=False):
        super().__init__(text)
        self.setFixedSize(50, 50)
        self.setCursor(Qt.PointingHandCursor)
        self.active = active
        self._apply_style()

    def _apply_style(self):
        border = "border-left: 2px solid #ffffff;" if self.active else "border: none;"
        color = "#ffffff" if self.active else "#858585"
        self.setStyleSheet(f"""
            QPushButton {{ background-color: #333333; color: {color}; border: none; {border} font-size: 16px; }}
            QPushButton:hover {{ color: #ffffff; }}
        """)

class IDEWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MetaSyntax")
        self.resize(1100, 700)
        self.setStyleSheet("background-color: #1e1e1e; font-family: 'Ubuntu Mono', sans-serif;")

        # Layout Setup
        central = QWidget()
        self.setCentralWidget(central)
        self.main_layout = QHBoxLayout(central)
        self.main_layout.setSpacing(0)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        self._init_activity_bar()
        #self._init_sidebar()
        self._init_editor_area()

        # Highlighter Initialization & Signal Connection
        self.hl_def = TokenDescHighlighter(self.def_edit.document())
        self.hl_test = None
        self.update_test_highlighter() # Initial build

        # Re-build test highlighter when definition changes
        self.def_edit.textChanged.connect(self.update_test_highlighter)

    def _init_activity_bar(self):
        bar = QFrame()
        bar.setFixedWidth(50)
        bar.setStyleSheet("background-color: #333333;")
        layout = QVBoxLayout(bar)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        for char, active in [("F", False), ("T", True), ("G", False), ("D", False)]:
            layout.addWidget(ActivityButton(char, active))
        layout.addStretch()
        self.main_layout.addWidget(bar)

    def _init_sidebar(self):
        sidebar = QFrame()
        sidebar.setFixedWidth(220)
        sidebar.setStyleSheet("background-color: #252526;")
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(0, 0, 0, 0)

        title = QLabel("TOKENS")
        title.setStyleSheet("color: #BBBBBB; font-size: 11px; font-weight: bold; padding: 10px;")
        layout.addWidget(title)

        add_btn = QPushButton("Add")
        add_btn.setStyleSheet("QPushButton { background-color: #007acc; color: white; border: none; padding: 6px; } QPushButton:hover { background-color: #0098ff; }")
        
        btn_wrap = QWidget()
        btn_layout = QVBoxLayout(btn_wrap)
        btn_layout.addWidget(add_btn)
        layout.addWidget(btn_wrap)

        token_list = QListWidget()
        token_list.setStyleSheet("QListWidget { border: none; background: transparent; color: #CCCCCC; outline: none; } QListWidget::item { padding: 5px; } QListWidget::item:selected { background-color: #37373d; }")
        token_list.addItems(["Identifier", "Symbol"])
        layout.addWidget(token_list)
        self.main_layout.addWidget(sidebar)

    def _init_editor_area(self):
        tabs = QTabWidget()
        tabs.setDocumentMode(True)
        tabs.setStyleSheet("""
            QTabWidget::pane { border: none; background: #1e1e1e; }
            QTabBar::tab { background: #2d2d2d; color: #969696; padding: 8px 15px; border-right: 1px solid #252526; }
            QTabBar::tab:selected { background: #1e1e1e; color: #ffffff; border-top: 1px solid #007acc; }
        """)

        # Token Tab
        token_widget = QWidget()
        token_layout = QHBoxLayout(token_widget)
        token_layout.setContentsMargins(0, 0, 0, 0)

        # Splitters
        h_split = QSplitter(Qt.Horizontal)
        h_split.setHandleWidth(1)
        h_split.setStyleSheet("QSplitter::handle { background-color: #3e3e42; }")
        
        v_split = QSplitter(Qt.Vertical)
        v_split.setHandleWidth(1)

        # Editors
        self.def_edit = self._create_editor('Identifier {\n    Special [\n        If r"if" ,\n        Else r"else"\n    ]\n    Normal r"[a-zA-Z_][a-zA-Z_0-9]*"\n}\nSymbol {\n    Special [\n        LeftParen r"\\(" ,\n        RightParen r"\\)"\n    ]\n}')
        self.test_edit = self._create_editor('if (condition){\n    this();\n} else {\n    that();\n}')

        # Info Panel
        info_panel = QWidget()
        info_panel.setStyleSheet("background-color: #252526;")
        info_layout = QVBoxLayout(info_panel)
        info_layout.setContentsMargins(0,0,0,0)
        
        info_head = QLabel("Selected Token")
        info_head.setStyleSheet("background-color: #333333; color: #CCCCCC; padding: 5px; font-size: 11px;")
        info_layout.addWidget(info_head)
        
        info_body = QLabel("if (cond...\n\nIdentifier[If] (Special)")
        info_body.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        info_body.setStyleSheet("color: #d4d4d4; padding: 10px; font-family: Consolas; font-size: 12px;")
        info_layout.addWidget(info_body)

        # Assemble
        v_split.addWidget(self.test_edit)
        v_split.addWidget(info_panel)
        v_split.setSizes([400, 200])

        h_split.addWidget(self.def_edit)
        h_split.addWidget(v_split)
        h_split.setSizes([500, 400])

        token_layout.addWidget(h_split)
        tabs.addTab(token_widget, "Tokens")
        tabs.addTab(QWidget(), "Parsing")
        self.main_layout.addWidget(tabs)

    def _create_editor(self, text):
        edit = QPlainTextEdit()
        edit.setFrameShape(QFrame.NoFrame)
        edit.setFont(QFont("Ubuntu Mono", 12))
        edit.setStyleSheet("background-color: #1e1e1e; color: #d4d4d4;")
        edit.setPlainText(text)
        return edit

    def update_test_highlighter(self):
        """Recreates the test highlighter based on current definitions."""
        if self.hl_test:
            self.hl_test.setDocument(None)
            self.hl_test.deleteLater()
            self.hl_test = None

        try:
            # Generate new Class from current text and Instantiate
            GeneratedHighlighter = metaclass_LexerTextHighlighter(self.def_edit.toPlainText())
            self.hl_test = GeneratedHighlighter(self.test_edit.document())
            
            # Force refresh
            self.test_edit.document().markContentsDirty(0, self.test_edit.document().characterCount())
        except Exception as e:
            # Prevents crash if regex/def is temporarily invalid while typing
            print(f"Highlighter update skipped: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = IDEWindow()
    window.show()
    sys.exit(app.exec())