"""
Main application window for NexPro PDF - WITH ALL CONNECTIONS
This is the updated version with all UI components connected to backend
"""

from PyQt6.QtWidgets import QMessageBox, QMenu
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction
from src.ui.main_window import MainWindow as BaseMainWindow
from src.ui.pdf_actions import PDFActions
from src.ui.license_dialog import LicenseDialog


class ConnectedMainWindow(BaseMainWindow):
    """Main window with all UI-to-backend connections"""

    def __init__(self, config, license_manager=None):
        """Initialize main window with connections"""
        # Initialize actions controller BEFORE calling super().__init__()
        # This is needed because ribbon creation requires actions
        self.actions = None  # Will be set properly after window init
        self.license_manager = license_manager

        super().__init__(config)

        # Now properly initialize actions controller
        if not self.actions:
            self.actions = PDFActions(self)

        self.logger.info("Connected main window initialized")

    def _create_ribbon(self):
        """Override to create connected ribbon"""
        from src.ui.ribbon_connected import ConnectedRibbonBar
        # Initialize actions if not already done
        if not self.actions:
            self.actions = PDFActions(self)
        self.ribbon = ConnectedRibbonBar(self, self.actions)
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.ribbon)

    def _add_help_menu_actions(self, menu: QMenu):
        """Override to add license info menu item"""
        # Call parent to add existing menu items
        super()._add_help_menu_actions(menu)

        # Add separator before license info
        menu.addSeparator()

        # Add License Info
        if self.license_manager:
            license_action = QAction("&License Information", self)
            license_action.setStatusTip("View license and trial information")
            license_action.triggered.connect(self.show_license_info)
            menu.addAction(license_action)

    def show_license_info(self):
        """Show license information dialog"""
        if self.license_manager:
            dialog = LicenseDialog(self.license_manager, self)
            dialog.exec()
