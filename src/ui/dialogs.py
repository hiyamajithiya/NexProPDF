"""
Dialog windows for NexPro PDF
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QPushButton, QComboBox,
    QSpinBox, QDoubleSpinBox, QCheckBox, QTextEdit,
    QFileDialog, QMessageBox, QGroupBox, QRadioButton,
    QButtonGroup, QListWidget, QDialogButtonBox
)
from PyQt6.QtCore import Qt
from typing import Optional, Dict, List


class PasswordDialog(QDialog):
    """Dialog for setting PDF password"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Set Password Protection")
        self.setModal(True)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        # User password
        user_group = QGroupBox("User Password (Open Document)")
        user_layout = QFormLayout()
        self.user_password = QLineEdit()
        self.user_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.user_password_confirm = QLineEdit()
        self.user_password_confirm.setEchoMode(QLineEdit.EchoMode.Password)
        user_layout.addRow("Password:", self.user_password)
        user_layout.addRow("Confirm:", self.user_password_confirm)
        user_group.setLayout(user_layout)
        layout.addWidget(user_group)

        # Owner password
        owner_group = QGroupBox("Owner Password (Edit Permissions)")
        owner_layout = QFormLayout()
        self.owner_password = QLineEdit()
        self.owner_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.owner_password_confirm = QLineEdit()
        self.owner_password_confirm.setEchoMode(QLineEdit.EchoMode.Password)
        owner_layout.addRow("Password:", self.owner_password)
        owner_layout.addRow("Confirm:", self.owner_password_confirm)
        owner_group.setLayout(owner_layout)
        layout.addWidget(owner_group)

        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.validate_and_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def validate_and_accept(self):
        """Validate passwords match"""
        if self.user_password.text() != self.user_password_confirm.text():
            QMessageBox.warning(self, "Error", "User passwords do not match")
            return

        if self.owner_password.text() != self.owner_password_confirm.text():
            QMessageBox.warning(self, "Error", "Owner passwords do not match")
            return

        self.accept()

    def get_passwords(self) -> Dict[str, str]:
        """Get entered passwords"""
        return {
            'user_password': self.user_password.text(),
            'owner_password': self.owner_password.text()
        }


class PermissionsDialog(QDialog):
    """Dialog for setting PDF permissions"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Set Document Permissions")
        self.setModal(True)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        # Permissions
        perm_group = QGroupBox("Allowed Actions")
        perm_layout = QVBoxLayout()

        self.allow_print = QCheckBox("Allow Printing")
        self.allow_print.setChecked(True)
        self.allow_copy = QCheckBox("Allow Content Copying")
        self.allow_copy.setChecked(True)
        self.allow_modify = QCheckBox("Allow Document Modification")
        self.allow_modify.setChecked(True)
        self.allow_annotate = QCheckBox("Allow Annotations")
        self.allow_annotate.setChecked(True)

        perm_layout.addWidget(self.allow_print)
        perm_layout.addWidget(self.allow_copy)
        perm_layout.addWidget(self.allow_modify)
        perm_layout.addWidget(self.allow_annotate)

        perm_group.setLayout(perm_layout)
        layout.addWidget(perm_group)

        # Owner password
        pwd_layout = QFormLayout()
        self.owner_password = QLineEdit()
        self.owner_password.setEchoMode(QLineEdit.EchoMode.Password)
        pwd_layout.addRow("Owner Password:", self.owner_password)
        layout.addLayout(pwd_layout)

        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_permissions(self) -> Dict:
        """Get selected permissions"""
        return {
            'print': self.allow_print.isChecked(),
            'copy': self.allow_copy.isChecked(),
            'modify': self.allow_modify.isChecked(),
            'annotate': self.allow_annotate.isChecked(),
            'owner_password': self.owner_password.text()
        }


class EncryptDialog(QDialog):
    """Dialog for encrypting PDF with passwords and permission control"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Encrypt PDF")
        self.setModal(True)
        self.setMinimumWidth(450)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        # User password
        user_group = QGroupBox("User Password (Required to Open)")
        user_layout = QFormLayout()
        self.user_password = QLineEdit()
        self.user_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.user_password_confirm = QLineEdit()
        self.user_password_confirm.setEchoMode(QLineEdit.EchoMode.Password)
        user_layout.addRow("Password:", self.user_password)
        user_layout.addRow("Confirm:", self.user_password_confirm)
        user_group.setLayout(user_layout)
        layout.addWidget(user_group)

        # Owner password
        owner_group = QGroupBox("Owner Password (Controls Permissions)")
        owner_layout = QFormLayout()
        self.owner_password = QLineEdit()
        self.owner_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.owner_password_confirm = QLineEdit()
        self.owner_password_confirm.setEchoMode(QLineEdit.EchoMode.Password)
        owner_layout.addRow("Password:", self.owner_password)
        owner_layout.addRow("Confirm:", self.owner_password_confirm)
        owner_note = QLabel("Required to restrict permissions. Must differ from user password.")
        owner_note.setStyleSheet("color: #888; font-size: 11px; padding: 2px 0px;")
        owner_note.setWordWrap(True)
        owner_layout.addRow(owner_note)
        owner_group.setLayout(owner_layout)
        layout.addWidget(owner_group)

        # Permissions
        perm_group = QGroupBox("Document Permissions (uncheck to restrict)")
        perm_layout = QVBoxLayout()

        self.allow_print = QCheckBox("Allow Printing")
        self.allow_print.setChecked(True)
        self.allow_copy = QCheckBox("Allow Content Copying")
        self.allow_copy.setChecked(True)
        self.allow_modify = QCheckBox("Allow Document Modification")
        self.allow_modify.setChecked(True)
        self.allow_annotate = QCheckBox("Allow Annotations")
        self.allow_annotate.setChecked(True)

        perm_layout.addWidget(self.allow_print)
        perm_layout.addWidget(self.allow_copy)
        perm_layout.addWidget(self.allow_modify)
        perm_layout.addWidget(self.allow_annotate)

        perm_group.setLayout(perm_layout)
        layout.addWidget(perm_group)

        # Encryption info
        info = QLabel("Encryption: AES-256")
        info.setStyleSheet("color: #666; font-style: italic; padding: 5px;")
        layout.addWidget(info)

        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.validate_and_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _has_restricted_permissions(self):
        """Check if any permission checkbox is unchecked"""
        return not (self.allow_print.isChecked() and
                    self.allow_copy.isChecked() and
                    self.allow_modify.isChecked() and
                    self.allow_annotate.isChecked())

    def validate_and_accept(self):
        """Validate passwords match and owner password is set for restrictions"""
        if not self.user_password.text():
            QMessageBox.warning(self, "Error", "Please enter a user password")
            return

        if self.user_password.text() != self.user_password_confirm.text():
            QMessageBox.warning(self, "Error", "User passwords do not match")
            return

        if self.owner_password.text() and self.owner_password.text() != self.owner_password_confirm.text():
            QMessageBox.warning(self, "Error", "Owner passwords do not match")
            return

        # If permissions are restricted, owner password is required and must differ
        if self._has_restricted_permissions():
            if not self.owner_password.text():
                QMessageBox.warning(
                    self, "Owner Password Required",
                    "You have restricted document permissions.\n\n"
                    "An owner password is required for permission restrictions "
                    "to be enforced. Please set an owner password different "
                    "from the user password."
                )
                self.owner_password.setFocus()
                return

            if self.owner_password.text() == self.user_password.text():
                QMessageBox.warning(
                    self, "Passwords Must Differ",
                    "The owner password must be different from the user password.\n\n"
                    "If both passwords are the same, PDF readers will grant full "
                    "access and permission restrictions will not be enforced."
                )
                self.owner_password.setFocus()
                return

        self.accept()

    def get_settings(self) -> Dict:
        """Get encrypt settings"""
        import secrets
        owner_pw = self.owner_password.text()
        if not owner_pw:
            # Generate a random owner password so it differs from user password
            owner_pw = secrets.token_hex(16)
        return {
            'user_password': self.user_password.text(),
            'owner_password': owner_pw,
            'permissions': {
                'print': self.allow_print.isChecked(),
                'copy': self.allow_copy.isChecked(),
                'modify': self.allow_modify.isChecked(),
                'annotate': self.allow_annotate.isChecked()
            }
        }


