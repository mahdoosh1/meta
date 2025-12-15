import sys, os
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,  # type: ignore
                               QHBoxLayout, QPushButton, QTabWidget, QLabel, QFrame, QTreeView,
                               QSplitter, QPlainTextEdit, QStackedWidget, QFileSystemModel)
from PySide6.QtCore import Qt, QDir # type: ignore
from PySide6.QtGui import QFont # type: ignore

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
        self.setStyleSheet("background-color: #1e1e1e; font-family: 'Ubuntu Mono', monospace;")

        # Layout Setup
        central = QWidget()
        self.setCentralWidget(central)
        self.main_layout = QHBoxLayout(central)
        self.main_layout.setSpacing(0)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        self.sidebar_stack = QStackedWidget()
        self.activity_buttons = []

        self._init_activity_bar()
        self._init_sidebar()
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

        # (F)ile, (T)okens, (G)it/Version, (D)ebug - T is index 1
        button_data = [("F", True), ("G", False), ("D", False)]
        for index, (char, active) in enumerate(button_data):
            button = ActivityButton(char, active)
            # Connect the button click to the new switching method
            button.clicked.connect(lambda checked, idx=index: self.switch_sidebar(idx))
            layout.addWidget(button)
            self.activity_buttons.append(button)

        layout.addStretch()
        self.main_layout.addWidget(bar)

    def _init_sidebar(self):
        # Main Sidebar container (QFrame, same as before)
        sidebar_frame = QFrame()
        sidebar_frame.setFixedWidth(220)
        sidebar_frame.setStyleSheet("background-color: #252526;")
        
        # The QStackedWidget holds the actual panels
        self.sidebar_stack.setStyleSheet("background-color: #252526;")

        # --- Panel 0: File Explorer (F) ---
        file_panel = QWidget()
        file_layout = QVBoxLayout(file_panel)
        file_layout.setContentsMargins(10, 5, 10, 5)
        file_layout.addWidget(QLabel("FILE EXPLORER"))
        file_tree = QTreeView(file_panel)
        model = QFileSystemModel(file_panel)
        print(model.rootPath())
        file_tree.setModel(model)
        model.setRootPath("..")
        file_layout.addWidget(file_tree)
        self.sidebar_stack.addWidget(file_panel)

        # --- Panels 1 & 2: Empty Placeholders (G, D) ---
        self.sidebar_stack.addWidget(QLabel("GIT/VERSION CONTROL"))
        self.sidebar_stack.addWidget(QLabel("DEBUG VIEW"))

        main_sidebar_layout = QVBoxLayout(sidebar_frame)
        main_sidebar_layout.addWidget(self.sidebar_stack)
        main_sidebar_layout.setContentsMargins(0, 0, 0, 0)

        self.main_layout.addWidget(sidebar_frame)
        
        # Initialize to show the "Tokens" panel (index 1)
        self.sidebar_stack.setCurrentIndex(0)

    # --- NEW METHOD TO HANDLE SWITCHING ---
    def switch_sidebar(self, index):
        """
        Updates the QStackedWidget and the visual style of the activity buttons.
        """
        # 1. Update Stacked Widget
        self.sidebar_stack.setCurrentIndex(index)

        # 2. Update Button Styles
        for i, button in enumerate(self.activity_buttons):
            is_active = (i == index)
            button.active = is_active
            button._apply_style()

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
        self.def_edit = self._create_editor("""Identifier {
    Special [
        Special r"Special" #C586C0, 
        Normal r"Normal" #C586C0,
        Token r"\\\\b[a-zA-Z_]\\\\w*\\b(?=\\\\s*\\\\{)" #DCDCAA
    ] 
    Normal r"[a-zA-Z_][a-zA-Z_0-9]*" #9CDCFE
}
Symbol {
    Special [
        LeftBrace r"\\{",
        RightBrace r"\\}",
        LeftBracket r"\\[",
        RightBracket r"\\]"
    ] #FF00FF
}
String {
    Normal r"r\\"([^\\\\\\"]|[\\\\\\\\\\\\\\s\\\\\\S])*\\"" #6A9955
}
Color {
    Normal r"#[0-9a-fA-F]{6}" #CE6021
}""".strip())
        self.test_edit = self._create_editor(r"""
if (condition){
    this();
} else {
    that();
}""".strip())

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

        try:
            # Generate new Class from current text and Instantiate
            GeneratedHighlighter = metaclass_LexerTextHighlighter(self.def_edit.toPlainText())
            if self.hl_test:
                self.hl_test.setDocument(None)
                self.hl_test.deleteLater()
                self.hl_test = None
            self.hl_test = GeneratedHighlighter(self.test_edit.document())
            
            # Force refresh
            self.test_edit.document().markContentsDirty(0, self.test_edit.document().characterCount())
        except Exception as e:
            raise e
            # Prevents crash if regex/def is temporarily invalid while typing
            print(f"Highlighter update skipped: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = IDEWindow()
    window.show()
    sys.exit(app.exec())