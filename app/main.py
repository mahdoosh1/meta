import sys
import re
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QPushButton, QListWidget, QTabWidget, 
                               QSplitter, QPlainTextEdit, QLabel, QFrame)
from PySide6.QtCore import Qt, QSize, QRegularExpression
from PySide6.QtGui import QColor, QPalette, QFont, QSyntaxHighlighter, QTextCharFormat, QBrush

from tokenparser.all import TokenDescHighlighter, metaclass_LexerTextHighlighter
# --- 2. Custom Components ---
class ActivityButton(QPushButton):
    def __init__(self, text, active=False):
        super().__init__(text)
        self.setFixedSize(50, 50)
        self.setCursor(Qt.PointingHandCursor)
        self.active = active
        self.update_style()

    def update_style(self):
        border = "border-left: 2px solid #ffffff;" if self.active else "border: none;"
        color = "#ffffff" if self.active else "#858585"
        self.setStyleSheet(f"""
            QPushButton {{ 
                background-color: #333333; 
                color: {color}; 
                border: none;
                {border}
                font-size: 16px;
            }}
            QPushButton:hover {{ color: #ffffff; }}
        """)

class SidebarItem(QWidget):
    def __init__(self, text, bg_color="#252526"):
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 2, 10, 2)
        label = QLabel(text)
        label.setStyleSheet("color: #CCCCCC; font-size: 13px;")
        layout.addWidget(label)
        self.setStyleSheet(f"background-color: {bg_color};")