class WatermarkDialog(QDialog):
    """Dialog for adding watermark"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Watermark")
        self.setModal(True)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        # Watermark type
        type_group = QGroupBox("Watermark Type")
        type_layout = QVBoxLayout()
        self.type_group = QButtonGroup()

        self.text_radio = QRadioButton("Text Watermark")
        self.text_radio.setChecked(True)
        self.image_radio = QRadioButton("Image Watermark")

        self.type_group.addButton(self.text_radio, 0)
        self.type_group.addButton(self.image_radio, 1)

        type_layout.addWidget(self.text_radio)
        type_layout.addWidget(self.image_radio)
        type_group.setLayout(type_layout)
        layout.addWidget(type_group)

        # Text watermark options
        self.text_group = QGroupBox("Text Options")
        text_layout = QFormLayout()

        self.watermark_text = QLineEdit("CONFIDENTIAL")
        self.font_size = QSpinBox()
        self.font_size.setRange(10, 100)
        self.font_size.setValue(50)

        self.opacity = QDoubleSpinBox()
        self.opacity.setRange(0.0, 1.0)
        self.opacity.setSingleStep(0.1)
        self.opacity.setValue(0.3)

        self.rotation = QSpinBox()
        self.rotation.setRange(0, 360)
        self.rotation.setValue(45)

        text_layout.addRow("Text:", self.watermark_text)
        text_layout.addRow("Font Size:", self.font_size)
        text_layout.addRow("Opacity:", self.opacity)
        text_layout.addRow("Rotation:", self.rotation)

        self.text_group.setLayout(text_layout)
        layout.addWidget(self.text_group)

        # Image watermark options
        self.image_group = QGroupBox("Image Options")
        image_layout = QFormLayout()

        self.image_path = QLineEdit()
        self.image_browse = QPushButton("Browse...")
        self.image_browse.clicked.connect(self.browse_image)

        self.image_opacity = QDoubleSpinBox()
        self.image_opacity.setRange(0.0, 1.0)
        self.image_opacity.setSingleStep(0.1)
        self.image_opacity.setValue(0.3)

        self.image_position = QComboBox()
        self.image_position.addItems(["Center", "Top Left", "Top Right",
                                      "Bottom Left", "Bottom Right"])

        image_layout.addRow("Image:", self.image_path)
        image_layout.addRow("", self.image_browse)
        image_layout.addRow("Opacity:", self.image_opacity)
        image_layout.addRow("Position:", self.image_position)

        self.image_group.setLayout(image_layout)
        self.image_group.setEnabled(False)
        layout.addWidget(self.image_group)

        # Connect radio buttons
        self.text_radio.toggled.connect(self.on_type_changed)

        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def on_type_changed(self, checked):
        """Handle watermark type change"""
        self.text_group.setEnabled(checked)
        self.image_group.setEnabled(not checked)

    def browse_image(self):
        """Browse for watermark image"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Watermark Image",
            "",
            "Images (*.png *.jpg *.jpeg)"
        )
        if file_path:
            self.image_path.setText(file_path)

    def get_watermark_settings(self) -> Dict:
        """Get watermark settings"""
        is_text = self.text_radio.isChecked()

        if is_text:
            return {
                'type': 'text',
                'text': self.watermark_text.text(),
                'font_size': self.font_size.value(),
                'opacity': self.opacity.value(),
                'rotation': self.rotation.value()
            }
        else:
            return {
                'type': 'image',
                'image_path': self.image_path.text(),
                'opacity': self.image_opacity.value(),
                'position': self.image_position.currentText().lower().replace(' ', '')
            }


