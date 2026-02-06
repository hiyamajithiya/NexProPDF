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
        """Override to add license info and update check menu items"""
        super()._add_help_menu_actions(menu)

        menu.addSeparator()

        # License Info
        if self.license_manager:
            license_action = QAction("&License Information", self)
            license_action.setStatusTip("View license and trial information")
            license_action.triggered.connect(self.show_license_info)
            menu.addAction(license_action)

        # Check for Updates
        update_action = QAction("Check for &Updates...", self)
        update_action.setStatusTip("Check for new version of NexPro PDF")
        update_action.triggered.connect(self.check_for_updates)
        menu.addAction(update_action)

    def show_license_info(self):
        """Show license information dialog"""
        if self.license_manager:
            dialog = LicenseDialog(self.license_manager, self)
            dialog.exec()

    def check_for_updates(self):
        """Check GitHub for a newer version and show result to user."""
        from PyQt6.QtWidgets import QProgressDialog, QApplication
        from PyQt6.QtCore import Qt as QtCore_Qt

        progress = QProgressDialog("Checking for updates...", None, 0, 0, self)
        progress.setWindowTitle("Update Check")
        progress.setWindowModality(QtCore_Qt.WindowModality.WindowModal)
        progress.setMinimumDuration(0)
        progress.setValue(0)
        QApplication.processEvents()

        from src.utilities.update_checker import UpdateChecker
        checker = UpdateChecker()
        result = checker.check_for_updates()

        progress.close()

        if result is None:
            QMessageBox.warning(
                self, "Update Check Failed",
                "Could not check for updates.\n\n"
                "Please verify your internet connection and try again."
            )
            return

        if result["available"]:
            import webbrowser
            reply = QMessageBox.information(
                self, "Update Available",
                f"A new version of NexPro PDF is available!\n\n"
                f"Current version:  v{result['current_version']}\n"
                f"Latest version:    v{result['latest_version']}\n\n"
                f"Would you like to download the update?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes,
            )
            if reply == QMessageBox.StandardButton.Yes:
                webbrowser.open(result["download_url"])
        else:
            QMessageBox.information(
                self, "Up to Date",
                f"You are running the latest version of NexPro PDF.\n\n"
                f"Current version: v{result['current_version']}"
            )

    def run_startup_update_check(self):
        """Background update check on startup — shows status bar message only."""
        from PyQt6.QtCore import QThread, pyqtSignal

        class _Worker(QThread):
            finished = pyqtSignal(object)

            def run(self):
                from src.utilities.update_checker import UpdateChecker
                self.finished.emit(UpdateChecker().check_for_updates())

        def _on_result(result):
            if result and result.get("available"):
                self.statusBar().showMessage(
                    f"Update available: v{result['latest_version']}  "
                    f"—  Help > Check for Updates",
                    15000,
                )
            self._update_worker = None  # prevent GC before signal fires

        self._update_worker = _Worker()
        self._update_worker.finished.connect(_on_result)
        self._update_worker.start()
