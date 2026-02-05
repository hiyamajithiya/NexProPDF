"""
NexPro PDF - Main Entry Point (CONNECTED VERSION)
Professional Desktop PDF Editor & Writer
This version uses the fully connected UI with all backend actions wired up
"""

import sys
import logging
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QDialog
from PyQt6.QtCore import Qt
from src.ui.main_window_connected import ConnectedMainWindow
from src.utilities.logger import setup_logger
from src.utilities.config_manager import ConfigManager
from src.security.license_manager import LicenseManager
from src.ui.license_dialog import TrialExpiredDialog
from src.version import __version__, __app_name__, __publisher__


def main():
    """Main entry point for NexPro PDF application (connected version)"""

    # Setup logging
    logger = setup_logger()
    logger.info("Starting NexPro PDF (Connected Version)...")

    try:
        # Load configuration
        config = ConfigManager()

        # Create Qt Application
        app = QApplication(sys.argv)
        app.setApplicationName(__app_name__)
        app.setApplicationVersion(__version__)
        app.setOrganizationName(__publisher__)

        # High DPI scaling is enabled by default in PyQt6

        # Initialize and check license
        license_manager = LicenseManager()
        license_manager.initialize_trial()
        is_valid, days_remaining, message = license_manager.check_license_validity()

        if not is_valid:
            # Show trial expired dialog
            dialog = TrialExpiredDialog(license_manager)
            if dialog.exec() != QDialog.DialogCode.Accepted:
                logger.info("Application closed due to expired trial")
                sys.exit(0)
            # Re-check after user interaction with activation dialog
            is_valid, _, _ = license_manager.check_license_validity()
            if not is_valid:
                logger.info("Application closed - no valid license")
                sys.exit(0)
        elif days_remaining <= 30:
            # Show warning if trial is expiring soon
            logger.warning(f"Trial period expiring in {days_remaining} days")

        # Create and show main window (CONNECTED VERSION)
        window = ConnectedMainWindow(config, license_manager)
        window.showMaximized()  # Start maximized automatically

        logger.info("NexPro PDF (Connected) started successfully")

        # Execute application
        sys.exit(app.exec())

    except Exception as e:
        logger.exception(f"Fatal error starting NexPro PDF: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