# --- 3. Main Window ---
class IDEWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Token/Parser IDE")
        self.resize(1100, 700)
        self.setStyleSheet("background-color: #1e1e1e; font-family: 'Segoe UI', sans-serif;")

        # Central Widget
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # --- A. Activity Bar ---
        activity_bar = QFrame()
        activity_bar.setFixedWidth(50)
        activity_bar.setStyleSheet("background-color: #333333;")
        act_layout = QVBoxLayout(activity_bar)
        act_layout.setContentsMargins(0, 0, 0, 0)
        act_layout.setSpacing(0)
        
        # Buttons (Files, Search, etc. - using text as placeholder)
        act_layout.addWidget(ActivityButton("F"))
        act_layout.addWidget(ActivityButton("T", active=True)) # Tokens selected
        act_layout.addWidget(ActivityButton("G"))
        act_layout.addWidget(ActivityButton("D"))
        act_layout.addStretch()
        
        # --- B. Sidebar ---
        sidebar = QFrame()
        sidebar.setFixedWidth(220)
        sidebar.setStyleSheet("background-color: #252526;")
        side_layout = QVBoxLayout(sidebar)
        side_layout.setContentsMargins(0, 0, 0, 0)
        
        # Title "Tokens"
        title_lbl = QLabel("TOKENS")
        title_lbl.setStyleSheet("color: #BBBBBB; font-size: 11px; font-weight: bold; padding: 10px;")
        side_layout.addWidget(title_lbl)

        # "Add" Button area
        btn_container = QWidget()
        btn_layout = QVBoxLayout(btn_container)
        add_btn = QPushButton("Add")
        add_btn.setStyleSheet("""
            QPushButton { background-color: #007acc; color: white; border: none; padding: 6px; }
            QPushButton:hover { background-color: #0098ff; }
        """)
        btn_layout.addWidget(add_btn)
        side_layout.addWidget(btn_container)

        # List
        self.token_list = QListWidget()
        self.token_list.setStyleSheet("""
            QListWidget { border: none; background: transparent; color: #CCCCCC; outline: none; }
            QListWidget::item { padding: 5px; }
            QListWidget::item:selected { background-color: #37373d; }
        """)
        self.token_list.addItems(["Identifier", "Symbol"])
        side_layout.addWidget(self.token_list)

        # --- C. Editor Area (Tabs) ---
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.setStyleSheet("""
            QTabWidget::pane { border: none; background: #1e1e1e; }
            QTabBar::tab { background: #2d2d2d; color: #969696; padding: 8px 15px; border-right: 1px solid #252526; }
            QTabBar::tab:selected { background: #1e1e1e; color: #ffffff; border-top: 1px solid #007acc; }
            QTabBar::tab:!selected:hover { color: #cccccc; }
        """)
        
        # Tab 1: Tokens Content
        tokens_widget = QWidget()
        tokens_layout = QHBoxLayout(tokens_widget)
        tokens_layout.setContentsMargins(0, 0, 0, 0)
        tokens_layout.setSpacing(0)

        # Splitter (Left: Def, Right: Test)
        main_splitter = QSplitter(Qt.Horizontal)
        main_splitter.setHandleWidth(1)
        main_splitter.setStyleSheet("QSplitter::handle { background-color: #3e3e42; }")

        # 1. Token Definition Editor
        self.def_edit = QPlainTextEdit()
        self.def_edit.setFrameShape(QFrame.NoFrame)
        self.def_edit.setFont(QFont("Ubuntu Mono", 12))
        self.def_edit.setStyleSheet("background-color: #1e1e1e; color: #d4d4d4;")
        self.def_edit.setPlainText('Identifier {\n    Special [\n        If r"if" ,\n        Else r"else"\n    ]\n    Normal r"[a-zA-Z_][a-zA-Z_0-9]*"\n}\nSymbol {\n    Special [\n        LeftParen r"\\(" ,\n        RightParen r"\\)"\n    ]\n}')
        self.hl_def = TokenDescHighlighter(self.def_edit.document())
        
        # 2. Right Side (Splitter Vertical)
        right_splitter = QSplitter(Qt.Vertical)
        right_splitter.setHandleWidth(1)

        # Top Right: Test Input
        self.test_edit = QPlainTextEdit()
        self.test_edit.setFrameShape(QFrame.NoFrame)
        self.test_edit.setFont(QFont("Consolas", 12))
        self.test_edit.setStyleSheet("background-color: #1e1e1e; color: #d4d4d4;")
        self.test_edit.setPlainText('if (condition){\n    this();\n} else {\n    that();\n}')
        
        self.hl_test = self.hl_gen()(self.test_edit.document())
        
        # Bottom Right: Info Panel
        info_widget = QWidget()
        info_widget.setStyleSheet("background-color: #252526;")
        info_layout = QVBoxLayout(info_widget)
        info_layout.setContentsMargins(0, 0, 0, 0)
        
        # Info Header
        info_header = QLabel("Selected Token")
        info_header.setStyleSheet("background-color: #333333; color: #CCCCCC; padding: 5px; font-size: 11px;")
        info_layout.addWidget(info_header)
        
        # Info Content
        info_content = QLabel("if (cond...\n\nIdentifier[If] (Special)")
        info_content.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        info_content.setStyleSheet("color: #d4d4d4; padding: 10px; font-family: Consolas; font-size: 12px;")
        info_layout.addWidget(info_content)
        
        right_splitter.addWidget(self.test_edit)
        right_splitter.addWidget(info_widget)
        right_splitter.setSizes([400, 200])

        main_splitter.addWidget(self.def_edit)
        main_splitter.addWidget(right_splitter)
        main_splitter.setSizes([500, 400])

        tokens_layout.addWidget(main_splitter)
        
        # Tab 2: Parsing Content (Empty placeholder)
        parsing_widget = QWidget()
        
        self.tabs.addTab(tokens_widget, "Tokens")
        self.tabs.addTab(parsing_widget, "Parsing")

        # Assemble Final Layout
        main_layout.addWidget(activity_bar)
        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.tabs)
    def hl_gen(self) -> QSyntaxHighlighter:
        return metaclass_LexerTextHighlighter(self.def_edit.document().toPlainText())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = IDEWindow()
    window.show()
    sys.exit(app.exec())