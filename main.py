"""
NexPro PDF - Main Entry Point
Professional Desktop PDF Editor & Writer
"""

import sys
import logging
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from src.ui.main_window import MainWindow
from src.utilities.logger import setup_logger
from src.utilities.config_manager import ConfigManager


def main():
    """Main entry point for NexPro PDF application"""

    # Setup logging
    logger = setup_logger()
    logger.info("Starting NexPro PDF...")

    try:
        # Load configuration
        config = ConfigManager()

        # Create Qt Application
        app = QApplication(sys.argv)
        app.setApplicationName(config.get("app.name", "NexPro PDF"))
        app.setApplicationVersion(config.get("app.version", "1.0.0"))
        app.setOrganizationName(config.get("app.company", "NexPro Technologies"))

        # High DPI scaling is enabled by default in PyQt6

        # Create and show main window
        window = MainWindow(config)
        window.show()

        logger.info("NexPro PDF started successfully")

        # Execute application
        sys.exit(app.exec())

    except Exception as e:
        logger.exception(f"Fatal error starting NexPro PDF: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
