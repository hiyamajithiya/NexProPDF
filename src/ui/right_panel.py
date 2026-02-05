"""
Right panel for NexPro PDF (Properties, Formatting, Security)
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTabWidget, QFormLayout,
    QLabel, QLineEdit, QPushButton, QGroupBox, QScrollArea,
    QTextEdit, QCheckBox
)
from PyQt6.QtCore import Qt


class RightPanel(QWidget):
    """Right sidebar panel with properties and options"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        """Setup right panel UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Create tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.TabPosition.North)

        # Properties tab
        self.properties_widget = self._create_properties_tab()
        self.tab_widget.addTab(self.properties_widget, "Properties")

        # Formatting tab
        self.formatting_widget = self._create_formatting_tab()
        self.tab_widget.addTab(self.formatting_widget, "Format")

        # Security tab
        self.security_widget = self._create_security_tab()
        self.tab_widget.addTab(self.security_widget, "Security")

        layout.addWidget(self.tab_widget)

        # Apply styling
        self.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #BDC3C7;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #ECF0F1;
                color: #2C3E50;
                padding: 8px 12px;
                border: 1px solid #BDC3C7;
                border-bottom: none;
            }
            QTabBar::tab:selected {
                background-color: white;
                font-weight: bold;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #BDC3C7;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)

    def _create_properties_tab(self) -> QWidget:
        """Create properties tab"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)

        # Document info group
        doc_group = QGroupBox("Document Information")
        doc_layout = QFormLayout()

        self.title_field = QLineEdit()
        self.author_field = QLineEdit()
        self.subject_field = QLineEdit()
        self.keywords_field = QLineEdit()

        doc_layout.addRow("Title:", self.title_field)
        doc_layout.addRow("Author:", self.author_field)
        doc_layout.addRow("Subject:", self.subject_field)
        doc_layout.addRow("Keywords:", self.keywords_field)

        doc_group.setLayout(doc_layout)
        layout.addWidget(doc_group)

        # File info group
        file_group = QGroupBox("File Information")
        file_layout = QFormLayout()

        self.file_size_label = QLabel("—")
        self.page_count_label = QLabel("—")
        self.created_label = QLabel("—")
        self.modified_label = QLabel("—")

        file_layout.addRow("File Size:", self.file_size_label)
        file_layout.addRow("Pages:", self.page_count_label)
        file_layout.addRow("Created:", self.created_label)
        file_layout.addRow("Modified:", self.modified_label)

        file_group.setLayout(file_layout)
        layout.addWidget(file_group)

        # Apply button
        apply_btn = QPushButton("Apply Changes")
        apply_btn.setStyleSheet("""
            QPushButton {
                background-color: #27AE60;
                color: white;
                font-weight: bold;
                padding: 8px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        layout.addWidget(apply_btn)

        layout.addStretch()

        scroll.setWidget(widget)
        return scroll

    def _create_formatting_tab(self) -> QWidget:
        """Create formatting tab"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)

        # Text formatting group
        text_group = QGroupBox("Text Formatting")
        text_layout = QFormLayout()

        self.font_field = QLineEdit("Arial")
        self.font_size_field = QLineEdit("12")
        self.text_color_field = QLineEdit("#000000")

        text_layout.addRow("Font:", self.font_field)
        text_layout.addRow("Size:", self.font_size_field)
        text_layout.addRow("Color:", self.text_color_field)

        text_group.setLayout(text_layout)
        layout.addWidget(text_group)

        # Page formatting group
        page_group = QGroupBox("Page Settings")
        page_layout = QFormLayout()

        self.page_width_field = QLineEdit()
        self.page_height_field = QLineEdit()
        self.orientation_field = QLineEdit("Portrait")

        page_layout.addRow("Width:", self.page_width_field)
        page_layout.addRow("Height:", self.page_height_field)
        page_layout.addRow("Orientation:", self.orientation_field)

        page_group.setLayout(page_layout)
        layout.addWidget(page_group)

        layout.addStretch()

        scroll.setWidget(widget)
        return scroll

    def _create_security_tab(self) -> QWidget:
        """Create security tab"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)

        # Security status group
        status_group = QGroupBox("Security Status")
        status_layout = QVBoxLayout()

        self.encrypted_label = QLabel("Not Encrypted")
        self.encrypted_label.setStyleSheet("color: #E74C3C; font-weight: bold;")
        status_layout.addWidget(QLabel("Encryption:"))
        status_layout.addWidget(self.encrypted_label)

        status_group.setLayout(status_layout)
        layout.addWidget(status_group)

        # Permissions group
        perms_group = QGroupBox("Permissions")
        perms_layout = QVBoxLayout()

        self.allow_print = QCheckBox("Allow Printing")
        self.allow_copy = QCheckBox("Allow Content Copying")
        self.allow_modify = QCheckBox("Allow Modifications")
        self.allow_assemble = QCheckBox("Allow Document Assembly")

        self.allow_print.setChecked(True)
        self.allow_copy.setChecked(True)
        self.allow_modify.setChecked(True)
        self.allow_assemble.setChecked(True)

        perms_layout.addWidget(self.allow_print)
        perms_layout.addWidget(self.allow_copy)
        perms_layout.addWidget(self.allow_modify)
        perms_layout.addWidget(self.allow_assemble)

        perms_group.setLayout(perms_layout)
        layout.addWidget(perms_group)

        # Security actions
        encrypt_btn = QPushButton("Encrypt Document")
        encrypt_btn.setStyleSheet("""
            QPushButton {
                background-color: #E74C3C;
                color: white;
                font-weight: bold;
                padding: 8px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #C0392B;
            }
        """)
        layout.addWidget(encrypt_btn)

        password_btn = QPushButton("Set Password")
        password_btn.setStyleSheet("""
            QPushButton {
                background-color: #F39C12;
                color: white;
                font-weight: bold;
                padding: 8px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #D68910;
            }
        """)
        layout.addWidget(password_btn)

        layout.addStretch()

        scroll.setWidget(widget)
        return scroll

    def update_properties(self, pdf_info: dict):
        """Update properties display"""
        self.title_field.setText(pdf_info.get('title', ''))
        self.author_field.setText(pdf_info.get('author', ''))
        self.subject_field.setText(pdf_info.get('subject', ''))
        self.keywords_field.setText(pdf_info.get('keywords', ''))

        self.file_size_label.setText(pdf_info.get('file_size', '—'))
        self.page_count_label.setText(str(pdf_info.get('page_count', 0)))
        self.created_label.setText(pdf_info.get('created', '—'))
        self.modified_label.setText(pdf_info.get('modified', '—'))

    def update_security_status(self, is_encrypted: bool, permissions: dict):
        """Update security status display"""
        if is_encrypted:
            self.encrypted_label.setText("Encrypted")
            self.encrypted_label.setStyleSheet("color: #27AE60; font-weight: bold;")
        else:
            self.encrypted_label.setText("Not Encrypted")
            self.encrypted_label.setStyleSheet("color: #E74C3C; font-weight: bold;")

        self.allow_print.setChecked(permissions.get('print', True))
        self.allow_copy.setChecked(permissions.get('copy', True))
        self.allow_modify.setChecked(permissions.get('modify', True))
        self.allow_assemble.setChecked(permissions.get('assemble', True))
