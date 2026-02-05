"""
Ribbon toolbar for NexPro PDF (MS Office style)
"""

from PyQt6.QtWidgets import (
    QToolBar, QWidget, QHBoxLayout, QVBoxLayout,
    QPushButton, QLabel, QToolButton, QButtonGroup
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QAction
from src.ui.modern_theme import ModernTheme


class RibbonBar(QToolBar):
    """Ribbon-style toolbar with tabs"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMovable(False)
        self.setFloatable(False)
        self.setIconSize(QSize(32, 32))
        self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)

        self._setup_ribbon()

    def _setup_ribbon(self):
        """Setup ribbon tabs and buttons"""
        # Create ribbon widget
        ribbon_widget = QWidget()
        ribbon_layout = QVBoxLayout(ribbon_widget)
        ribbon_layout.setContentsMargins(5, 5, 5, 5)
        ribbon_layout.setSpacing(0)

        # Tab buttons
        tab_layout = QHBoxLayout()
        tab_layout.setSpacing(2)

        self.file_tab = self._create_tab_button("File")
        self.edit_tab = self._create_tab_button("Edit")
        self.convert_tab = self._create_tab_button("Convert")
        self.pages_tab = self._create_tab_button("Pages")
        self.security_tab = self._create_tab_button("Security")
        self.redaction_tab = self._create_tab_button("Redaction")
        self.forms_tab = self._create_tab_button("Forms")
        self.signature_tab = self._create_tab_button("Signature")
        self.tools_tab = self._create_tab_button("Tools")
        self.help_tab = self._create_tab_button("Help")

        tab_layout.addWidget(self.file_tab)
        tab_layout.addWidget(self.edit_tab)
        tab_layout.addWidget(self.convert_tab)
        tab_layout.addWidget(self.pages_tab)
        tab_layout.addWidget(self.security_tab)
        tab_layout.addWidget(self.redaction_tab)
        tab_layout.addWidget(self.forms_tab)
        tab_layout.addWidget(self.signature_tab)
        tab_layout.addWidget(self.tools_tab)
        tab_layout.addWidget(self.help_tab)
        tab_layout.addStretch()

        ribbon_layout.addLayout(tab_layout)

        # Tool buttons area (initially show File tab content)
        self.tool_area = QWidget()
        self.tool_layout = QHBoxLayout(self.tool_area)
        self.tool_layout.setContentsMargins(5, 5, 5, 5)
        self._create_file_tab_tools()

        ribbon_layout.addWidget(self.tool_area)

        self.addWidget(ribbon_widget)

        # Connect tab buttons
        self.file_tab.clicked.connect(lambda: self._switch_tab("file"))
        self.edit_tab.clicked.connect(lambda: self._switch_tab("edit"))
        self.convert_tab.clicked.connect(lambda: self._switch_tab("convert"))
        self.pages_tab.clicked.connect(lambda: self._switch_tab("pages"))
        self.security_tab.clicked.connect(lambda: self._switch_tab("security"))
        self.redaction_tab.clicked.connect(lambda: self._switch_tab("redaction"))

    def _create_tab_button(self, text: str) -> QPushButton:
        """Create modern ribbon tab button"""
        btn = QPushButton(text)
        btn.setCheckable(True)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {ModernTheme.SURFACE};
                color: {ModernTheme.TEXT_SECONDARY};
                border: none;
                border-bottom: 3px solid transparent;
                padding: 10px 20px;
                font-weight: 600;
                font-size: 13px;
                min-width: 80px;
            }}
            QPushButton:checked {{
                background-color: {ModernTheme.SURFACE};
                color: {ModernTheme.PRIMARY};
                border-bottom: 3px solid {ModernTheme.PRIMARY};
            }}
            QPushButton:hover {{
                background-color: {ModernTheme.PRIMARY_LIGHT};
                color: white;
                border-bottom: 3px solid {ModernTheme.PRIMARY};
            }}
        """)
        return btn

    def _create_tool_button(self, text: str, tooltip: str = "") -> QToolButton:
        """Create modern ribbon tool button"""
        btn = QToolButton()
        btn.setText(text)
        btn.setToolTip(tooltip or text)
        btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        btn.setIconSize(QSize(20, 20))
        btn.setStyleSheet(f"""
            QToolButton {{
                background-color: transparent;
                border: 2px solid transparent;
                border-radius: 8px;
                padding: 10px 16px;
                min-width: 100px;
                color: {ModernTheme.TEXT_PRIMARY};
                font-size: 13px;
                font-weight: 500;
            }}
            QToolButton:hover {{
                background-color: {ModernTheme.PRIMARY_LIGHT};
                border: 2px solid {ModernTheme.PRIMARY};
                color: white;
            }}
            QToolButton:pressed {{
                background-color: {ModernTheme.PRIMARY_DARK};
                border: 2px solid {ModernTheme.PRIMARY_DARK};
                color: white;
            }}
        """)
        return btn

    def _clear_tool_area(self):
        """Clear tool area"""
        while self.tool_layout.count():
            item = self.tool_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _create_file_tab_tools(self):
        """Create File tab tools"""
        self._clear_tool_area()

        # New section
        new_btn = self._create_tool_button("New", "Create new PDF")
        open_btn = self._create_tool_button("Open", "Open existing PDF")
        save_btn = self._create_tool_button("Save", "Save current PDF")
        save_as_btn = self._create_tool_button("Save As", "Save PDF with new name")

        self.tool_layout.addWidget(new_btn)
        self.tool_layout.addWidget(open_btn)
        self.tool_layout.addWidget(save_btn)
        self.tool_layout.addWidget(save_as_btn)
        self.tool_layout.addWidget(self._create_separator())

        # Create section
        from_word_btn = self._create_tool_button("From Word", "Create PDF from Word document")
        from_excel_btn = self._create_tool_button("From Excel", "Create PDF from Excel spreadsheet")
        from_ppt_btn = self._create_tool_button("From PPT", "Create PDF from PowerPoint")
        from_images_btn = self._create_tool_button("From Images", "Create PDF from images")

        self.tool_layout.addWidget(from_word_btn)
        self.tool_layout.addWidget(from_excel_btn)
        self.tool_layout.addWidget(from_ppt_btn)
        self.tool_layout.addWidget(from_images_btn)

        self.tool_layout.addStretch()

    def _create_edit_tab_tools(self):
        """Create Edit tab tools"""
        self._clear_tool_area()

        edit_text_btn = self._create_tool_button("Edit Text", "Edit existing text")
        add_text_btn = self._create_tool_button("Add Text", "Add new text box")
        edit_image_btn = self._create_tool_button("Edit Image", "Edit or replace images")
        add_image_btn = self._create_tool_button("Add Image", "Insert new image")

        self.tool_layout.addWidget(edit_text_btn)
        self.tool_layout.addWidget(add_text_btn)
        self.tool_layout.addWidget(edit_image_btn)
        self.tool_layout.addWidget(add_image_btn)
        self.tool_layout.addWidget(self._create_separator())

        undo_btn = self._create_tool_button("Undo", "Undo last action")
        redo_btn = self._create_tool_button("Redo", "Redo last action")

        self.tool_layout.addWidget(undo_btn)
        self.tool_layout.addWidget(redo_btn)

        self.tool_layout.addStretch()

    def _create_pages_tab_tools(self):
        """Create Pages tab tools"""
        self._clear_tool_area()

        insert_btn = self._create_tool_button("Insert", "Insert pages")
        delete_btn = self._create_tool_button("Delete", "Delete pages")
        reorder_btn = self._create_tool_button("Reorder", "Reorder pages")
        rotate_btn = self._create_tool_button("Rotate", "Rotate pages")
        crop_btn = self._create_tool_button("Crop", "Crop pages")

        self.tool_layout.addWidget(insert_btn)
        self.tool_layout.addWidget(delete_btn)
        self.tool_layout.addWidget(reorder_btn)
        self.tool_layout.addWidget(rotate_btn)
        self.tool_layout.addWidget(crop_btn)
        self.tool_layout.addWidget(self._create_separator())

        merge_btn = self._create_tool_button("Merge", "Merge multiple PDFs")
        split_btn = self._create_tool_button("Split", "Split PDF")

        self.tool_layout.addWidget(merge_btn)
        self.tool_layout.addWidget(split_btn)

        self.tool_layout.addStretch()

    def _create_security_tab_tools(self):
        """Create Security tab tools"""
        self._clear_tool_area()

        password_btn = self._create_tool_button("Password", "Add password protection")
        encrypt_btn = self._create_tool_button("Encrypt", "Encrypt PDF with AES-256")
        permissions_btn = self._create_tool_button("Permissions", "Set document permissions")
        watermark_btn = self._create_tool_button("Watermark", "Add watermark")

        self.tool_layout.addWidget(password_btn)
        self.tool_layout.addWidget(encrypt_btn)
        self.tool_layout.addWidget(permissions_btn)
        self.tool_layout.addWidget(watermark_btn)

        self.tool_layout.addStretch()

    def _create_redaction_tab_tools(self):
        """Create Redaction tab tools"""
        self._clear_tool_area()

        manual_btn = self._create_tool_button("Manual", "Draw redaction box")
        text_btn = self._create_tool_button("Text", "Redact specific text")
        pan_btn = self._create_tool_button("PAN", "Redact PAN numbers")
        aadhaar_btn = self._create_tool_button("Aadhaar", "Redact Aadhaar numbers")
        gstin_btn = self._create_tool_button("GSTIN", "Redact GSTIN numbers")
        bank_btn = self._create_tool_button("Bank Acc", "Redact bank account numbers")

        self.tool_layout.addWidget(manual_btn)
        self.tool_layout.addWidget(text_btn)
        self.tool_layout.addWidget(self._create_separator())
        self.tool_layout.addWidget(pan_btn)
        self.tool_layout.addWidget(aadhaar_btn)
        self.tool_layout.addWidget(gstin_btn)
        self.tool_layout.addWidget(bank_btn)
        self.tool_layout.addWidget(self._create_separator())

        apply_btn = self._create_tool_button("Apply", "Apply redactions permanently")
        apply_btn.setStyleSheet(apply_btn.styleSheet() + """
            QToolButton { background-color: #E74C3C; color: white; font-weight: bold; }
            QToolButton:hover { background-color: #C0392B; }
        """)
        self.tool_layout.addWidget(apply_btn)

        self.tool_layout.addStretch()

    def _create_separator(self) -> QWidget:
        """Create vertical separator"""
        separator = QWidget()
        separator.setFixedWidth(1)
        separator.setStyleSheet("background-color: #BDC3C7;")
        return separator

    def _switch_tab(self, tab_name: str):
        """Switch ribbon tab"""
        # Uncheck all tabs
        for btn in [self.file_tab, self.edit_tab, self.pages_tab,
                    self.security_tab, self.redaction_tab, self.forms_tab,
                    self.signature_tab, self.tools_tab, self.help_tab]:
            btn.setChecked(False)

        # Load appropriate tab content
        if tab_name == "file":
            self.file_tab.setChecked(True)
            self._create_file_tab_tools()
        elif tab_name == "edit":
            self.edit_tab.setChecked(True)
            self._create_edit_tab_tools()
        elif tab_name == "pages":
            self.pages_tab.setChecked(True)
            self._create_pages_tab_tools()
        elif tab_name == "security":
            self.security_tab.setChecked(True)
            self._create_security_tab_tools()
        elif tab_name == "redaction":
            self.redaction_tab.setChecked(True)
            self._create_redaction_tab_tools()

        # Set default checked tab
        if tab_name == "file":
            self.file_tab.setChecked(True)