class MergeDialog(QDialog):
    """Dialog for merging PDFs"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Merge PDFs")
        self.setModal(True)
        self.setMinimumWidth(500)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        # File list
        list_label = QLabel("Select PDF files to merge (in order):")
        layout.addWidget(list_label)

        self.file_list = QListWidget()
        layout.addWidget(self.file_list)

        # Buttons for managing list
        btn_layout = QHBoxLayout()

        add_btn = QPushButton("Add Files...")
        add_btn.clicked.connect(self.add_files)
        btn_layout.addWidget(add_btn)

        remove_btn = QPushButton("Remove Selected")
        remove_btn.clicked.connect(self.remove_selected)
        btn_layout.addWidget(remove_btn)

        move_up_btn = QPushButton("Move Up")
        move_up_btn.clicked.connect(self.move_up)
        btn_layout.addWidget(move_up_btn)

        move_down_btn = QPushButton("Move Down")
        move_down_btn.clicked.connect(self.move_down)
        btn_layout.addWidget(move_down_btn)

        layout.addLayout(btn_layout)

        # Output file
        output_layout = QHBoxLayout()
        output_layout.addWidget(QLabel("Output:"))
        self.output_path = QLineEdit()
        output_layout.addWidget(self.output_path)

        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self.browse_output)
        output_layout.addWidget(browse_btn)

        layout.addLayout(output_layout)

        # Dialog buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.validate_and_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def add_files(self):
        """Add PDF files to merge"""
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select PDF Files",
            "",
            "PDF Files (*.pdf)"
        )
        for file in files:
            self.file_list.addItem(file)

    def remove_selected(self):
        """Remove selected files"""
        for item in self.file_list.selectedItems():
            self.file_list.takeItem(self.file_list.row(item))

    def move_up(self):
        """Move selected item up"""
        row = self.file_list.currentRow()
        if row > 0:
            item = self.file_list.takeItem(row)
            self.file_list.insertItem(row - 1, item)
            self.file_list.setCurrentRow(row - 1)

    def move_down(self):
        """Move selected item down"""
        row = self.file_list.currentRow()
        if row < self.file_list.count() - 1:
            item = self.file_list.takeItem(row)
            self.file_list.insertItem(row + 1, item)
            self.file_list.setCurrentRow(row + 1)

    def browse_output(self):
        """Browse for output file"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Merged PDF",
            "",
            "PDF Files (*.pdf)"
        )
        if file_path:
            self.output_path.setText(file_path)

    def validate_and_accept(self):
        """Validate inputs"""
        if self.file_list.count() < 2:
            QMessageBox.warning(self, "Error", "Please add at least 2 PDF files")
            return

        if not self.output_path.text():
            QMessageBox.warning(self, "Error", "Please specify output file")
            return

        self.accept()

    def get_files(self) -> List[str]:
        """Get list of files to merge"""
        return [self.file_list.item(i).text()
                for i in range(self.file_list.count())]

    def get_output_file(self) -> str:
        """Get output file path"""
        return self.output_path.text()


