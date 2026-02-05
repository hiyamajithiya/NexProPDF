"""
Modern Professional Theme for NexPro PDF
"""

class ModernTheme:
    """Modern color scheme and styling"""

    # Professional Color Palette
    PRIMARY = "#1E88E5"  # Modern Blue
    PRIMARY_DARK = "#1565C0"
    PRIMARY_LIGHT = "#42A5F5"

    SECONDARY = "#26A69A"  # Teal accent
    SECONDARY_DARK = "#00897B"

    SUCCESS = "#66BB6A"  # Green
    WARNING = "#FFA726"  # Orange
    ERROR = "#EF5350"  # Red
    INFO = "#29B6F6"  # Light Blue

    BACKGROUND = "#F5F7FA"  # Light gray background
    SURFACE = "#FFFFFF"  # White surface

    TEXT_PRIMARY = "#212121"
    TEXT_SECONDARY = "#757575"
    TEXT_DISABLED = "#BDBDBD"

    BORDER = "#E0E0E0"
    BORDER_FOCUS = "#1E88E5"

    SHADOW = "rgba(0, 0, 0, 0.1)"
    SHADOW_HEAVY = "rgba(0, 0, 0, 0.2)"

    @staticmethod
    def get_main_stylesheet():
        """Get main application stylesheet"""
        return f"""
            QMainWindow {{
                background-color: {ModernTheme.BACKGROUND};
            }}

            /* Menu Bar */
            QMenuBar {{
                background-color: {ModernTheme.SURFACE};
                color: {ModernTheme.TEXT_PRIMARY};
                border-bottom: 1px solid {ModernTheme.BORDER};
                padding: 4px;
                font-size: 13px;
            }}

            QMenuBar::item {{
                background-color: transparent;
                padding: 8px 12px;
                border-radius: 4px;
            }}

            QMenuBar::item:selected {{
                background-color: {ModernTheme.PRIMARY_LIGHT};
                color: white;
            }}

            QMenuBar::item:pressed {{
                background-color: {ModernTheme.PRIMARY};
                color: white;
            }}

            /* Menus */
            QMenu {{
                background-color: {ModernTheme.SURFACE};
                border: 1px solid {ModernTheme.BORDER};
                border-radius: 6px;
                padding: 8px;
            }}

            QMenu::item {{
                padding: 8px 24px 8px 12px;
                border-radius: 4px;
                margin: 2px;
            }}

            QMenu::item:selected {{
                background-color: {ModernTheme.PRIMARY_LIGHT};
                color: white;
            }}

            /* Status Bar */
            QStatusBar {{
                background-color: {ModernTheme.SURFACE};
                color: {ModernTheme.TEXT_SECONDARY};
                border-top: 1px solid {ModernTheme.BORDER};
                padding: 4px;
                font-size: 12px;
            }}

            QStatusBar QLabel {{
                padding: 2px 8px;
            }}

            /* Buttons */
            QPushButton {{
                background-color: {ModernTheme.PRIMARY};
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-size: 13px;
                font-weight: 500;
                min-width: 80px;
            }}

            QPushButton:hover {{
                background-color: {ModernTheme.PRIMARY_DARK};
            }}

            QPushButton:pressed {{
                background-color: {ModernTheme.PRIMARY_DARK};
                padding-top: 9px;
                padding-bottom: 7px;
            }}

            QPushButton:disabled {{
                background-color: {ModernTheme.BORDER};
                color: {ModernTheme.TEXT_DISABLED};
            }}

            /* Input Fields */
            QLineEdit, QTextEdit, QSpinBox, QComboBox {{
                background-color: {ModernTheme.SURFACE};
                border: 2px solid {ModernTheme.BORDER};
                border-radius: 6px;
                padding: 8px 12px;
                color: {ModernTheme.TEXT_PRIMARY};
                font-size: 13px;
            }}

            QLineEdit:focus, QTextEdit:focus, QSpinBox:focus, QComboBox:focus {{
                border-color: {ModernTheme.BORDER_FOCUS};
            }}

            /* Dialogs */
            QDialog {{
                background-color: {ModernTheme.BACKGROUND};
            }}

            /* Labels */
            QLabel {{
                color: {ModernTheme.TEXT_PRIMARY};
                font-size: 13px;
            }}

            /* Scroll Bars */
            QScrollBar:vertical {{
                background-color: {ModernTheme.BACKGROUND};
                width: 12px;
                border-radius: 6px;
            }}

            QScrollBar::handle:vertical {{
                background-color: {ModernTheme.BORDER};
                border-radius: 6px;
                min-height: 30px;
            }}

            QScrollBar::handle:vertical:hover {{
                background-color: {ModernTheme.TEXT_DISABLED};
            }}

            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}

            QScrollBar:horizontal {{
                background-color: {ModernTheme.BACKGROUND};
                height: 12px;
                border-radius: 6px;
            }}

            QScrollBar::handle:horizontal {{
                background-color: {ModernTheme.BORDER};
                border-radius: 6px;
                min-width: 30px;
            }}

            QScrollBar::handle:horizontal:hover {{
                background-color: {ModernTheme.TEXT_DISABLED};
            }}

            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
                width: 0px;
            }}
        """

    @staticmethod
    def get_ribbon_stylesheet():
        """Get ribbon toolbar stylesheet"""
        return f"""
            QToolBar {{
                background-color: {ModernTheme.SURFACE};
                border: none;
                border-bottom: 2px solid {ModernTheme.BORDER};
                spacing: 8px;
                padding: 12px 8px;
            }}

            QToolBar QToolButton {{
                background-color: transparent;
                border: none;
                border-radius: 6px;
                padding: 10px 16px;
                color: {ModernTheme.TEXT_PRIMARY};
                font-size: 13px;
                font-weight: 500;
                min-width: 90px;
            }}

            QToolBar QToolButton:hover {{
                background-color: {ModernTheme.PRIMARY_LIGHT};
                color: white;
            }}

            QToolBar QToolButton:checked {{
                background-color: {ModernTheme.PRIMARY};
                color: white;
            }}

            QToolBar QToolButton:pressed {{
                background-color: {ModernTheme.PRIMARY_DARK};
            }}
        """

    @staticmethod
    def get_viewer_stylesheet():
        """Get PDF viewer stylesheet"""
        return f"""
            QWidget {{
                background-color: {ModernTheme.BACKGROUND};
            }}

            QLabel {{
                background-color: #E8EAF6;
                color: {ModernTheme.TEXT_SECONDARY};
                font-size: 16px;
                border-radius: 8px;
            }}

            QScrollArea {{
                border: none;
                background-color: {ModernTheme.BACKGROUND};
            }}
        """

    @staticmethod
    def get_panel_stylesheet():
        """Get side panel stylesheet"""
        return f"""
            QTabWidget::pane {{
                background-color: {ModernTheme.SURFACE};
                border: 1px solid {ModernTheme.BORDER};
                border-radius: 8px;
            }}

            QTabBar::tab {{
                background-color: {ModernTheme.BACKGROUND};
                color: {ModernTheme.TEXT_SECONDARY};
                padding: 10px 16px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                margin-right: 2px;
                font-size: 12px;
                font-weight: 500;
            }}

            QTabBar::tab:selected {{
                background-color: {ModernTheme.SURFACE};
                color: {ModernTheme.PRIMARY};
                border-bottom: 2px solid {ModernTheme.PRIMARY};
            }}

            QTabBar::tab:hover {{
                background-color: {ModernTheme.PRIMARY_LIGHT};
                color: white;
            }}
        """
