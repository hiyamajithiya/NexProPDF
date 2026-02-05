"""
Left panel for NexPro PDF (Thumbnails, Bookmarks, Layers, Attachments)
"""

import fitz  # PyMuPDF
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTabWidget, QListWidget,
    QListWidgetItem, QLabel, QScrollArea
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QPixmap, QIcon, QImage


class LeftPanel(QWidget):
    """Left sidebar panel with tabs"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        """Setup left panel UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Create tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.TabPosition.North)

        # Thumbnails tab
        self.thumbnails_widget = self._create_thumbnails_tab()
        self.tab_widget.addTab(self.thumbnails_widget, "Thumbnails")

        # Bookmarks tab
        self.bookmarks_widget = self._create_bookmarks_tab()
        self.tab_widget.addTab(self.bookmarks_widget, "Bookmarks")

        # Layers tab
        self.layers_widget = self._create_layers_tab()
        self.tab_widget.addTab(self.layers_widget, "Layers")

        # Attachments tab
        self.attachments_widget = self._create_attachments_tab()
        self.tab_widget.addTab(self.attachments_widget, "Attachments")

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
            QListWidget {
                border: none;
                background-color: white;
            }
        """)

    def _create_thumbnails_tab(self) -> QWidget:
        """Create thumbnails tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)

        # Thumbnails list
        self.thumbnails_list = QListWidget()
        self.thumbnails_list.setViewMode(QListWidget.ViewMode.IconMode)
        self.thumbnails_list.setIconSize(QSize(120, 150))
        self.thumbnails_list.setSpacing(10)
        self.thumbnails_list.setResizeMode(QListWidget.ResizeMode.Adjust)

        # Placeholder
        placeholder = QListWidgetItem("No pages to display")
        self.thumbnails_list.addItem(placeholder)

        layout.addWidget(self.thumbnails_list)

        return widget

    def _create_bookmarks_tab(self) -> QWidget:
        """Create bookmarks tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)

        # Bookmarks list
        self.bookmarks_list = QListWidget()

        # Placeholder
        placeholder = QListWidgetItem("No bookmarks")
        self.bookmarks_list.addItem(placeholder)

        layout.addWidget(self.bookmarks_list)

        return widget

    def _create_layers_tab(self) -> QWidget:
        """Create layers tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)

        # Layers list
        self.layers_list = QListWidget()

        # Placeholder
        placeholder = QListWidgetItem("No layers")
        self.layers_list.addItem(placeholder)

        layout.addWidget(self.layers_list)

        return widget

    def _create_attachments_tab(self) -> QWidget:
        """Create attachments tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)

        # Attachments list
        self.attachments_list = QListWidget()

        # Placeholder
        placeholder = QListWidgetItem("No attachments")
        self.attachments_list.addItem(placeholder)

        layout.addWidget(self.attachments_list)

        return widget

    def load_thumbnails(self, pdf_document):
        """Load PDF page thumbnails"""
        self.thumbnails_list.clear()

        try:
            for page_num in range(len(pdf_document)):
                page = pdf_document[page_num]

                # Render small thumbnail
                zoom = 0.2  # 20% size for thumbnail
                mat = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom))

                # Convert to QPixmap
                from PyQt6.QtGui import QImage
                img = QImage(mat.samples, mat.width, mat.height,
                           mat.stride, QImage.Format.Format_RGB888)
                pixmap = QPixmap.fromImage(img)

                # Add to list
                item = QListWidgetItem(QIcon(pixmap), f"Page {page_num + 1}")
                self.thumbnails_list.addItem(item)

        except Exception as e:
            placeholder = QListWidgetItem(f"Error loading thumbnails: {e}")
            self.thumbnails_list.addItem(placeholder)

    def load_bookmarks(self, pdf_document):
        """Load PDF bookmarks"""
        self.bookmarks_list.clear()

        try:
            toc = pdf_document.get_toc()
            if not toc:
                placeholder = QListWidgetItem("No bookmarks")
                self.bookmarks_list.addItem(placeholder)
                return

            for level, title, page_num in toc:
                indent = "  " * (level - 1)
                item = QListWidgetItem(f"{indent}{title} (Page {page_num})")
                self.bookmarks_list.addItem(item)

        except Exception as e:
            placeholder = QListWidgetItem(f"Error loading bookmarks: {e}")
            self.bookmarks_list.addItem(placeholder)