class BatesNumberingDialog(QDialog):
    """Dialog for Bates numbering"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Bates Numbering")
        self.setModal(True)
        self._setup_ui()

    def _setup_ui(self):
        layout = QFormLayout(self)

        # Prefix
        self.prefix = QLineEdit("DOC")
        layout.addRow("Prefix:", self.prefix)

        # Starting number
        self.start_number = QSpinBox()
        self.start_number.setRange(1, 999999)
        self.start_number.setValue(1)
        layout.addRow("Starting Number:", self.start_number)

        # Digits
        self.digits = QSpinBox()
        self.digits.setRange(3, 10)
        self.digits.setValue(6)
        layout.addRow("Number of Digits:", self.digits)

        # Suffix
        self.suffix = QLineEdit("")
        layout.addRow("Suffix:", self.suffix)

        # Position
        self.position = QComboBox()
        self.position.addItems(["Bottom Right", "Bottom Left",
                               "Top Right", "Top Left"])
        layout.addRow("Position:", self.position)

        # Font size
        self.font_size = QSpinBox()
        self.font_size.setRange(8, 24)
        self.font_size.setValue(10)
        layout.addRow("Font Size:", self.font_size)

        # Preview
        self.preview = QLabel()
        self.update_preview()
        layout.addRow("Preview:", self.preview)

        # Connect signals for live preview
        self.prefix.textChanged.connect(self.update_preview)
        self.start_number.valueChanged.connect(self.update_preview)
        self.digits.valueChanged.connect(self.update_preview)
        self.suffix.textChanged.connect(self.update_preview)

        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def update_preview(self):
        """Update Bates number preview"""
        prefix = self.prefix.text()
        number = str(self.start_number.value()).zfill(self.digits.value())
        suffix = self.suffix.text()
        preview = f"{prefix}{number}{suffix}"
        self.preview.setText(f"<b>{preview}</b>")

    def get_settings(self) -> Dict:
        """Get Bates numbering settings"""
        return {
            'prefix': self.prefix.text(),
            'start_number': self.start_number.value(),
            'digits': self.digits.value(),
            'suffix': self.suffix.text(),
            'position': self.position.currentText().lower().replace(' ', '_'),
            'font_size': self.font_size.value()
        }


class CreateFormFieldDialog(QDialog):
    """Dialog for creating form fields"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create Form Field")
        self.setModal(True)
        self.setMinimumWidth(400)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        # Field type
        type_layout = QFormLayout()
        self.field_type = QComboBox()
        self.field_type.addItems(["Text Field", "Checkbox", "Radio Button", "Dropdown List"])
        self.field_type.currentTextChanged.connect(self._on_type_changed)
        type_layout.addRow("Field Type:", self.field_type)
        layout.addLayout(type_layout)

        # Common properties
        common_group = QGroupBox("Field Properties")
        common_layout = QFormLayout()

        self.field_name = QLineEdit()
        common_layout.addRow("Field Name:", self.field_name)

        self.field_value = QLineEdit()
        common_layout.addRow("Default Value:", self.field_value)

        self.field_required = QCheckBox("Required field")
        common_layout.addRow("", self.field_required)

        self.field_readonly = QCheckBox("Read-only")
        common_layout.addRow("", self.field_readonly)

        common_group.setLayout(common_layout)
        layout.addWidget(common_group)

        # Position group
        position_group = QGroupBox("Position on Page")
        position_layout = QFormLayout()

        self.page_number = QSpinBox()
        self.page_number.setRange(1, 9999)
        self.page_number.setValue(1)
        position_layout.addRow("Page Number:", self.page_number)

        self.x_pos = QSpinBox()
        self.x_pos.setRange(0, 1000)
        self.x_pos.setValue(100)
        self.x_pos.setSuffix(" pt")
        position_layout.addRow("X Position:", self.x_pos)

        self.y_pos = QSpinBox()
        self.y_pos.setRange(0, 1000)
        self.y_pos.setValue(100)
        self.y_pos.setSuffix(" pt")
        position_layout.addRow("Y Position:", self.y_pos)

        self.width = QSpinBox()
        self.width.setRange(50, 500)
        self.width.setValue(200)
        self.width.setSuffix(" pt")
        position_layout.addRow("Width:", self.width)

        self.height = QSpinBox()
        self.height.setRange(10, 200)
        self.height.setValue(30)
        self.height.setSuffix(" pt")
        position_layout.addRow("Height:", self.height)

        position_group.setLayout(position_layout)
        layout.addWidget(position_group)

        # Dropdown-specific options
        self.dropdown_group = QGroupBox("Dropdown Options")
        dropdown_layout = QVBoxLayout()

        self.options_list = QListWidget()
        dropdown_layout.addWidget(QLabel("Options (one per line):"))
        dropdown_layout.addWidget(self.options_list)

        option_buttons = QHBoxLayout()
        add_btn = QPushButton("Add Option")
        add_btn.clicked.connect(self._add_option)
        remove_btn = QPushButton("Remove Selected")
        remove_btn.clicked.connect(self._remove_option)
        option_buttons.addWidget(add_btn)
        option_buttons.addWidget(remove_btn)
        dropdown_layout.addLayout(option_buttons)

        self.dropdown_group.setLayout(dropdown_layout)
        self.dropdown_group.setVisible(False)
        layout.addWidget(self.dropdown_group)

        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.validate_and_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _on_type_changed(self, field_type):
        """Update UI based on field type"""
        self.dropdown_group.setVisible(field_type == "Dropdown List")

    def _add_option(self):
        """Add option to dropdown list"""
        from PyQt6.QtWidgets import QInputDialog
        text, ok = QInputDialog.getText(self, "Add Option", "Option text:")
        if ok and text:
            self.options_list.addItem(text)

    def _remove_option(self):
        """Remove selected option"""
        current = self.options_list.currentRow()
        if current >= 0:
            self.options_list.takeItem(current)

    def validate_and_accept(self):
        """Validate inputs"""
        if not self.field_name.text():
            QMessageBox.warning(self, "Error", "Please enter a field name")
            return

        if self.field_type.currentText() == "Dropdown List" and self.options_list.count() == 0:
            QMessageBox.warning(self, "Error", "Please add at least one option for dropdown")
            return

        self.accept()

    def get_settings(self) -> Dict:
        """Get form field settings"""
        settings = {
            'type': self.field_type.currentText(),
            'name': self.field_name.text(),
            'value': self.field_value.text(),
            'required': self.field_required.isChecked(),
            'readonly': self.field_readonly.isChecked(),
            'page': self.page_number.value(),
            'x': self.x_pos.value(),
            'y': self.y_pos.value(),
            'width': self.width.value(),
            'height': self.height.value()
        }

        if self.field_type.currentText() == "Dropdown List":
            settings['options'] = [self.options_list.item(i).text()
                                  for i in range(self.options_list.count())]

        return settings


