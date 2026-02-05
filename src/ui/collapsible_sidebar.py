"""
Collapsible Sidebar - VS Code-style sidebar with icon strip
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QToolButton,
    QFrame, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QCursor, QFont, QIcon, QPixmap, QPainter, QColor
from src.ui.modern_theme import ModernTheme


def create_text_icon(text: str, size: int = 32, color: str = "#333333", bg_color: str = None) -> QIcon:
    """Create an icon with text"""
    pixmap = QPixmap(size, size)
    if bg_color:
        pixmap.fill(QColor(bg_color))
    else:
        pixmap.fill(Qt.GlobalColor.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    # Set font
    font = QFont("Arial", 14, QFont.Weight.Bold)
    painter.setFont(font)
    painter.setPen(QColor(color))

    # Draw text centered
    painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, text)
    painter.end()

    return QIcon(pixmap)


class SidebarIconButton(QToolButton):
    """Icon button for sidebar strip using QToolButton"""

    def __init__(self, icon_text: str, tooltip: str, parent=None):
        super().__init__(parent)
        self.icon_text = icon_text
        self.setToolTip(tooltip)
        self.setFixedSize(44, 44)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.setCheckable(True)

        # Set the text as button text
        self.setText(icon_text)

        # Set font
        font = QFont("Arial", 14, QFont.Weight.Bold)
        self.setFont(font)

        # Set tool button style to show text
        self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextOnly)

        self._is_active = False
        self._apply_style()

    def _apply_style(self):
        """Apply button style based on active state"""
        if self._is_active:
            self.setStyleSheet("""
                QToolButton {
                    background-color: #1E88E5;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 4px;
                }
                QToolButton:hover {
                    background-color: #1565C0;
                }
            """)
        else:
            self.setStyleSheet("""
                QToolButton {
                    background-color: #FFFFFF;
                    color: #333333;
                    border: 1px solid #CCCCCC;
                    border-radius: 6px;
                    padding: 4px;
                }
                QToolButton:hover {
                    background-color: #42A5F5;
                    color: white;
                }
            """)

    def setActive(self, active: bool):
        """Set button active state"""
        self._is_active = active
        self.setChecked(active)
        self._apply_style()


class CollapsibleSidebar(QWidget):
    """
    VS Code-style collapsible sidebar with icon strip.
    The icon strip is always visible, clicking an icon toggles the panel.
    """

    panel_toggled = pyqtSignal(bool)  # Emitted when panel is shown/hidden

    def __init__(self, panel_widget: QWidget, icons: list, position: str = "left", parent=None):
        """
        Initialize collapsible sidebar.

        Args:
            panel_widget: The actual panel content (LeftPanel or RightPanel)
            icons: List of tuples (icon_text, tooltip, tab_index)
            position: "left" or "right" - determines icon strip position
            parent: Parent widget
        """
        super().__init__(parent)
        self.panel_widget = panel_widget
        self.icons = icons
        self.position = position
        self.is_expanded = False  # Start collapsed
        self.active_tab = 0
        self.icon_buttons = []

        # Set minimum width for the sidebar
        self.setMinimumWidth(48)

        self._setup_ui()

        # Hide panel by default
        self.panel_container.hide()

    def _setup_ui(self):
        """Setup the sidebar UI"""
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Create icon strip
        self.icon_strip = QFrame()
        self.icon_strip.setFixedWidth(52)
        self.icon_strip.setStyleSheet(f"""
            QFrame {{
                background-color: {ModernTheme.BACKGROUND};
                border-right: 1px solid {ModernTheme.BORDER};
            }}
        """)

        icon_layout = QVBoxLayout(self.icon_strip)
        icon_layout.setContentsMargins(4, 8, 4, 8)
        icon_layout.setSpacing(4)

        # Add icon buttons
        for i, (icon_text, tooltip, tab_index) in enumerate(self.icons):
            btn = SidebarIconButton(icon_text, tooltip)
            btn.clicked.connect(lambda checked, idx=tab_index: self._on_icon_clicked(idx))
            self.icon_buttons.append(btn)
            icon_layout.addWidget(btn)

        icon_layout.addStretch()

        # All buttons start inactive (panel is collapsed by default)
        for btn in self.icon_buttons:
            btn.setActive(False)

        # Panel container
        self.panel_container = QFrame()
        self.panel_container.setMinimumWidth(200)
        self.panel_container.setStyleSheet(f"""
            QFrame {{
                background-color: {ModernTheme.SURFACE};
                border: none;
            }}
        """)
        panel_layout = QVBoxLayout(self.panel_container)
        panel_layout.setContentsMargins(0, 0, 0, 0)
        panel_layout.setSpacing(0)

        # Add close button header
        header_frame = QFrame()
        header_frame.setFixedHeight(28)
        header_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {ModernTheme.BACKGROUND};
                border-bottom: 1px solid {ModernTheme.BORDER};
            }}
        """)
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(8, 2, 4, 2)
        header_layout.addStretch()

        # Close button
        close_btn = QToolButton()
        close_btn.setText("X")
        close_btn.setFixedSize(24, 24)
        close_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        close_btn.setStyleSheet("""
            QToolButton {
                background-color: transparent;
                color: #666666;
                border: none;
                border-radius: 4px;
                font-weight: bold;
                font-size: 12px;
            }
            QToolButton:hover {
                background-color: #FF5252;
                color: white;
            }
        """)
        close_btn.clicked.connect(self.collapse)
        header_layout.addWidget(close_btn)

        panel_layout.addWidget(header_frame)
        panel_layout.addWidget(self.panel_widget)

        # Add widgets based on position
        if self.position == "left":
            main_layout.addWidget(self.icon_strip)
            main_layout.addWidget(self.panel_container)
            # Update border for left position
            self.icon_strip.setStyleSheet(f"""
                QFrame {{
                    background-color: #E8EAF6;
                    border-right: 2px solid {ModernTheme.PRIMARY};
                }}
            """)
        else:  # right
            main_layout.addWidget(self.panel_container)
            main_layout.addWidget(self.icon_strip)
            # Update border for right position
            self.icon_strip.setStyleSheet(f"""
                QFrame {{
                    background-color: #E8EAF6;
                    border-left: 2px solid {ModernTheme.PRIMARY};
                }}
            """)

    def _on_icon_clicked(self, tab_index: int):
        """Handle icon button click"""
        if self.is_expanded and self.active_tab == tab_index:
            # Same tab clicked while expanded - collapse
            self.collapse()
        else:
            # Different tab or was collapsed - expand and switch tab
            self.expand()
            self.active_tab = tab_index

            # Update icon button states
            for i, btn in enumerate(self.icon_buttons):
                btn.setActive(self.icons[i][2] == tab_index)

            # Switch to the selected tab in the panel
            if hasattr(self.panel_widget, 'tab_widget'):
                self.panel_widget.tab_widget.setCurrentIndex(tab_index)

    def expand(self):
        """Expand the panel"""
        if not self.is_expanded:
            self.panel_container.show()
            self.is_expanded = True
            self.panel_toggled.emit(True)

    def collapse(self):
        """Collapse the panel"""
        if self.is_expanded:
            self.panel_container.hide()
            self.is_expanded = False
            # Deactivate all buttons
            for btn in self.icon_buttons:
                btn.setActive(False)
            self.panel_toggled.emit(False)

    def toggle(self):
        """Toggle panel visibility"""
        if self.is_expanded:
            self.collapse()
        else:
            self.expand()
            # Reactivate the last active tab button
            if self.icon_buttons and self.active_tab < len(self.icon_buttons):
                for i, btn in enumerate(self.icon_buttons):
                    btn.setActive(self.icons[i][2] == self.active_tab)

    def is_panel_visible(self) -> bool:
        """Check if panel is visible"""
        return self.is_expanded
