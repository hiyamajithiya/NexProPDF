"""
License and Activation Dialog
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QTextEdit, QGroupBox, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from src.ui.modern_theme import ModernTheme


class LicenseDialog(QDialog):
    """Dialog for license information and activation"""

    def __init__(self, license_manager, parent=None):
        super().__init__(parent)
        self.license_manager = license_manager
        self.setWindowTitle("NexPro PDF - License Information")
        self.setMinimumWidth(600)
        self.setModal(True)

        self._setup_ui()
        self._load_license_info()

    def _setup_ui(self):
        """Setup dialog UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)

        # Title
        title = QLabel("NexPro PDF License Manager")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # License Status Group
        status_group = QGroupBox("License Status")
        status_layout = QVBoxLayout()

        self.status_label = QLabel()
        self.status_label.setWordWrap(True)
        self.status_label.setStyleSheet(f"font-size: 14px; padding: 10px;")
        status_layout.addWidget(self.status_label)

        status_group.setLayout(status_layout)
        layout.addWidget(status_group)

        # Activation Group
        activation_group = QGroupBox("Activate Subscription")
        activation_layout = QVBoxLayout()

        activation_info = QLabel(
            "Enter your license key to activate a subscription.\n"
            "License keys are in format: NEXPRO-XXXXX-XXXXX-XXXXX-XXXXX"
        )
        activation_info.setWordWrap(True)
        activation_info.setStyleSheet("color: #666; padding: 5px;")
        activation_layout.addWidget(activation_info)

        # License key input
        key_layout = QHBoxLayout()
        self.license_key_input = QLineEdit()
        self.license_key_input.setPlaceholderText("Enter license key...")
        self.license_key_input.setStyleSheet(f"""
            QLineEdit {{
                padding: 10px;
                font-size: 13px;
                border: 2px solid {ModernTheme.BORDER};
                border-radius: 6px;
            }}
            QLineEdit:focus {{
                border-color: {ModernTheme.PRIMARY};
            }}
        """)
        key_layout.addWidget(self.license_key_input)

        activate_btn = QPushButton("Activate")
        activate_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {ModernTheme.SUCCESS};
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                min-width: 100px;
            }}
            QPushButton:hover {{
                background-color: #4CAF50;
            }}
        """)
        activate_btn.clicked.connect(self._activate_license)
        key_layout.addWidget(activate_btn)

        activation_layout.addLayout(key_layout)
        activation_group.setLayout(activation_layout)
        layout.addWidget(activation_group)

        # Purchase Information Group
        purchase_group = QGroupBox("Purchase Subscription")
        purchase_layout = QVBoxLayout()

        contact_info = self.license_manager.get_contact_info()
        purchase_text = QLabel(
            f"<b>Contact Information:</b><br><br>"
            f"📧 Email: <a href='mailto:{contact_info['email']}'>{contact_info['email']}</a><br>"
            f"📞 Phone: {contact_info['phone']}<br>"
            f"💬 WhatsApp: {contact_info['whatsapp']}<br>"
            f"🌐 Website: {contact_info['website']}<br><br>"
            f"<i>Contact CA Himanshu Majithiya for subscription details and pricing.</i>"
        )
        purchase_text.setWordWrap(True)
        purchase_text.setOpenExternalLinks(True)
        purchase_text.setStyleSheet("padding: 10px; font-size: 13px;")
        purchase_layout.addWidget(purchase_text)

        purchase_group.setLayout(purchase_layout)
        layout.addWidget(purchase_group)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        close_btn = QPushButton("Close")
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {ModernTheme.PRIMARY};
                color: white;
                padding: 10px 30px;
                border: none;
                border-radius: 6px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {ModernTheme.PRIMARY_DARK};
            }}
        """)
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)

        layout.addLayout(button_layout)

        # Apply modern styling
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {ModernTheme.BACKGROUND};
            }}
            QGroupBox {{
                font-weight: bold;
                border: 2px solid {ModernTheme.BORDER};
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }}
        """)

    def _load_license_info(self):
        """Load and display current license information"""
        is_valid, days_remaining, message = self.license_manager.check_license_validity()

        if is_valid:
            if days_remaining <= 30:
                color = ModernTheme.WARNING
                status_icon = "⚠️"
            else:
                color = ModernTheme.SUCCESS
                status_icon = "✅"
        else:
            color = ModernTheme.ERROR
            status_icon = "❌"

        self.status_label.setText(f"<b>{status_icon} Status:</b> {message}")
        self.status_label.setStyleSheet(f"color: {color}; font-size: 14px; padding: 10px;")

    def _activate_license(self):
        """Activate license with provided key"""
        license_key = self.license_key_input.text().strip().upper()

        if not license_key:
            QMessageBox.warning(
                self,
                "No License Key",
                "Please enter a license key."
            )
            return

        # Attempt activation
        success, message = self.license_manager.activate_subscription(license_key)

        if success:
            QMessageBox.information(
                self,
                "Activation Successful",
                message
            )
            self._load_license_info()
            self.license_key_input.clear()
        else:
            QMessageBox.critical(
                self,
                "Activation Failed",
                message
            )


class TrialExpiredDialog(QDialog):
    """Dialog shown when trial expires"""

    def __init__(self, license_manager, parent=None):
        super().__init__(parent)
        self.license_manager = license_manager
        self.setWindowTitle("Trial Expired - NexPro PDF")
        self.setMinimumWidth(500)
        self.setModal(True)

        self._setup_ui()

    def _setup_ui(self):
        """Setup dialog UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)

        # Icon and Title
        title = QLabel("⏰ Your Trial Period Has Expired")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(f"color: {ModernTheme.ERROR};")
        layout.addWidget(title)

        # Message
        message = QLabel(
            "Thank you for trying NexPro PDF!\n\n"
            "Your 1-year trial period has ended. To continue using NexPro PDF, "
            "please purchase a subscription.\n\n"
            "Contact CA Himanshu Majithiya for subscription details."
        )
        message.setWordWrap(True)
        message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        message.setStyleSheet("font-size: 14px; padding: 20px;")
        layout.addWidget(message)

        # Contact Information
        contact_info = self.license_manager.get_contact_info()
        contact_label = QLabel(
            f"<b>Contact Information:</b><br><br>"
            f"📧 Email: <a href='mailto:{contact_info['email']}'>{contact_info['email']}</a><br>"
            f"📞 Phone: {contact_info['phone']}<br>"
            f"💬 WhatsApp: {contact_info['whatsapp']}"
        )
        contact_label.setWordWrap(True)
        contact_label.setOpenExternalLinks(True)
        contact_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        contact_label.setStyleSheet("font-size: 13px; padding: 20px;")
        layout.addWidget(contact_label)

        # Buttons
        button_layout = QHBoxLayout()

        activate_btn = QPushButton("Enter License Key")
        activate_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {ModernTheme.SUCCESS};
                color: white;
                padding: 12px 30px;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: #4CAF50;
            }}
        """)
        activate_btn.clicked.connect(self._show_activation)
        button_layout.addWidget(activate_btn)

        exit_btn = QPushButton("Exit")
        exit_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {ModernTheme.TEXT_SECONDARY};
                color: white;
                padding: 12px 30px;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {ModernTheme.TEXT_PRIMARY};
            }}
        """)
        exit_btn.clicked.connect(self.reject)
        button_layout.addWidget(exit_btn)

        layout.addLayout(button_layout)

        # Apply styling
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {ModernTheme.SURFACE};
            }}
        """)

    def _show_activation(self):
        """Show activation dialog"""
        dialog = LicenseDialog(self.license_manager, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Check if activated successfully
            is_valid, _, _ = self.license_manager.check_license_validity()
            if is_valid:
                self.accept()  # Close expired dialog and continue