class BookmarkDialog(QDialog):
    """Dialog for managing bookmarks"""

    def __init__(self, parent=None, current_bookmarks=None):
        super().__init__(parent)
        self.setWindowTitle("Manage Bookmarks")
        self.setModal(True)
        self.setMinimumSize(500, 400)
        self.current_bookmarks = current_bookmarks or []
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        # Bookmarks list
        list_group = QGroupBox("Existing Bookmarks")
        list_layout = QVBoxLayout()

        self.bookmarks_list = QListWidget()
        for bookmark in self.current_bookmarks:
            self.bookmarks_list.addItem(f"{bookmark.get('title', 'Untitled')} (Page {bookmark.get('page', 0) + 1})")
        list_layout.addWidget(self.bookmarks_list)

        list_group.setLayout(list_layout)
        layout.addWidget(list_group)

        # Add new bookmark
        add_group = QGroupBox("Add New Bookmark")
        add_layout = QFormLayout()

        self.bookmark_title = QLineEdit()
        add_layout.addRow("Title:", self.bookmark_title)

        self.bookmark_page = QSpinBox()
        self.bookmark_page.setRange(1, 9999)
        self.bookmark_page.setValue(1)
        add_layout.addRow("Page Number:", self.bookmark_page)

        add_btn = QPushButton("Add Bookmark")
        add_btn.clicked.connect(self._add_bookmark)
        add_layout.addRow("", add_btn)

        add_group.setLayout(add_layout)
        layout.addWidget(add_group)

        # Action buttons
        action_layout = QHBoxLayout()
        delete_btn = QPushButton("Delete Selected")
        delete_btn.clicked.connect(self._delete_bookmark)
        action_layout.addWidget(delete_btn)
        action_layout.addStretch()
        layout.addLayout(action_layout)

        # Dialog buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _add_bookmark(self):
        """Add new bookmark to list"""
        title = self.bookmark_title.text()
        page = self.bookmark_page.value()

        if not title:
            QMessageBox.warning(self, "Error", "Please enter a bookmark title")
            return

        self.bookmarks_list.addItem(f"{title} (Page {page})")
        self.bookmark_title.clear()

    def _delete_bookmark(self):
        """Delete selected bookmark"""
        current = self.bookmarks_list.currentRow()
        if current >= 0:
            self.bookmarks_list.takeItem(current)

    def get_bookmarks(self) -> List[Dict]:
        """Get list of bookmarks"""
        bookmarks = []
        for i in range(self.bookmarks_list.count()):
            text = self.bookmarks_list.item(i).text()
            # Parse "Title (Page N)"
            if " (Page " in text:
                title = text.split(" (Page ")[0]
                page_str = text.split(" (Page ")[1].rstrip(")")
                page = int(page_str) - 1  # 0-indexed
                bookmarks.append({'title': title, 'page': page})
        return bookmarks


class MetadataDialog(QDialog):
    """Dialog for editing PDF metadata"""

    def __init__(self, parent=None, current_metadata=None):
        super().__init__(parent)
        self.setWindowTitle("Edit PDF Metadata")
        self.setModal(True)
        self.setMinimumWidth(500)
        self.current_metadata = current_metadata or {}
        self._setup_ui()

    def _setup_ui(self):
        layout = QFormLayout(self)

        # Title
        self.title = QLineEdit()
        self.title.setText(self.current_metadata.get('title', ''))
        layout.addRow("Title:", self.title)

        # Author
        self.author = QLineEdit()
        self.author.setText(self.current_metadata.get('author', ''))
        layout.addRow("Author:", self.author)

        # Subject
        self.subject = QLineEdit()
        self.subject.setText(self.current_metadata.get('subject', ''))
        layout.addRow("Subject:", self.subject)

        # Keywords
        self.keywords = QLineEdit()
        self.keywords.setText(self.current_metadata.get('keywords', ''))
        self.keywords.setPlaceholderText("Comma-separated keywords")
        layout.addRow("Keywords:", self.keywords)

        # Creator
        self.creator = QLineEdit()
        self.creator.setText(self.current_metadata.get('creator', ''))
        layout.addRow("Creator:", self.creator)

        # Producer
        self.producer = QLineEdit()
        self.producer.setText(self.current_metadata.get('producer', ''))
        layout.addRow("Producer:", self.producer)

        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def get_metadata(self) -> Dict:
        """Get metadata values"""
        return {
            'title': self.title.text(),
            'author': self.author.text(),
            'subject': self.subject.text(),
            'keywords': self.keywords.text(),
            'creator': self.creator.text(),
            'producer': self.producer.text()
        }


