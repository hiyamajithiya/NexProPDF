"""
Main application window for NexPro PDF
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QStatusBar, QToolBar, QMenuBar, QMenu,
    QTabWidget, QLabel, QMessageBox, QPushButton, QFrame
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QAction, QIcon, QKeySequence
from src.utilities.logger import get_logger
from src.ui.pdf_viewer import PDFViewer
from src.ui.left_panel import LeftPanel
from src.ui.right_panel import RightPanel
from src.ui.ribbon import RibbonBar
from src.ui.modern_theme import ModernTheme
from src.ui.collapsible_sidebar import CollapsibleSidebar


class MainWindow(QMainWindow):
    """Main application window"""

    def __init__(self, config):
        """
        Initialize main window

        Args:
            config: Configuration manager instance
        """
        super().__init__()
        self.config = config
        self.logger = get_logger()
        self.current_file = None
        self._first_show = True  # Flag to center window on first show

        # Setup UI
        self._setup_window()
        self._create_menu_bar()
        self._create_ribbon()
        self._create_main_layout()
        self._create_status_bar()
        self._apply_styling()

        self.logger.info("Main window initialized")

    def _setup_window(self):
        """Setup main window properties"""
        # Ensure standard window decorations (title bar with min/max/close buttons)
        self.setWindowFlags(Qt.WindowType.Window)

        # Window title
        title = self.config.get("ui.window_title", "NexPro PDF")
        self.setWindowTitle(title)

        # Get available screen geometry (accounts for taskbar)
        screen = self.screen().availableGeometry()

        # Set window size to 80% of available screen size for better fit
        width = int(screen.width() * 0.80)
        height = int(screen.height() * 0.80)

        # Ensure minimum usable size
        width = max(width, 1024)
        height = max(height, 700)

        # Make sure we don't exceed available screen size
        width = min(width, screen.width() - 100)
        height = min(height, screen.height() - 100)

        # Set size and position
        self.resize(width, height)

        # Center the window within available screen area
        x = screen.x() + (screen.width() - width) // 2
        y = screen.y() + (screen.height() - height) // 2
        self.move(x, y)

    def center_on_screen(self):
        """Center window on screen"""
        screen = self.screen().availableGeometry()
        window_rect = self.frameGeometry()
        x = screen.x() + (screen.width() - window_rect.width()) // 2
        y = screen.y() + (screen.height() - window_rect.height()) // 2
        self.move(x, y)

    def _create_menu_bar(self):
        """Create menu bar"""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")
        self._add_file_menu_actions(file_menu)

        # Edit menu
        edit_menu = menubar.addMenu("&Edit")
        self._add_edit_menu_actions(edit_menu)

        # View menu
        view_menu = menubar.addMenu("&View")
        self._add_view_menu_actions(view_menu)

        # Help menu
        help_menu = menubar.addMenu("&Help")
        self._add_help_menu_actions(help_menu)

    def _add_file_menu_actions(self, menu: QMenu):
        """Add File menu actions"""
        # New
        new_action = QAction("&New", self)
        new_action.setShortcut(QKeySequence.StandardKey.New)
        new_action.setStatusTip("Create new PDF")
        new_action.triggered.connect(self.new_file)
        menu.addAction(new_action)

        # Open
        open_action = QAction("&Open...", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.setStatusTip("Open existing PDF")
        open_action.triggered.connect(self.open_file)
        menu.addAction(open_action)

        menu.addSeparator()

        # Save
        save_action = QAction("&Save", self)
        save_action.setShortcut(QKeySequence.StandardKey.Save)
        save_action.setStatusTip("Save current PDF")
        save_action.triggered.connect(self.save_file)
        menu.addAction(save_action)

        # Save As
        save_as_action = QAction("Save &As...", self)
        save_as_action.setShortcut(QKeySequence.StandardKey.SaveAs)
        save_as_action.setStatusTip("Save PDF with new name")
        save_as_action.triggered.connect(self.save_file_as)
        menu.addAction(save_as_action)

        # Save All Edits (for edit text mode)
        save_all_action = QAction("Save All &Edits", self)
        save_all_action.setShortcut("Ctrl+Shift+S")
        save_all_action.setStatusTip("Save all pending text edits to PDF")
        save_all_action.triggered.connect(self.save_all_edits)
        menu.addAction(save_all_action)

        menu.addSeparator()

        # Close
        close_action = QAction("&Close", self)
        close_action.setShortcut("Ctrl+W")
        close_action.setStatusTip("Close current PDF file")
        close_action.triggered.connect(self.close_file)
        menu.addAction(close_action)

        menu.addSeparator()

        # Exit
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.setStatusTip("Exit application")
        exit_action.triggered.connect(self.close)
        menu.addAction(exit_action)

    def _add_edit_menu_actions(self, menu: QMenu):
        """Add Edit menu actions"""
        # Undo
        undo_action = QAction("&Undo", self)
        undo_action.setShortcut(QKeySequence.StandardKey.Undo)
        undo_action.setStatusTip("Undo last action")
        menu.addAction(undo_action)

        # Redo
        redo_action = QAction("&Redo", self)
        redo_action.setShortcut(QKeySequence.StandardKey.Redo)
        redo_action.setStatusTip("Redo last action")
        menu.addAction(redo_action)

        menu.addSeparator()

        # Copy
        copy_action = QAction("&Copy", self)
        copy_action.setShortcut(QKeySequence.StandardKey.Copy)
        menu.addAction(copy_action)

        # Paste
        paste_action = QAction("&Paste", self)
        paste_action.setShortcut(QKeySequence.StandardKey.Paste)
        menu.addAction(paste_action)

        menu.addSeparator()

        # Find & Replace
        find_replace_action = QAction("&Find && Replace...", self)
        find_replace_action.setShortcut("Ctrl+H")
        find_replace_action.setStatusTip("Find and replace text in PDF")
        find_replace_action.triggered.connect(self._open_find_replace)
        menu.addAction(find_replace_action)

    def _open_find_replace(self):
        """Open Find & Replace dialog"""
        if hasattr(self, 'pdf_viewer') and self.pdf_viewer:
            self.pdf_viewer.show_find_replace_dialog()
        else:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "No PDF", "Please open a PDF file first.")

    def _add_view_menu_actions(self, menu: QMenu):
        """Add View menu actions"""
        # Zoom In
        zoom_in = QAction("Zoom &In", self)
        zoom_in.setShortcut(QKeySequence.StandardKey.ZoomIn)
        menu.addAction(zoom_in)

        # Zoom Out
        zoom_out = QAction("Zoom &Out", self)
        zoom_out.setShortcut(QKeySequence.StandardKey.ZoomOut)
        menu.addAction(zoom_out)

        menu.addSeparator()

        # Fit Page
        fit_page = QAction("&Fit Page", self)
        menu.addAction(fit_page)

        # Fit Width
        fit_width = QAction("Fit &Width", self)
        menu.addAction(fit_width)

        menu.addSeparator()

        # Toggle Left Panel
        toggle_left = QAction("Toggle &Left Panel", self)
        toggle_left.setShortcut("F4")
        toggle_left.setStatusTip("Show/hide the left panel (thumbnails, bookmarks)")
        toggle_left.triggered.connect(self._toggle_left_panel)
        menu.addAction(toggle_left)

        # Toggle Right Panel
        toggle_right = QAction("Toggle &Right Panel", self)
        toggle_right.setShortcut("Shift+F4")
        toggle_right.setStatusTip("Show/hide the right panel (properties)")
        toggle_right.triggered.connect(self._toggle_right_panel)
        menu.addAction(toggle_right)

    def _toggle_left_panel(self):
        """Toggle left sidebar panel"""
        if hasattr(self, 'left_sidebar'):
            self.left_sidebar.toggle()

    def _toggle_right_panel(self):
        """Toggle right sidebar panel"""
        if hasattr(self, 'right_sidebar'):
            self.right_sidebar.toggle()

    def _add_help_menu_actions(self, menu: QMenu):
        """Add Help menu actions"""
        # About
        about_action = QAction("&About NexPro PDF", self)
        about_action.setStatusTip("About NexPro PDF")
        about_action.triggered.connect(self.show_about)
        menu.addAction(about_action)

        # Help
        help_action = QAction("&Help Documentation", self)
        help_action.setShortcut(QKeySequence.StandardKey.HelpContents)
        menu.addAction(help_action)

    def _create_ribbon(self):
        """Create ribbon toolbar"""
        self.ribbon = RibbonBar(self)
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.ribbon)

    def _create_main_layout(self):
        """Create main application layout"""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main vertical layout (file tab bar on top, then content below)
        outer_layout = QVBoxLayout(central_widget)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)

        # File tab bar at the top
        self._create_file_tab_bar()
        outer_layout.addWidget(self.file_tab_bar)

        # Content layout (horizontal)
        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # Left panel (thumbnails, bookmarks, layers, attachments)
        self.left_panel = LeftPanel(self)

        # Left sidebar icons: (icon, tooltip, tab_index)
        left_icons = [
            ("T", "Thumbnails (F4)", 0),
            ("B", "Bookmarks", 1),
            ("L", "Layers", 2),
            ("A", "Attachments", 3),
        ]
        self.left_sidebar = CollapsibleSidebar(self.left_panel, left_icons, "left", self)

        # Center panel (PDF viewer)
        self.pdf_viewer = PDFViewer(self)

        # Right panel (properties, formatting, security)
        self.right_panel = RightPanel(self)

        # Right sidebar icons: (icon, tooltip, tab_index)
        right_icons = [
            ("P", "Properties (Shift+F4)", 0),
            ("F", "Format", 1),
            ("S", "Security", 2),
        ]
        self.right_sidebar = CollapsibleSidebar(self.right_panel, right_icons, "right", self)

        # Add widgets to content layout
        content_layout.addWidget(self.left_sidebar)
        content_layout.addWidget(self.pdf_viewer, 1)  # PDF viewer takes remaining space
        content_layout.addWidget(self.right_sidebar)

        outer_layout.addLayout(content_layout)

    def _create_file_tab_bar(self):
        """Create file tab bar at the top showing current file with close button"""
        self.file_tab_bar = QFrame()
        self.file_tab_bar.setFixedHeight(32)
        self.file_tab_bar.setStyleSheet(f"""
            QFrame {{
                background-color: {ModernTheme.BACKGROUND};
                border-bottom: 1px solid {ModernTheme.BORDER};
            }}
        """)

        tab_layout = QHBoxLayout(self.file_tab_bar)
        tab_layout.setContentsMargins(10, 4, 10, 4)
        tab_layout.setSpacing(0)

        # File tab widget (shows current file with close button)
        self.file_tab_widget = QFrame()
        self.file_tab_widget.setStyleSheet(f"""
            QFrame {{
                background-color: {ModernTheme.SURFACE};
                border: 1px solid {ModernTheme.BORDER};
                border-bottom: none;
                border-radius: 6px 6px 0 0;
                padding: 0px;
                margin: 0px;
            }}
        """)
        file_tab_inner_layout = QHBoxLayout(self.file_tab_widget)
        file_tab_inner_layout.setContentsMargins(12, 4, 6, 4)
        file_tab_inner_layout.setSpacing(8)

        self.file_name_label = QLabel("No file open")
        self.file_name_label.setStyleSheet(f"""
            QLabel {{
                color: {ModernTheme.TEXT_SECONDARY};
                font-size: 12px;
                font-weight: 500;
                border: none;
                background: transparent;
            }}
        """)
        file_tab_inner_layout.addWidget(self.file_name_label)

        self.file_close_btn = QPushButton("✕")
        self.file_close_btn.setFixedSize(20, 20)
        self.file_close_btn.setToolTip("Close file (Ctrl+W)")
        self.file_close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.file_close_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                border-radius: 10px;
                font-size: 12px;
                font-weight: bold;
                color: #888888;
            }
            QPushButton:hover {
                background-color: #E74C3C;
                color: white;
            }
        """)
        self.file_close_btn.clicked.connect(self.close_file)
        self.file_close_btn.hide()  # Hidden when no file is open
        file_tab_inner_layout.addWidget(self.file_close_btn)

        tab_layout.addWidget(self.file_tab_widget)
        tab_layout.addStretch()  # Push tab to the left

    def _create_status_bar(self):
        """Create status bar"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # Left side - status label
        self.status_label = QLabel("Ready")
        self.status_bar.addWidget(self.status_label, 1)

        # Center - CA branding (highlighted)
        branding_label = QLabel("⭐ Prepared by CA Himanshu Majithiya ⭐")
        branding_label.setStyleSheet(f"""
            QLabel {{
                color: white;
                background-color: {ModernTheme.PRIMARY};
                font-weight: bold;
                font-size: 13px;
                padding: 4px 20px;
                border-radius: 4px;
                margin: 2px;
            }}
        """)
        branding_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_bar.addWidget(branding_label, 2)

        # Right side - page and zoom info
        page_label = QLabel("Page: 0/0")
        self.status_bar.addWidget(page_label, 1)

        zoom_label = QLabel("Zoom: 100%")
        self.status_bar.addPermanentWidget(zoom_label)

    def _apply_styling(self):
        """Apply modern professional styling"""
        # Apply modern theme stylesheet
        self.setStyleSheet(ModernTheme.get_main_stylesheet())

    def showEvent(self, event):
        """Override showEvent to center window on first display"""
        super().showEvent(event)
        if self._first_show:
            self._first_show = False
            # Center window after it's fully displayed
            self.center_on_screen()

    # File operations
    def new_file(self):
        """Create new PDF"""
        self.logger.info("New file requested")
        self.status_label.setText("Creating new file...")

    def open_file(self):
        """Open existing PDF"""
        self.logger.info("Open file requested")
        from PyQt6.QtWidgets import QFileDialog
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open PDF",
            "",
            "PDF Files (*.pdf);;All Files (*)"
        )
        if file_path:
            self.load_pdf(file_path)

    def close_file(self):
        """Close current PDF file"""
        if not self.current_file:
            return

        self.logger.info(f"Closing file: {self.current_file}")

        # Close the PDF in the viewer
        self.pdf_viewer.close_pdf()

        # Reset state
        self.current_file = None
        self.setWindowTitle(self.config.get("ui.window_title", "NexPro PDF"))
        self.status_label.setText("Ready - No file open")

        # Update file tab - show "No file open" and hide close button
        self.file_name_label.setText("No file open")
        self.file_name_label.setStyleSheet(f"""
            QLabel {{
                color: {ModernTheme.TEXT_SECONDARY};
                font-size: 12px;
                font-weight: 500;
                border: none;
                background: transparent;
            }}
        """)
        self.file_close_btn.hide()

    def load_pdf(self, file_path: str):
        """Load PDF file"""
        try:
            self.logger.info(f"Loading PDF: {file_path}")
            self.current_file = file_path
            self.pdf_viewer.load_pdf(file_path)
            self.setWindowTitle(f"{self.config.get('ui.window_title')} - {file_path}")
            self.status_label.setText(f"Loaded: {file_path}")

            # Update file tab with file name and show close button
            import os
            file_name = os.path.basename(file_path)
            self.file_name_label.setText(file_name)
            self.file_name_label.setStyleSheet(f"""
                QLabel {{
                    color: {ModernTheme.TEXT_PRIMARY};
                    font-size: 12px;
                    font-weight: 500;
                    border: none;
                    background: transparent;
                }}
            """)
            self.file_close_btn.show()
        except Exception as e:
            self.logger.error(f"Error loading PDF: {e}")
            QMessageBox.critical(self, "Error", f"Failed to load PDF: {e}")

    def save_file(self):
        """Save current PDF"""
        # Check if edit text mode is active - if so, delegate to edit text save
        if hasattr(self, 'pdf_viewer') and self.pdf_viewer.edit_text_mode:
            self.logger.info("Edit text mode active - delegating to edit text save")
            self.pdf_viewer._save_edited_text()
            return

        if self.current_file and hasattr(self, 'pdf_viewer') and self.pdf_viewer.pdf_document:
            try:
                self.logger.info(f"Saving file: {self.current_file}")
                import tempfile, shutil

                # Save to temp file first, then replace original
                temp_fd, temp_path = tempfile.mkstemp(suffix='.pdf')
                import os
                os.close(temp_fd)

                self.pdf_viewer.pdf_document.save(temp_path, garbage=4, deflate=True, clean=True)

                # Close current document, replace file, reopen
                self.pdf_viewer.pdf_document.close()
                shutil.move(temp_path, self.current_file)
                self.pdf_viewer.pdf_document = __import__('fitz').open(self.current_file)
                self.pdf_viewer.render_current_page()

                self.status_label.setText("File saved successfully")
                self.logger.info("File saved successfully")
            except Exception as e:
                self.logger.error(f"Error saving file: {e}")
                from PyQt6.QtWidgets import QMessageBox
                QMessageBox.critical(self, "Save Error", f"Failed to save file: {e}")
        else:
            self.save_file_as()

    def save_file_as(self):
        """Save PDF with new name"""
        from PyQt6.QtWidgets import QFileDialog, QMessageBox

        if not hasattr(self, 'pdf_viewer') or not self.pdf_viewer.pdf_document:
            QMessageBox.warning(self, "No PDF", "No PDF document to save.")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save PDF As",
            self.current_file or "",
            "PDF Files (*.pdf)"
        )
        if file_path:
            try:
                self.logger.info(f"Saving file as: {file_path}")
                self.pdf_viewer.pdf_document.save(file_path, garbage=4, deflate=True, clean=True)
                self.current_file = file_path
                self.status_label.setText(f"Saved as: {file_path}")

                # Reload from the new file
                self.load_pdf(file_path)
            except Exception as e:
                self.logger.error(f"Error saving file: {e}")
                QMessageBox.critical(self, "Save Error", f"Failed to save file: {e}")

    def save_all_edits(self):
        """Save all pending text edits to PDF"""
        if hasattr(self, 'pdf_viewer') and self.pdf_viewer.edit_text_mode:
            self.logger.info("Saving all pending edits")
            self.pdf_viewer.save_all_edits()
        else:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.information(
                self,
                "No Edit Mode",
                "Edit text mode is not active. Use Edit > Edit Text to enter edit mode."
            )

    def show_about(self):
        """Show about dialog"""
        about_text = f"""
        <h2>NexPro PDF</h2>
        <p>Version {self.config.get('app.version', '1.0.0')}</p>
        <p>Professional PDF Editor & Writer</p>
        <p>Copyright © 2024 {self.config.get('app.company', 'NexPro Technologies')}</p>
        <p><b>Features:</b></p>
        <ul>
            <li>PDF Creation & Conversion</li>
            <li>Advanced Editing</li>
            <li>Secure Redaction</li>
            <li>Digital Signatures</li>
            <li>Security & Encryption</li>
        </ul>
        <p><i>Built for Professionals</i></p>
        """
        QMessageBox.about(self, "About NexPro PDF", about_text)

    def closeEvent(self, event):
        """Handle window close event"""
        self.logger.info("Application closing")
        event.accept()