class ExtractPagesDialog(QDialog):
    """Dialog for extracting pages"""

    def __init__(self, parent=None, total_pages=0):
        super().__init__(parent)
        self.setWindowTitle("Extract Pages")
        self.setModal(True)
        self.total_pages = total_pages
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        # Info label
        info = QLabel(f"Total pages in document: {self.total_pages}")
        layout.addWidget(info)

        # Page selection
        selection_group = QGroupBox("Select Pages to Extract")
        selection_layout = QVBoxLayout()

        self.all_pages = QRadioButton("All pages")
        self.all_pages.setChecked(True)
        selection_layout.addWidget(self.all_pages)

        self.page_range = QRadioButton("Page range")
        selection_layout.addWidget(self.page_range)

        range_layout = QHBoxLayout()
        range_layout.addWidget(QLabel("From:"))
        self.from_page = QSpinBox()
        self.from_page.setRange(1, self.total_pages)
        self.from_page.setValue(1)
        self.from_page.setEnabled(False)
        range_layout.addWidget(self.from_page)

        range_layout.addWidget(QLabel("To:"))
        self.to_page = QSpinBox()
        self.to_page.setRange(1, self.total_pages)
        self.to_page.setValue(self.total_pages)
        self.to_page.setEnabled(False)
        range_layout.addWidget(self.to_page)

        selection_layout.addLayout(range_layout)

        self.specific_pages = QRadioButton("Specific pages")
        selection_layout.addWidget(self.specific_pages)

        self.pages_input = QLineEdit()
        self.pages_input.setPlaceholderText("e.g., 1,3,5-8,10")
        self.pages_input.setEnabled(False)
        selection_layout.addWidget(self.pages_input)

        selection_group.setLayout(selection_layout)
        layout.addWidget(selection_group)

        # Connect radio buttons
        self.page_range.toggled.connect(lambda checked: self.from_page.setEnabled(checked))
        self.page_range.toggled.connect(lambda checked: self.to_page.setEnabled(checked))
        self.specific_pages.toggled.connect(lambda checked: self.pages_input.setEnabled(checked))

        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.validate_and_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.output_file = None

    def validate_and_accept(self):
        """Validate inputs and ask for save location"""
        if self.specific_pages.isChecked() and not self.pages_input.text():
            QMessageBox.warning(self, "Error", "Please enter specific pages")
            return

        # Ask for save location
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Extracted Pages As",
            "",
            "PDF Files (*.pdf)"
        )
        if file_path:
            self.output_file = file_path
            self.accept()
        # If user cancels save dialog, stay in extract dialog

    def get_settings(self) -> Dict:
        """Get extraction settings"""
        if self.all_pages.isChecked():
            pages = list(range(self.total_pages))
        elif self.page_range.isChecked():
            pages = list(range(self.from_page.value() - 1, self.to_page.value()))
        else:
            # Parse specific pages
            pages = []
            for part in self.pages_input.text().split(','):
                part = part.strip()
                if '-' in part:
                    start, end = map(int, part.split('-'))
                    pages.extend(range(start - 1, end))
                else:
                    pages.append(int(part) - 1)

        return {
            'pages': pages,
            'output_file': self.output_file
        }


class AddCommentDialog(QDialog):
    """Dialog for adding comments/annotations"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Comment")
        self.setModal(True)
        self.setMinimumWidth(400)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        # Comment type
        type_layout = QFormLayout()
        self.comment_type = QComboBox()
        self.comment_type.addItems(["Sticky Note", "Text Comment"])
        type_layout.addRow("Comment Type:", self.comment_type)
        layout.addLayout(type_layout)

        # Page and position
        position_group = QGroupBox("Position")
        position_layout = QFormLayout()

        self.page_number = QSpinBox()
        self.page_number.setRange(1, 9999)
        self.page_number.setValue(1)
        position_layout.addRow("Page Number:", self.page_number)

        self.x_pos = QSpinBox()
        self.x_pos.setRange(0, 1000)
        self.x_pos.setValue(100)
        self.x_pos.setSuffix(" pt")
        position_layout.addRow("X Position:", self.x_pos)

        self.y_pos = QSpinBox()
        self.y_pos.setRange(0, 1000)
        self.y_pos.setValue(100)
        self.y_pos.setSuffix(" pt")
        position_layout.addRow("Y Position:", self.y_pos)

        position_group.setLayout(position_layout)
        layout.addWidget(position_group)

        # Comment text
        layout.addWidget(QLabel("Comment Text:"))
        self.comment_text = QTextEdit()
        self.comment_text.setMaximumHeight(150)
        layout.addWidget(self.comment_text)

        # Author
        author_layout = QFormLayout()
        self.author = QLineEdit("User")
        author_layout.addRow("Author:", self.author)
        layout.addLayout(author_layout)

        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.validate_and_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def validate_and_accept(self):
        """Validate inputs"""
        if not self.comment_text.toPlainText():
            QMessageBox.warning(self, "Error", "Please enter comment text")
            return
        self.accept()

    def get_settings(self) -> Dict:
        """Get comment settings"""
        return {
            'type': self.comment_type.currentText(),
            'page': self.page_number.value(),
            'x': self.x_pos.value(),
            'y': self.y_pos.value(),
            'text': self.comment_text.toPlainText(),
            'author': self.author.text()
        }


class FillFormDialog(QDialog):
    """Dialog for filling form fields"""

    def __init__(self, parent=None, form_fields=None):
        super().__init__(parent)
        self.setWindowTitle("Fill Form Fields")
        self.setModal(True)
        self.setMinimumSize(500, 400)
        self.form_fields = form_fields or []
        self.field_widgets = {}
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        if not self.form_fields:
            layout.addWidget(QLabel("No form fields found in this PDF"))
            buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
            buttons.accepted.connect(self.reject)
            layout.addWidget(buttons)
            return

        # Scroll area for fields
        from PyQt6.QtWidgets import QScrollArea
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QFormLayout(scroll_widget)

        for field in self.form_fields:
            field_name = field.get('name', 'Unnamed')
            field_type = field.get('type', 'text')
            field_value = field.get('value', '')

            if field_type == 'text':
                widget = QLineEdit(field_value)
                self.field_widgets[field_name] = widget
                scroll_layout.addRow(f"{field_name}:", widget)
            elif field_type == 'checkbox':
                widget = QCheckBox()
                widget.setChecked(field_value == 'Yes')
                self.field_widgets[field_name] = widget
                scroll_layout.addRow(f"{field_name}:", widget)
            elif field_type == 'dropdown':
                widget = QComboBox()
                widget.addItems(field.get('options', []))
                if field_value in field.get('options', []):
                    widget.setCurrentText(field_value)
                self.field_widgets[field_name] = widget
                scroll_layout.addRow(f"{field_name}:", widget)

        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)

        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_values(self) -> Dict:
        """Get filled form values"""
        values = {}
        for field_name, widget in self.field_widgets.items():
            if isinstance(widget, QLineEdit):
                values[field_name] = widget.text()
            elif isinstance(widget, QCheckBox):
                values[field_name] = 'Yes' if widget.isChecked() else 'No'
            elif isinstance(widget, QComboBox):
                values[field_name] = widget.currentText()
        return values


class BatchProcessDialog(QDialog):
    """Dialog for batch processing PDFs"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Batch Process PDFs")
        self.setModal(True)
        self.setMinimumSize(600, 500)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        # File list
        files_group = QGroupBox("PDF Files to Process")
        files_layout = QVBoxLayout()

        self.file_list = QListWidget()
        files_layout.addWidget(self.file_list)

        file_buttons = QHBoxLayout()
        add_files_btn = QPushButton("Add Files")
        add_files_btn.clicked.connect(self._add_files)
        remove_btn = QPushButton("Remove Selected")
        remove_btn.clicked.connect(self._remove_file)
        clear_btn = QPushButton("Clear All")
        clear_btn.clicked.connect(self.file_list.clear)

        file_buttons.addWidget(add_files_btn)
        file_buttons.addWidget(remove_btn)
        file_buttons.addWidget(clear_btn)
        file_buttons.addStretch()
        files_layout.addLayout(file_buttons)

        files_group.setLayout(files_layout)
        layout.addWidget(files_group)

        # Operation selection
        operation_group = QGroupBox("Operation to Perform")
        operation_layout = QVBoxLayout()

        self.operation = QComboBox()
        self.operation.addItems([
            "Add Watermark",
            "Compress Files",
            "Convert to PDF/A",
            "Merge All into One",
            "Add Page Numbers"
        ])
        operation_layout.addWidget(self.operation)

        operation_group.setLayout(operation_layout)
        layout.addWidget(operation_group)

        # Output directory
        output_layout = QHBoxLayout()
        output_layout.addWidget(QLabel("Output Directory:"))
        self.output_dir = QLineEdit()
        output_layout.addWidget(self.output_dir)
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self._browse_output)
        output_layout.addWidget(browse_btn)
        layout.addLayout(output_layout)

        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.validate_and_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _add_files(self):
        """Add files to process"""
        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Select PDF Files",
            "",
            "PDF Files (*.pdf)"
        )
        for file_path in file_paths:
            if file_path not in [self.file_list.item(i).text()
                                for i in range(self.file_list.count())]:
                self.file_list.addItem(file_path)

    def _remove_file(self):
        """Remove selected file"""
        current = self.file_list.currentRow()
        if current >= 0:
            self.file_list.takeItem(current)

    def _browse_output(self):
        """Browse for output directory"""
        dir_path = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if dir_path:
            self.output_dir.setText(dir_path)

    def validate_and_accept(self):
        """Validate inputs"""
        if self.file_list.count() == 0:
            QMessageBox.warning(self, "Error", "Please add at least one PDF file")
            return
        if not self.output_dir.text():
            QMessageBox.warning(self, "Error", "Please specify output directory")
            return
        self.accept()

    def get_settings(self) -> Dict:
        """Get batch processing settings"""
        return {
            'files': [self.file_list.item(i).text()
                     for i in range(self.file_list.count())],
            'operation': self.operation.currentText(),
            'output_dir': self.output_dir.text()
        }


class ConvertToWordDialog(QDialog):
    """Dialog for PDF to Word conversion options"""

    def __init__(self, parent=None, tesseract_available: bool = False,
                 available_languages: List[str] = None, detected_type: str = 'text'):
        super().__init__(parent)
        self.setWindowTitle("Convert PDF to Word")
        self.setModal(True)
        self.setMinimumWidth(450)
        self.tesseract_available = tesseract_available
        self.available_languages = available_languages or ['eng']
        self.detected_type = detected_type
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        # Info label
        info_label = QLabel(
            "Choose conversion mode for best results.\n"
            "Text Mode works best for digital PDFs.\n"
            "OCR Mode is for scanned documents (images of text)."
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #666; margin-bottom: 10px;")
        layout.addWidget(info_label)

        # Detected type info
        if self.detected_type == 'scanned':
            detected_label = QLabel("⚠️ This PDF appears to be scanned. OCR mode recommended.")
            detected_label.setStyleSheet("color: #e67e22; font-weight: bold; margin-bottom: 10px;")
        else:
            detected_label = QLabel("✓ This PDF contains extractable text.")
            detected_label.setStyleSheet("color: #27ae60; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(detected_label)

        # Conversion mode group
        mode_group = QGroupBox("Conversion Mode")
        mode_layout = QVBoxLayout()

        self.mode_group = QButtonGroup(self)

        # Auto mode
        self.auto_radio = QRadioButton("Auto-detect (Recommended)")
        self.auto_radio.setToolTip("Automatically choose the best method based on PDF content")
        self.mode_group.addButton(self.auto_radio, 0)
        mode_layout.addWidget(self.auto_radio)

        # Text extraction mode
        self.text_radio = QRadioButton("Text Extraction (for digital PDFs)")
        self.text_radio.setToolTip("Extract text directly from PDF - best for digitally created PDFs")
        self.mode_group.addButton(self.text_radio, 1)
        mode_layout.addWidget(self.text_radio)

        # OCR mode
        self.ocr_radio = QRadioButton("OCR (for scanned documents)")
        self.ocr_radio.setToolTip("Use Optical Character Recognition - best for scanned documents")
        self.mode_group.addButton(self.ocr_radio, 2)
        mode_layout.addWidget(self.ocr_radio)

        if not self.tesseract_available:
            self.ocr_radio.setEnabled(False)
            self.ocr_radio.setText("OCR (Tesseract not installed)")
            self.ocr_radio.setToolTip(
                "Tesseract OCR is not installed.\n"
                "Download from: https://github.com/UB-Mannheim/tesseract/wiki"
            )

        # Default selection based on detected type
        if self.detected_type == 'scanned' and self.tesseract_available:
            self.ocr_radio.setChecked(True)
        else:
            self.auto_radio.setChecked(True)

        mode_group.setLayout(mode_layout)
        layout.addWidget(mode_group)

        # Options group
        options_group = QGroupBox("Options")
        options_layout = QVBoxLayout()

        # Include images checkbox
        self.include_images = QCheckBox("Include images in output")
        self.include_images.setChecked(True)
        self.include_images.setToolTip("Include embedded images from the PDF in the Word document")
        options_layout.addWidget(self.include_images)

        # OCR Language selection
        lang_layout = QHBoxLayout()
        lang_label = QLabel("OCR Language:")
        self.language_combo = QComboBox()

        # Add common languages
        language_names = {
            'eng': 'English',
            'hin': 'Hindi',
            'guj': 'Gujarati',
            'mar': 'Marathi',
            'tam': 'Tamil',
            'tel': 'Telugu',
            'kan': 'Kannada',
            'mal': 'Malayalam',
            'ben': 'Bengali',
            'pan': 'Punjabi',
            'urd': 'Urdu',
            'ori': 'Odia',
            'san': 'Sanskrit',
            'deu': 'German',
            'fra': 'French',
            'spa': 'Spanish',
            'ita': 'Italian',
            'por': 'Portuguese',
            'rus': 'Russian',
            'jpn': 'Japanese',
            'chi_sim': 'Chinese (Simplified)',
            'chi_tra': 'Chinese (Traditional)',
            'kor': 'Korean',
            'ara': 'Arabic'
        }

        for lang in self.available_languages:
            display_name = language_names.get(lang, lang)
            self.language_combo.addItem(f"{display_name} ({lang})", lang)

        # Set English as default if available
        eng_index = self.language_combo.findData('eng')
        if eng_index >= 0:
            self.language_combo.setCurrentIndex(eng_index)

        lang_layout.addWidget(lang_label)
        lang_layout.addWidget(self.language_combo)
        lang_layout.addStretch()
        options_layout.addLayout(lang_layout)

        # Enable/disable language based on mode
        self.mode_group.buttonClicked.connect(self._on_mode_changed)
        self._on_mode_changed()

        options_group.setLayout(options_layout)
        layout.addWidget(options_group)

        # Tesseract install info if not available
        if not self.tesseract_available:
            install_label = QLabel(
                "💡 To enable OCR for scanned documents:\n"
                "1. Download Tesseract from github.com/UB-Mannheim/tesseract/wiki\n"
                "2. Install and add to system PATH\n"
                "3. Restart the application"
            )
            install_label.setStyleSheet(
                "background-color: #fff3cd; padding: 10px; "
                "border-radius: 5px; color: #856404;"
            )
            install_label.setWordWrap(True)
            layout.addWidget(install_label)

        # Buttons
        button_layout = QHBoxLayout()
        self.convert_btn = QPushButton("Convert")
        self.convert_btn.setDefault(True)
        self.convert_btn.clicked.connect(self.accept)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)

        button_layout.addStretch()
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(self.convert_btn)
        layout.addLayout(button_layout)

    def _on_mode_changed(self):
        """Update options based on selected mode"""
        is_ocr = self.ocr_radio.isChecked()
        self.language_combo.setEnabled(is_ocr or self.auto_radio.isChecked())
        self.include_images.setEnabled(not is_ocr)

    def get_settings(self) -> Dict:
        """Get conversion settings"""
        mode_id = self.mode_group.checkedId()
        mode_map = {0: 'auto', 1: 'text', 2: 'ocr'}

        return {
            'mode': mode_map.get(mode_id, 'auto'),
            'include_images': self.include_images.isChecked(),
            'ocr_language': self.language_combo.currentData() or 'eng'
        }
