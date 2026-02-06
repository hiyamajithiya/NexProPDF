"""
PDF Viewer component for NexPro PDF
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QScrollArea,
    QLabel, QPushButton, QSlider, QComboBox, QToolBar, QTextEdit, QLineEdit,
    QMessageBox, QFileDialog, QDialog, QFormLayout, QCheckBox, QSpinBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize, QPoint, QRect, QEvent
from PyQt6.QtGui import QPixmap, QImage, QPainter, QPen, QColor, QCursor, QMouseEvent, QFont, QKeyEvent
from src.utilities.logger import get_logger
from src.ui.modern_theme import ModernTheme
import fitz  # PyMuPDF


class FindReplaceDialog(QDialog):
    """Simple Find & Replace dialog for PDF text editing"""

    def __init__(self, parent=None, pdf_viewer=None):
        super().__init__(parent)
        self.pdf_viewer = pdf_viewer
        self.logger = get_logger()
        self.found_locations = []  # List of (page, rect) tuples
        self.current_match_index = -1

        self.setWindowTitle("Find & Replace")
        self.setMinimumWidth(450)
        self.setModal(False)  # Allow interaction with PDF while dialog is open

        self._setup_ui()

    def _setup_ui(self):
        """Setup the dialog UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        # Form layout for find/replace fields
        form_layout = QFormLayout()
        form_layout.setSpacing(8)

        # Find field
        self.find_input = QLineEdit()
        self.find_input.setPlaceholderText("Enter text to find...")
        self.find_input.setMinimumHeight(32)
        self.find_input.textChanged.connect(self._on_find_text_changed)
        form_layout.addRow("Find:", self.find_input)

        # Replace field
        self.replace_input = QLineEdit()
        self.replace_input.setPlaceholderText("Enter replacement text...")
        self.replace_input.setMinimumHeight(32)
        form_layout.addRow("Replace:", self.replace_input)

        layout.addLayout(form_layout)

        # Options
        options_layout = QHBoxLayout()
        self.case_sensitive = QCheckBox("Case sensitive")
        self.whole_word = QCheckBox("Whole word")
        options_layout.addWidget(self.case_sensitive)
        options_layout.addWidget(self.whole_word)
        options_layout.addStretch()
        layout.addLayout(options_layout)

        # Results label
        self.results_label = QLabel("")
        self.results_label.setStyleSheet(f"color: {ModernTheme.TEXT_SECONDARY}; font-size: 12px;")
        layout.addWidget(self.results_label)

        # Buttons
        buttons_layout = QHBoxLayout()

        self.find_btn = QPushButton("Find")
        self.find_btn.clicked.connect(self._find_text)
        self.find_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {ModernTheme.PRIMARY};
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {ModernTheme.PRIMARY_DARK};
            }}
        """)

        self.find_next_btn = QPushButton("Find Next")
        self.find_next_btn.clicked.connect(self._find_next)
        self.find_next_btn.setEnabled(False)

        self.replace_btn = QPushButton("Replace")
        self.replace_btn.clicked.connect(self._replace_current)
        self.replace_btn.setEnabled(False)
        self.replace_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {ModernTheme.SECONDARY};
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {ModernTheme.SECONDARY_DARK};
            }}
            QPushButton:disabled {{
                background-color: {ModernTheme.BORDER};
                color: {ModernTheme.TEXT_DISABLED};
            }}
        """)

        self.replace_all_btn = QPushButton("Replace All")
        self.replace_all_btn.clicked.connect(self._replace_all)
        self.replace_all_btn.setEnabled(False)
        self.replace_all_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {ModernTheme.SUCCESS};
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #1B5E20;
            }}
            QPushButton:disabled {{
                background-color: {ModernTheme.BORDER};
                color: {ModernTheme.TEXT_DISABLED};
            }}
        """)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)

        buttons_layout.addWidget(self.find_btn)
        buttons_layout.addWidget(self.find_next_btn)
        buttons_layout.addWidget(self.replace_btn)
        buttons_layout.addWidget(self.replace_all_btn)
        buttons_layout.addStretch()
        buttons_layout.addWidget(close_btn)

        layout.addLayout(buttons_layout)

        # Set dialog style
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {ModernTheme.SURFACE};
            }}
            QLineEdit {{
                padding: 8px;
                border: 1px solid {ModernTheme.BORDER};
                border-radius: 4px;
                font-size: 13px;
            }}
            QLineEdit:focus {{
                border-color: {ModernTheme.PRIMARY};
            }}
            QCheckBox {{
                font-size: 12px;
            }}
            QPushButton {{
                padding: 6px 12px;
                border-radius: 4px;
            }}
        """)

    def _on_find_text_changed(self, text):
        """Clear previous results when find text changes"""
        self.found_locations = []
        self.current_match_index = -1
        self.results_label.setText("")
        self.find_next_btn.setEnabled(False)
        self.replace_btn.setEnabled(False)
        self.replace_all_btn.setEnabled(False)

        # Clear any highlights
        if self.pdf_viewer:
            self.pdf_viewer.render_current_page()

    def _find_text(self):
        """Find all occurrences of the text in the PDF"""
        find_text = self.find_input.text().strip()
        if not find_text:
            QMessageBox.warning(self, "Find", "Please enter text to find.")
            return

        if not self.pdf_viewer or not self.pdf_viewer.pdf_document:
            QMessageBox.warning(self, "Find", "No PDF document loaded.")
            return

        self.found_locations = []
        self.current_match_index = -1

        pdf_doc = self.pdf_viewer.pdf_document

        # Search through all pages
        for page_num in range(len(pdf_doc)):
            page = pdf_doc[page_num]

            # Search for text
            if self.case_sensitive.isChecked():
                results = page.search_for(find_text)
            else:
                # Case-insensitive search
                results = page.search_for(find_text, quads=False)

            for rect in results:
                self.found_locations.append((page_num, rect, find_text))

        if self.found_locations:
            self.results_label.setText(f"Found {len(self.found_locations)} match(es)")
            self.find_next_btn.setEnabled(True)
            self.replace_btn.setEnabled(True)
            self.replace_all_btn.setEnabled(True)

            # Go to first match
            self._find_next()
        else:
            self.results_label.setText("No matches found")
            self.find_next_btn.setEnabled(False)
            self.replace_btn.setEnabled(False)
            self.replace_all_btn.setEnabled(False)

        self.logger.info(f"Find: '{find_text}' - {len(self.found_locations)} matches")

    def _find_next(self):
        """Go to next match"""
        if not self.found_locations:
            return

        self.current_match_index = (self.current_match_index + 1) % len(self.found_locations)
        page_num, rect, _ = self.found_locations[self.current_match_index]

        # Navigate to the page if needed
        if self.pdf_viewer.current_page != page_num:
            self.pdf_viewer.go_to_page(page_num)

        # Highlight the current match
        self._highlight_match(page_num, rect)

        # Update results label
        self.results_label.setText(
            f"Match {self.current_match_index + 1} of {len(self.found_locations)} (Page {page_num + 1})"
        )

    def _highlight_match(self, page_num, rect):
        """Highlight the current match on the PDF"""
        if not self.pdf_viewer:
            return

        # Re-render the page first
        self.pdf_viewer.render_current_page()

        # Draw highlight rectangle on top
        zoom = self.pdf_viewer.zoom_level
        x0 = int(rect.x0 * zoom)
        y0 = int(rect.y0 * zoom)
        x1 = int(rect.x1 * zoom)
        y1 = int(rect.y1 * zoom)

        # Get current pixmap and draw on it
        current_pixmap = self.pdf_viewer.pdf_label.pixmap()
        if current_pixmap:
            pixmap = QPixmap(current_pixmap)
            painter = QPainter(pixmap)
            painter.setPen(QPen(QColor(255, 165, 0), 2))  # Orange border
            painter.setBrush(QColor(255, 255, 0, 80))  # Yellow highlight
            painter.drawRect(x0, y0, x1 - x0, y1 - y0)
            painter.end()

            self.pdf_viewer.pdf_label.setPixmap(pixmap)

    def _replace_current(self):
        """Replace the currently selected match"""
        if self.current_match_index < 0 or not self.found_locations:
            QMessageBox.warning(self, "Replace", "No match selected. Click 'Find' first.")
            return

        replace_text = self.replace_input.text()
        page_num, rect, find_text = self.found_locations[self.current_match_index]

        # Perform the replacement
        success = self._do_replace(page_num, rect, find_text, replace_text)

        if success:
            # Remove this match from the list
            del self.found_locations[self.current_match_index]

            if self.found_locations:
                # Adjust index if needed
                if self.current_match_index >= len(self.found_locations):
                    self.current_match_index = 0
                else:
                    self.current_match_index -= 1  # So next find_next shows current index

                self.results_label.setText(f"{len(self.found_locations)} match(es) remaining")
                self._find_next()
            else:
                self.results_label.setText("All matches replaced")
                self.find_next_btn.setEnabled(False)
                self.replace_btn.setEnabled(False)
                self.replace_all_btn.setEnabled(False)
                self.current_match_index = -1

    def _replace_all(self):
        """Replace all matches"""
        if not self.found_locations:
            QMessageBox.warning(self, "Replace All", "No matches found. Click 'Find' first.")
            return

        replace_text = self.replace_input.text()
        find_text = self.find_input.text().strip()

        # Confirm replacement
        reply = QMessageBox.question(
            self,
            "Replace All",
            f"Replace all {len(self.found_locations)} occurrences of '{find_text}' with '{replace_text}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        replaced_count = 0

        # Group by page for efficiency (process in reverse order to maintain rect positions)
        pages_to_process = {}
        for page_num, rect, text in self.found_locations:
            if page_num not in pages_to_process:
                pages_to_process[page_num] = []
            pages_to_process[page_num].append((rect, text))

        # Process each page
        for page_num in sorted(pages_to_process.keys()):
            matches = pages_to_process[page_num]
            for rect, text in matches:
                if self._do_replace(page_num, rect, text, replace_text):
                    replaced_count += 1

        # Clear matches and refresh
        self.found_locations = []
        self.current_match_index = -1
        self.find_next_btn.setEnabled(False)
        self.replace_btn.setEnabled(False)
        self.replace_all_btn.setEnabled(False)

        self.results_label.setText(f"Replaced {replaced_count} occurrence(s)")

        # Re-render
        self.pdf_viewer.render_current_page()

        QMessageBox.information(
            self,
            "Replace All",
            f"Successfully replaced {replaced_count} occurrence(s).\n\n"
            "Note: Changes are in memory. Use File > Save As to save the modified PDF."
        )

        self.logger.info(f"Replace all: replaced {replaced_count} occurrences")

    def _do_replace(self, page_num, rect, old_text, new_text):
        """Perform the actual text replacement with smart fitting"""
        if not self.pdf_viewer or not self.pdf_viewer.pdf_document:
            return False

        try:
            page = self.pdf_viewer.pdf_document[page_num]

            # Get font info from the area being replaced
            text_dict = page.get_text("dict")
            original_font_size = 11  # Default
            font_name = "helv"

            # Find the text block containing this rect to get font info
            for block in text_dict.get("blocks", []):
                if block.get("type") == 0:  # Text block
                    for line in block.get("lines", []):
                        for span in line.get("spans", []):
                            span_rect = fitz.Rect(span["bbox"])
                            if span_rect.intersects(rect):
                                original_font_size = span.get("size", 11)
                                font_name = span.get("font", "helv")
                                # Normalize font name
                                if "arial" in font_name.lower() or "helvetica" in font_name.lower():
                                    font_name = "helv"
                                elif "times" in font_name.lower():
                                    font_name = "tiro"
                                elif "courier" in font_name.lower():
                                    font_name = "cour"
                                else:
                                    font_name = "helv"
                                break

            # Smart Fitting: Calculate if new text fits at original size
            available_width = rect.width
            min_font_size = 6.0  # Minimum readable font size

            # Find the best font size that fits
            final_font_size = original_font_size
            text_fits = False

            # Try original font size first, then progressively smaller sizes
            test_font_size = original_font_size
            while test_font_size >= min_font_size:
                try:
                    text_width = fitz.get_text_length(new_text, fontname=font_name, fontsize=test_font_size)
                    if text_width <= available_width:
                        final_font_size = test_font_size
                        text_fits = True
                        break
                except:
                    # If get_text_length fails, estimate width
                    text_width = len(new_text) * test_font_size * 0.6
                    if text_width <= available_width:
                        final_font_size = test_font_size
                        text_fits = True
                        break

                # Reduce font size by 0.5pt each iteration
                test_font_size -= 0.5

            # If text still doesn't fit at minimum size, warn user
            if not text_fits:
                try:
                    text_width_at_min = fitz.get_text_length(new_text, fontname=font_name, fontsize=min_font_size)
                except:
                    text_width_at_min = len(new_text) * min_font_size * 0.6

                msg_box = QMessageBox(self)
                msg_box.setWindowTitle("Text Too Long")
                msg_box.setText(
                    f"The replacement text '{new_text}' is too long to fit in the available space.\n\n"
                    f"Original text: '{old_text}'\n"
                    f"Available width: {available_width:.1f}pt\n"
                    f"Text width at 6pt: {text_width_at_min:.1f}pt\n\n"
                    "Choose an option:"
                )

                scale_btn = msg_box.addButton("Use 6pt Font (smallest)", QMessageBox.ButtonRole.AcceptRole)
                proceed_btn = msg_box.addButton("Proceed Anyway (may overlap)", QMessageBox.ButtonRole.ActionRole)
                cancel_btn = msg_box.addButton("Cancel", QMessageBox.ButtonRole.RejectRole)

                msg_box.exec()

                clicked_btn = msg_box.clickedButton()

                if clicked_btn == cancel_btn:
                    self.logger.info(f"User cancelled replacement due to text overflow")
                    return False
                elif clicked_btn == scale_btn:
                    final_font_size = min_font_size
                    self.logger.info(f"User chose to scale to minimum font size: {min_font_size}pt")
                else:  # proceed_btn
                    final_font_size = original_font_size
                    self.logger.info(f"User chose to proceed anyway with original size: {original_font_size}pt")

            # Log if font size was adjusted
            if final_font_size != original_font_size:
                self.logger.info(f"Font size adjusted from {original_font_size}pt to {final_font_size}pt to fit text")

            # Redact the old text
            page.add_redact_annot(rect, fill=(1, 1, 1))  # White fill
            page.apply_redactions()

            # Insert new text at the same position
            # Calculate baseline position (approximately 85% down from top of rect)
            baseline_y = rect.y0 + (final_font_size * 0.85)

            page.insert_text(
                (rect.x0, baseline_y),
                new_text,
                fontsize=final_font_size,
                fontname=font_name,
                color=(0, 0, 0)
            )

            self.logger.info(f"Replaced '{old_text}' with '{new_text}' at page {page_num + 1}")

            # Re-render the page to show the change
            self.pdf_viewer.render_current_page()

            return True

        except Exception as e:
            self.logger.error(f"Error replacing text: {e}")
            QMessageBox.warning(
                self,
                "Replace Error",
                f"Failed to replace text: {str(e)}"
            )
            return False

    def closeEvent(self, event):
        """Handle dialog close"""
        # Clear any highlights
        if self.pdf_viewer:
            self.pdf_viewer.render_current_page()
        super().closeEvent(event)


class EditTextBox(QTextEdit):
    """Custom text box for editing PDF text with Ctrl+S support"""

    save_requested = pyqtSignal()  # Signal emitted when Ctrl+S is pressed
    cancel_requested = pyqtSignal()  # Signal emitted when Esc is pressed

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.logger = get_logger()

    def keyPressEvent(self, event: QKeyEvent):
        """Override to capture Ctrl+S before QTextEdit processes it"""
        self.logger.info(f"EditTextBox keyPressEvent: key={event.key()}, modifiers={event.modifiers()}")

        # Ctrl+S to save
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_S:
            self.logger.info("*** CTRL+S DETECTED IN EditTextBox - EMITTING SIGNAL ***")
            self.save_requested.emit()
            event.accept()  # Mark event as handled
            return
        # Escape to cancel
        elif event.key() == Qt.Key.Key_Escape:
            self.logger.info("*** ESC DETECTED IN EditTextBox - EMITTING SIGNAL ***")
            self.cancel_requested.emit()
            event.accept()
            return

        # Let QTextEdit handle all other keys
        super().keyPressEvent(event)


class EditableTextBox(QTextEdit):
    """Floating text box that appears on PDF for direct editing"""

    # Signal emitted when editing is done (text, x, y, font_size)
    editing_finished = pyqtSignal(str, float, float, int)
    editing_cancelled = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.pdf_x = 0
        self.pdf_y = 0
        self.font_size = 12

        # Style the text box with modern design
        self.setStyleSheet(f"""
            QTextEdit {{
                background-color: {ModernTheme.SURFACE};
                border: 3px solid {ModernTheme.PRIMARY};
                border-radius: 8px;
                padding: 10px;
                box-shadow: 0 4px 12px {ModernTheme.SHADOW_HEAVY};
                font-size: 13px;
            }}
        """)

        # Set default font
        font = QFont("Arial", 12)
        self.setFont(font)

        # Enable focus and cursor
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setCursorWidth(2)

        # Set placeholder
        self.setPlaceholderText("Type here... Press Ctrl+Enter to save, Esc to cancel")

    def keyPressEvent(self, event):
        """Handle key press events"""
        # Ctrl+Enter or Ctrl+Return to finish editing
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter) and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            self.finish_editing()
        # Escape to cancel
        elif event.key() == Qt.Key.Key_Escape:
            self.cancel_editing()
        else:
            super().keyPressEvent(event)

    def finish_editing(self):
        """Finish editing and emit signal"""
        text = self.toPlainText().strip()
        if text:
            self.editing_finished.emit(text, self.pdf_x, self.pdf_y, self.font_size)
        self.hide()

    def cancel_editing(self):
        """Cancel editing"""
        self.editing_cancelled.emit()
        self.hide()

    def start_editing(self, screen_x: int, screen_y: int, pdf_x: float, pdf_y: float, font_size: int = 12, width: int = 300):
        """Start editing at specified position"""
        self.pdf_x = pdf_x
        self.pdf_y = pdf_y
        self.font_size = font_size

        # Set font size
        font = self.font()
        font.setPointSize(font_size)
        self.setFont(font)

        # Position and size
        self.setGeometry(screen_x, screen_y, width, 100)

        # Clear previous text
        self.clear()

        # Show and focus
        self.show()
        self.setFocus()
        self.raise_()


class InteractivePDFLabel(QLabel):
    """Interactive PDF label that supports click-to-edit"""

    # Signal emitted when user clicks on PDF (x, y coordinates in PDF space)
    pdf_clicked = pyqtSignal(float, float, int, int)  # pdf_x, pdf_y, screen_x, screen_y
    text_block_clicked = pyqtSignal(dict)  # Signal emitted when text block is clicked
    redaction_drawn = pyqtSignal(object)  # Signal emitted when redaction rectangle is drawn (fitz.Rect)
    area_selected = pyqtSignal(float, float, float, float)  # Signal emitted when area is selected (x0, y0, x1, y1 in PDF coords)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.edit_mode = False
        self.edit_mode_type = None  # 'text' or 'image'
        self.click_position = None
        self.zoom_level = 1.0
        self.original_pixmap = None

        # Edit text mode
        self.edit_text_mode = False
        self.text_blocks = []
        self.selected_block_index = None

        # Redaction mode
        self.redaction_mode = False
        self.redaction_rects = []  # List of redaction rectangles (in PDF coordinates)
        self.drawing_redaction = False
        self.redaction_start = None  # Start point of current redaction rectangle
        self.redaction_current = None  # Current point while drawing

        # Area selection mode (for text/image/comment placement)
        self.selection_mode = False
        self.selection_mode_type = None  # 'text', 'image', 'comment'
        self.drawing_selection = False
        self.selection_start = None
        self.selection_current = None
        self.selection_rect = None  # Final selection in PDF coordinates

        # Set cursor to normal by default
        self.setCursor(QCursor(Qt.CursorShape.ArrowCursor))

    def set_edit_mode(self, enabled: bool, mode_type: str = 'text'):
        """Enable or disable edit mode"""
        self.edit_mode = enabled
        self.edit_mode_type = mode_type
        if enabled:
            self.setCursor(QCursor(Qt.CursorShape.IBeamCursor if mode_type == 'text' else Qt.CursorShape.CrossCursor))
        else:
            self.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
            self.click_position = None
            # Restore original pixmap without marker
            if self.original_pixmap:
                super().setPixmap(self.original_pixmap)

    def setPixmap(self, pixmap):
        """Override to store original pixmap"""
        self.original_pixmap = pixmap
        super().setPixmap(pixmap)

    def set_text_blocks(self, blocks, zoom_level):
        """Set text blocks for editing mode"""
        self.text_blocks = blocks
        self.zoom_level = zoom_level
        self.update()  # Trigger repaint

    def set_edit_text_mode(self, enabled: bool):
        """Enable or disable edit text mode"""
        self.edit_text_mode = enabled
        if enabled:
            self.setCursor(QCursor(Qt.CursorShape.IBeamCursor))
        else:
            self.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
            self.text_blocks = []
            self.selected_block_index = None
        self.update()  # Trigger repaint

    def set_redaction_mode(self, enabled: bool):
        """Enable or disable redaction mode for drawing redaction rectangles"""
        self.redaction_mode = enabled
        if enabled:
            self.setCursor(QCursor(Qt.CursorShape.CrossCursor))
            self.redaction_rects = []  # Clear previous redactions
        else:
            self.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
            self.drawing_redaction = False
            self.redaction_start = None
            self.redaction_current = None
        self.update()

    def clear_redaction_rects(self):
        """Clear all redaction rectangles"""
        self.redaction_rects = []
        self.update()

    def get_redaction_rects(self):
        """Get all redaction rectangles in PDF coordinates"""
        return self.redaction_rects

    def set_selection_mode(self, enabled: bool, mode_type: str = 'text'):
        """Enable or disable area selection mode for placing text/image/comment"""
        self.selection_mode = enabled
        self.selection_mode_type = mode_type
        if enabled:
            self.setCursor(QCursor(Qt.CursorShape.CrossCursor))
            self.selection_rect = None
        else:
            self.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
            self.drawing_selection = False
            self.selection_start = None
            self.selection_current = None
        self.update()

    def get_selection_rect(self):
        """Get the selected area in PDF coordinates"""
        return self.selection_rect

    def clear_selection(self):
        """Clear the selection"""
        self.selection_rect = None
        self.selection_start = None
        self.selection_current = None
        self.drawing_selection = False
        self.update()

    def paintEvent(self, event):
        """Override to draw bounding box only for selected text block in edit mode"""
        super().paintEvent(event)

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Only draw highlight for the SELECTED block, not all blocks
        if self.edit_text_mode and self.text_blocks and self.selected_block_index is not None:
            # Only draw the selected block
            if 0 <= self.selected_block_index < len(self.text_blocks):
                block = self.text_blocks[self.selected_block_index]
                bbox = block['bbox']  # (x0, y0, x1, y1) in PDF coordinates

                # Convert PDF coordinates to screen coordinates
                x0 = bbox[0] * self.zoom_level
                y0 = bbox[1] * self.zoom_level
                x1 = bbox[2] * self.zoom_level
                y1 = bbox[3] * self.zoom_level

                # Draw selected block with subtle highlight
                pen = QPen(QColor(41, 128, 185), 2, Qt.PenStyle.SolidLine)
                painter.setPen(pen)
                painter.setBrush(QColor(41, 128, 185, 20))  # Very light blue fill

                rect = QRect(int(x0), int(y0), int(x1 - x0), int(y1 - y0))
                painter.drawRect(rect)

        # Draw redaction rectangles
        if self.redaction_mode:
            # Draw existing redaction rectangles
            for redact_rect in self.redaction_rects:
                x0 = int(redact_rect[0] * self.zoom_level)
                y0 = int(redact_rect[1] * self.zoom_level)
                x1 = int(redact_rect[2] * self.zoom_level)
                y1 = int(redact_rect[3] * self.zoom_level)

                pen = QPen(QColor(220, 53, 69), 2, Qt.PenStyle.SolidLine)  # Red border
                painter.setPen(pen)
                painter.setBrush(QColor(0, 0, 0, 150))  # Semi-transparent black fill
                painter.drawRect(x0, y0, x1 - x0, y1 - y0)

            # Draw the rectangle being currently drawn
            if self.drawing_redaction and self.redaction_start and self.redaction_current:
                x0 = min(self.redaction_start.x(), self.redaction_current.x())
                y0 = min(self.redaction_start.y(), self.redaction_current.y())
                x1 = max(self.redaction_start.x(), self.redaction_current.x())
                y1 = max(self.redaction_start.y(), self.redaction_current.y())

                pen = QPen(QColor(220, 53, 69), 2, Qt.PenStyle.DashLine)  # Red dashed border
                painter.setPen(pen)
                painter.setBrush(QColor(220, 53, 69, 80))  # Semi-transparent red fill
                painter.drawRect(x0, y0, x1 - x0, y1 - y0)

        # Draw area selection rectangle
        if self.selection_mode and self.drawing_selection and self.selection_start and self.selection_current:
            x0 = min(self.selection_start.x(), self.selection_current.x())
            y0 = min(self.selection_start.y(), self.selection_current.y())
            x1 = max(self.selection_start.x(), self.selection_current.x())
            y1 = max(self.selection_start.y(), self.selection_current.y())

            # Blue dashed border for selection
            pen = QPen(QColor(41, 128, 185), 2, Qt.PenStyle.DashLine)
            painter.setPen(pen)
            painter.setBrush(QColor(41, 128, 185, 40))  # Semi-transparent blue fill
            painter.drawRect(x0, y0, x1 - x0, y1 - y0)

        painter.end()

    def mousePressEvent(self, event: QMouseEvent):
        """Handle mouse click"""
        # Handle area selection mode - start drawing selection rectangle
        if self.selection_mode and event.button() == Qt.MouseButton.LeftButton:
            self.drawing_selection = True
            self.selection_start = event.pos()
            self.selection_current = event.pos()
            self.update()
            return

        # Handle redaction mode - start drawing rectangle
        if self.redaction_mode and event.button() == Qt.MouseButton.LeftButton:
            self.drawing_redaction = True
            self.redaction_start = event.pos()
            self.redaction_current = event.pos()
            self.update()
            return

        if self.edit_text_mode and event.button() == Qt.MouseButton.LeftButton:
            # Check if clicked on a text block
            click_pos = event.pos()

            for i, block in enumerate(self.text_blocks):
                bbox = block['bbox']
                x0 = bbox[0] * self.zoom_level
                y0 = bbox[1] * self.zoom_level
                x1 = bbox[2] * self.zoom_level
                y1 = bbox[3] * self.zoom_level

                rect = QRect(int(x0), int(y0), int(x1 - x0), int(y1 - y0))

                if rect.contains(click_pos):
                    self.selected_block_index = i
                    self.update()  # Repaint to show selection
                    self.text_block_clicked.emit(block)
                    return

            # Clicked outside any block
            self.selected_block_index = None
            self.update()

        elif self.edit_mode and event.button() == Qt.MouseButton.LeftButton:
            # Get click position relative to label
            click_pos = event.pos()

            # Store click position
            self.click_position = click_pos

            # Convert to PDF coordinates (accounting for zoom)
            pdf_x = click_pos.x() / self.zoom_level
            pdf_y = click_pos.y() / self.zoom_level

            # Get screen position for text box
            screen_pos = self.mapToGlobal(click_pos)

            # Emit signal with both PDF and screen coordinates
            self.pdf_clicked.emit(pdf_x, pdf_y, click_pos.x(), click_pos.y())

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        """Handle mouse move for redaction/selection drawing"""
        if self.selection_mode and self.drawing_selection:
            self.selection_current = event.pos()
            self.update()
        elif self.redaction_mode and self.drawing_redaction:
            self.redaction_current = event.pos()
            self.update()
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        """Handle mouse release to finish redaction/selection rectangle"""
        # Handle area selection completion
        if self.selection_mode and self.drawing_selection and event.button() == Qt.MouseButton.LeftButton:
            self.drawing_selection = False

            if self.selection_start and self.selection_current:
                # Calculate rectangle in screen coordinates
                x0 = min(self.selection_start.x(), self.selection_current.x())
                y0 = min(self.selection_start.y(), self.selection_current.y())
                x1 = max(self.selection_start.x(), self.selection_current.x())
                y1 = max(self.selection_start.y(), self.selection_current.y())

                # Only accept if rectangle has some size (at least 10x10 pixels)
                if (x1 - x0) > 10 and (y1 - y0) > 10:
                    # Convert to PDF coordinates
                    pdf_x0 = x0 / self.zoom_level
                    pdf_y0 = y0 / self.zoom_level
                    pdf_x1 = x1 / self.zoom_level
                    pdf_y1 = y1 / self.zoom_level

                    # Store selection
                    self.selection_rect = (pdf_x0, pdf_y0, pdf_x1, pdf_y1)

                    # Emit signal with selection coordinates
                    self.area_selected.emit(pdf_x0, pdf_y0, pdf_x1, pdf_y1)

            self.selection_start = None
            self.selection_current = None
            self.update()
            return

        # Handle redaction mode
        if self.redaction_mode and self.drawing_redaction and event.button() == Qt.MouseButton.LeftButton:
            self.drawing_redaction = False

            if self.redaction_start and self.redaction_current:
                # Calculate rectangle in screen coordinates
                x0 = min(self.redaction_start.x(), self.redaction_current.x())
                y0 = min(self.redaction_start.y(), self.redaction_current.y())
                x1 = max(self.redaction_start.x(), self.redaction_current.x())
                y1 = max(self.redaction_start.y(), self.redaction_current.y())

                # Only add if rectangle has some size
                if (x1 - x0) > 5 and (y1 - y0) > 5:
                    # Convert to PDF coordinates
                    pdf_x0 = x0 / self.zoom_level
                    pdf_y0 = y0 / self.zoom_level
                    pdf_x1 = x1 / self.zoom_level
                    pdf_y1 = y1 / self.zoom_level

                    # Store as tuple (x0, y0, x1, y1) in PDF coordinates
                    self.redaction_rects.append((pdf_x0, pdf_y0, pdf_x1, pdf_y1))

                    # Emit signal with the fitz.Rect
                    self.redaction_drawn.emit(fitz.Rect(pdf_x0, pdf_y0, pdf_x1, pdf_y1))

            self.redaction_start = None
            self.redaction_current = None
            self.update()

        super().mouseReleaseEvent(event)


class PDFViewer(QWidget):
    """PDF viewer with navigation and zoom controls"""

    page_changed = pyqtSignal(int)  # Current page number
    zoom_changed = pyqtSignal(float)  # Current zoom level
    pdf_clicked = pyqtSignal(float, float, int, int)  # PDF clicked at (pdf_x, pdf_y, screen_x, screen_y)
    text_added = pyqtSignal(str, float, float, int)  # Text, x, y, font_size
    area_selected = pyqtSignal(float, float, float, float)  # Area selected (x0, y0, x1, y1 in PDF coords)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = get_logger()
        self.main_window = parent  # Reference to main window
        self.pdf_document = None
        self.current_page = 0
        self.zoom_level = 1.0
        self.total_pages = 0
        self.edit_mode_active = False
        self.text_box = None
        self.view_mode = "single"  # "single" or "continuous"
        self.page_rotation = 0  # 0, 90, 180, 270 degrees

        # Edit text mode (Adobe-like)
        self.edit_text_mode = False
        self.text_blocks = []  # List of text blocks with bounding boxes
        self.selected_text_block = None  # Currently selected text block
        self.text_edit_box = None  # Editable text box for editing
        self.pending_edits = []  # List of pending edits to apply when saving
        self.temp_pdf_document = None  # Temporary PDF with live edits
        self.original_pdf_path = None  # Path to original PDF for reset

        # Enable keyboard focus for shortcuts
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self._setup_ui()

    def _setup_ui(self):
        """Setup PDF viewer UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Navigation toolbar
        self.nav_toolbar = self._create_navigation_toolbar()
        layout.addWidget(self.nav_toolbar)

        # Scroll area for PDF content
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(False)  # Important: False for fixed-size content like PDFs
        self.scroll_area.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # Ensure no padding or margins on scroll area
        self.scroll_area.setStyleSheet("QScrollArea { border: none; padding: 0px; margin: 0px; }")

        # Interactive PDF display label with modern styling
        self.pdf_label = InteractivePDFLabel()
        self.pdf_label.setText("No PDF loaded")
        self.pdf_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pdf_label.setStyleSheet(f"""
            QLabel {{
                background-color: #E8EAF6;
                color: {ModernTheme.TEXT_SECONDARY};
                font-size: 18px;
                font-weight: 500;
                padding: 40px;
                border-radius: 12px;
            }}
        """)

        # Connect click signals
        self.pdf_label.pdf_clicked.connect(self._on_pdf_clicked)
        self.pdf_label.text_block_clicked.connect(self._on_text_block_clicked)
        self.pdf_label.area_selected.connect(self._on_area_selected)

        self.scroll_area.setWidget(self.pdf_label)
        layout.addWidget(self.scroll_area)

        # Create floating text box (hidden by default)
        # Parent is pdf_label so it positions correctly relative to click position
        self.text_box = EditableTextBox(self.pdf_label)
        self.text_box.hide()
        self.text_box.editing_finished.connect(self._on_text_editing_finished)
        self.text_box.editing_cancelled.connect(self._on_text_editing_cancelled)

    def _create_navigation_toolbar(self) -> QToolBar:
        """Create modern navigation toolbar"""
        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(20, 20))
        toolbar.setStyleSheet(f"""
            QToolBar {{
                background-color: {ModernTheme.SURFACE};
                border-bottom: 2px solid {ModernTheme.BORDER};
                spacing: 4px;
                padding: 6px;
            }}
        """)

        # Previous page button with modern styling
        self.prev_btn = QPushButton("◄ Previous")
        self.prev_btn.setEnabled(False)
        self.prev_btn.clicked.connect(self.previous_page)
        self.prev_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {ModernTheme.PRIMARY};
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 6px;
                font-size: 12px;
                font-weight: 500;
                min-width: 80px;
            }}
            QPushButton:hover {{
                background-color: {ModernTheme.PRIMARY_DARK};
            }}
            QPushButton:disabled {{
                background-color: {ModernTheme.BORDER};
                color: {ModernTheme.TEXT_DISABLED};
            }}
        """)
        toolbar.addWidget(self.prev_btn)

        # Page info with modern styling
        self.page_info = QLabel("Page: 0 / 0")
        self.page_info.setStyleSheet(f"""
            QLabel {{
                padding: 0 16px;
                font-weight: 600;
                font-size: 14px;
                color: {ModernTheme.TEXT_PRIMARY};
            }}
        """)
        toolbar.addWidget(self.page_info)

        # Next page button with modern styling
        self.next_btn = QPushButton("Next ►")
        self.next_btn.setEnabled(False)
        self.next_btn.clicked.connect(self.next_page)
        self.next_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {ModernTheme.PRIMARY};
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 6px;
                font-size: 12px;
                font-weight: 500;
                min-width: 80px;
            }}
            QPushButton:hover {{
                background-color: {ModernTheme.PRIMARY_DARK};
            }}
            QPushButton:disabled {{
                background-color: {ModernTheme.BORDER};
                color: {ModernTheme.TEXT_DISABLED};
            }}
        """)
        toolbar.addWidget(self.next_btn)

        toolbar.addSeparator()

        # Zoom out button
        self.zoom_out_btn = QPushButton("−")
        self.zoom_out_btn.setFixedWidth(40)
        self.zoom_out_btn.clicked.connect(self.zoom_out)
        self.zoom_out_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {ModernTheme.SECONDARY};
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 18px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {ModernTheme.SECONDARY_DARK};
            }}
        """)
        toolbar.addWidget(self.zoom_out_btn)

        # Zoom combo box
        self.zoom_combo = QComboBox()
        self.zoom_combo.addItems(["50%", "75%", "100%", "125%", "150%", "200%", "Fit Page", "Fit Width"])
        self.zoom_combo.setCurrentText("Fit Width")
        self.zoom_combo.currentTextChanged.connect(self.on_zoom_changed)
        self.zoom_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {ModernTheme.SURFACE};
                border: 2px solid {ModernTheme.BORDER};
                border-radius: 6px;
                padding: 4px 8px;
                min-width: 85px;
                max-width: 95px;
                font-size: 12px;
                font-weight: 500;
            }}
            QComboBox:hover {{
                border-color: {ModernTheme.PRIMARY};
            }}
            QComboBox::drop-down {{
                border: none;
            }}
        """)
        toolbar.addWidget(self.zoom_combo)

        # Zoom in button
        self.zoom_in_btn = QPushButton("+")
        self.zoom_in_btn.setFixedWidth(40)
        self.zoom_in_btn.clicked.connect(self.zoom_in)
        self.zoom_in_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {ModernTheme.SECONDARY};
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 18px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {ModernTheme.SECONDARY_DARK};
            }}
        """)
        toolbar.addWidget(self.zoom_in_btn)

        toolbar.addSeparator()

        # Rotate counter-clockwise button
        self.rotate_ccw_btn = QPushButton("↺")
        self.rotate_ccw_btn.setFixedWidth(35)
        self.rotate_ccw_btn.setToolTip("Rotate counter-clockwise")
        self.rotate_ccw_btn.clicked.connect(self.rotate_ccw)
        self.rotate_ccw_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {ModernTheme.SURFACE};
                color: {ModernTheme.TEXT_PRIMARY};
                border: 1px solid {ModernTheme.BORDER};
                border-radius: 4px;
                font-size: 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {ModernTheme.BORDER};
            }}
        """)
        toolbar.addWidget(self.rotate_ccw_btn)

        # Rotate clockwise button
        self.rotate_cw_btn = QPushButton("↻")
        self.rotate_cw_btn.setFixedWidth(35)
        self.rotate_cw_btn.setToolTip("Rotate clockwise")
        self.rotate_cw_btn.clicked.connect(self.rotate_cw)
        self.rotate_cw_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {ModernTheme.SURFACE};
                color: {ModernTheme.TEXT_PRIMARY};
                border: 1px solid {ModernTheme.BORDER};
                border-radius: 4px;
                font-size: 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {ModernTheme.BORDER};
            }}
        """)
        toolbar.addWidget(self.rotate_cw_btn)

        toolbar.addSeparator()

        # View mode selector
        self.view_mode_combo = QComboBox()
        self.view_mode_combo.addItems(["Single Page", "Continuous"])
        self.view_mode_combo.setCurrentText("Single Page")
        self.view_mode_combo.currentTextChanged.connect(self.on_view_mode_changed)
        self.view_mode_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {ModernTheme.SURFACE};
                border: 1px solid {ModernTheme.BORDER};
                border-radius: 4px;
                padding: 4px 8px;
                min-width: 90px;
                font-size: 11px;
            }}
            QComboBox:hover {{
                border-color: {ModernTheme.PRIMARY};
            }}
        """)
        toolbar.addWidget(self.view_mode_combo)

        return toolbar

    def load_pdf(self, file_path: str):
        """Load PDF file"""
        try:
            self.logger.info(f"Loading PDF: {file_path}")

            # Open PDF with PyMuPDF
            self.pdf_document = fitz.open(file_path)

            # Check if PDF is password protected
            if self.pdf_document.needs_pass:
                self.logger.info("PDF is password protected, prompting for password")
                from PyQt6.QtWidgets import QInputDialog, QLineEdit
                max_attempts = 3
                authenticated = False

                for attempt in range(max_attempts):
                    password, ok = QInputDialog.getText(
                        self,
                        "Password Protected PDF",
                        f"This PDF is password protected.\nEnter password to open:"
                        + (f"\n(Attempt {attempt + 1} of {max_attempts})" if attempt > 0 else ""),
                        QLineEdit.EchoMode.Password
                    )

                    if not ok:
                        # User cancelled
                        self.pdf_document.close()
                        self.pdf_document = None
                        raise Exception("Password entry cancelled by user")

                    if self.pdf_document.authenticate(password):
                        authenticated = True
                        self.logger.info("PDF password authentication successful")
                        break
                    else:
                        self.logger.warning(f"Incorrect password attempt {attempt + 1}")
                        if attempt < max_attempts - 1:
                            from PyQt6.QtWidgets import QMessageBox
                            QMessageBox.warning(
                                self,
                                "Incorrect Password",
                                f"The password is incorrect. {max_attempts - attempt - 1} attempt(s) remaining."
                            )

                if not authenticated:
                    self.pdf_document.close()
                    self.pdf_document = None
                    raise Exception("Failed to authenticate PDF after 3 attempts")

            self.total_pages = len(self.pdf_document)
            self.current_page = 0

            # Enable navigation
            self.prev_btn.setEnabled(True)
            self.next_btn.setEnabled(True)

            # Automatically fit to width for better viewing
            self.fit_width()

            self.logger.info(f"PDF loaded successfully: {self.total_pages} pages")

        except Exception as e:
            self.logger.error(f"Error loading PDF: {e}")
            self.pdf_label.setText(f"Error loading PDF:\n{str(e)}")
            raise

    def render_current_page(self):
        """Render current page to display"""
        if not self.pdf_document:
            return

        try:
            # Get current page
            page = self.pdf_document[self.current_page]

            # Calculate zoom matrix with rotation
            zoom_matrix = fitz.Matrix(self.zoom_level, self.zoom_level)
            if self.page_rotation != 0:
                zoom_matrix = zoom_matrix.prerotate(self.page_rotation)

            # Render page to pixmap
            pix = page.get_pixmap(matrix=zoom_matrix, alpha=False)

            # Convert to QImage
            img_format = QImage.Format.Format_RGB888
            qimage = QImage(pix.samples, pix.width, pix.height,
                          pix.stride, img_format)

            # Display in label
            pixmap = QPixmap.fromImage(qimage)
            self.pdf_label.setPixmap(pixmap)
            self.pdf_label.setFixedSize(pixmap.size())

            # Remove padding/styling when displaying PDF
            self.pdf_label.setStyleSheet("QLabel { padding: 0px; margin: 0px; border: none; }")

            # Update page info
            self.page_info.setText(f"Page: {self.current_page + 1} / {self.total_pages}")

            # Update navigation buttons
            self.prev_btn.setEnabled(self.current_page > 0)
            self.next_btn.setEnabled(self.current_page < self.total_pages - 1)

            # Update zoom level in interactive label
            self.pdf_label.zoom_level = self.zoom_level

            # Emit signal
            self.page_changed.emit(self.current_page + 1)

        except Exception as e:
            self.logger.error(f"Error rendering page: {e}")
            self.pdf_label.setText(f"Error rendering page: {str(e)}")

    def previous_page(self):
        """Go to previous page"""
        if self.current_page > 0:
            self.current_page -= 1
            self.render_current_page()

    def next_page(self):
        """Go to next page"""
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            self.render_current_page()

    def go_to_page(self, page_number: int):
        """Go to specific page"""
        if 0 <= page_number < self.total_pages:
            self.current_page = page_number
            self.render_current_page()

    def zoom_in(self):
        """Zoom in"""
        self.zoom_level = min(self.zoom_level + 0.25, 4.0)
        self._update_zoom_combo()
        self.render_current_page()
        self.zoom_changed.emit(self.zoom_level)

    def zoom_out(self):
        """Zoom out"""
        self.zoom_level = max(self.zoom_level - 0.25, 0.25)
        self._update_zoom_combo()
        self.render_current_page()
        self.zoom_changed.emit(self.zoom_level)

    def on_zoom_changed(self, zoom_text: str):
        """Handle zoom combo box change"""
        if zoom_text == "Fit Page":
            self.fit_page()
        elif zoom_text == "Fit Width":
            self.fit_width()
        else:
            try:
                # Extract percentage
                zoom_percent = int(zoom_text.rstrip('%'))
                self.zoom_level = zoom_percent / 100.0
                self.render_current_page()
                self.zoom_changed.emit(self.zoom_level)
            except ValueError:
                pass

    def fit_page(self):
        """Fit entire page in view"""
        if not self.pdf_document:
            return

        page = self.pdf_document[self.current_page]
        page_rect = page.rect

        # Get viewport dimensions
        viewport_width = self.scroll_area.viewport().width()
        viewport_height = self.scroll_area.viewport().height()

        # Calculate zoom ratios for width and height
        zoom_w = viewport_width / page_rect.width
        zoom_h = viewport_height / page_rect.height

        # Use the smaller zoom to ensure entire page fits
        # Apply 0.98 multiplier to account for potential scrollbar
        self.zoom_level = min(zoom_w, zoom_h) * 0.98
        self._update_zoom_combo()
        self.render_current_page()

    def fit_width(self):
        """Fit page width in view"""
        if not self.pdf_document:
            return

        page = self.pdf_document[self.current_page]
        page_rect = page.rect

        # Get the viewport width
        viewport_width = self.scroll_area.viewport().width()

        # According to PyMuPDF best practices:
        # zoom = viewport_width / page_width
        # Apply 0.95 multiplier to ensure content doesn't get cut off
        # (accounts for vertical scrollbar and any padding/margins)
        self.zoom_level = (viewport_width / page_rect.width) * 0.95

        self._update_zoom_combo()
        self.render_current_page()

    def _update_zoom_combo(self):
        """Update zoom combo box text"""
        zoom_percent = int(self.zoom_level * 100)
        # Only set if it's a valid combo box item
        zoom_text = f"{zoom_percent}%"
        if zoom_text in ["50%", "75%", "100%", "125%", "150%", "200%"]:
            self.zoom_combo.setCurrentText(zoom_text)
        # Otherwise leave it showing the last valid selection

    def rotate_cw(self):
        """Rotate page clockwise (90 degrees)"""
        self.page_rotation = (self.page_rotation + 90) % 360
        self.render_current_page()
        self.logger.info(f"Rotated page clockwise to {self.page_rotation} degrees")

    def rotate_ccw(self):
        """Rotate page counter-clockwise (90 degrees)"""
        self.page_rotation = (self.page_rotation - 90) % 360
        self.render_current_page()
        self.logger.info(f"Rotated page counter-clockwise to {self.page_rotation} degrees")

    def on_view_mode_changed(self, mode_text: str):
        """Handle view mode change"""
        if mode_text == "Single Page":
            self.view_mode = "single"
        elif mode_text == "Continuous":
            self.view_mode = "continuous"

        self.logger.info(f"View mode changed to: {self.view_mode}")
        if self.pdf_document:
            self.render_current_page()

    def close_pdf(self):
        """Close current PDF"""
        if self.pdf_document:
            self.pdf_document.close()
            self.pdf_document = None
            self.current_page = 0
            self.total_pages = 0
            self.page_rotation = 0  # Reset rotation
            self.pdf_label.setText("No PDF loaded")
            self.page_info.setText("Page: 0 / 0")

            # Restore styling for "No PDF loaded" state
            self.pdf_label.setStyleSheet(f"""
                QLabel {{
                    background-color: #E8EAF6;
                    color: {ModernTheme.TEXT_SECONDARY};
                    font-size: 18px;
                    font-weight: 500;
                    padding: 40px;
                    border-radius: 12px;
                }}
            """)

    def enable_edit_mode(self, mode_type: str = 'text', font_size: int = 12, text_width: int = 300):
        """Enable interactive edit mode"""
        self.edit_mode_active = True
        self.edit_mode_type = mode_type
        self.edit_font_size = font_size
        self.edit_text_width = text_width
        self.pdf_label.set_edit_mode(True, mode_type)
        self.logger.info(f"Edit mode enabled ({mode_type}) - Click on PDF to place cursor")

    def disable_edit_mode(self):
        """Disable interactive edit mode"""
        self.edit_mode_active = False
        self.pdf_label.set_edit_mode(False)
        if self.text_box:
            self.text_box.hide()
        self.logger.info("Edit mode disabled")

    def enable_redaction_mode(self):
        """Enable redaction mode for drawing redaction rectangles"""
        if not self.pdf_document:
            return False
        self.pdf_label.set_redaction_mode(True)
        self.logger.info("Redaction mode enabled - Draw rectangles to mark areas for redaction")
        return True

    def disable_redaction_mode(self):
        """Disable redaction mode"""
        self.pdf_label.set_redaction_mode(False)
        self.logger.info("Redaction mode disabled")

    def get_redaction_rects(self):
        """Get all redaction rectangles drawn by user"""
        return self.pdf_label.get_redaction_rects()

    def clear_redaction_rects(self):
        """Clear all redaction rectangles"""
        self.pdf_label.clear_redaction_rects()

    def enable_selection_mode(self, mode_type: str = 'text'):
        """Enable area selection mode for placing text/image/comment"""
        if not self.pdf_document:
            return False
        self.pdf_label.set_selection_mode(True, mode_type)
        self.logger.info(f"Selection mode enabled ({mode_type}) - Draw rectangle to select area")
        return True

    def disable_selection_mode(self):
        """Disable area selection mode"""
        self.pdf_label.set_selection_mode(False)
        self.logger.info("Selection mode disabled")

    def get_selection_rect(self):
        """Get the selected area in PDF coordinates"""
        return self.pdf_label.get_selection_rect()

    def clear_selection(self):
        """Clear the current selection"""
        self.pdf_label.clear_selection()

    def _on_area_selected(self, x0: float, y0: float, x1: float, y1: float):
        """Handle area selection event - forward signal"""
        self.logger.info(f"Area selected: ({x0:.2f}, {y0:.2f}) to ({x1:.2f}, {y1:.2f})")
        self.area_selected.emit(x0, y0, x1, y1)

    def apply_redactions(self):
        """Apply all drawn redactions to the current page"""
        if not self.pdf_document:
            return False, "No PDF document loaded"

        redaction_rects = self.get_redaction_rects()
        if not redaction_rects:
            return False, "No redaction areas marked"

        try:
            page = self.pdf_document[self.current_page]

            # Add redaction annotations for each rectangle
            for rect_tuple in redaction_rects:
                rect = fitz.Rect(rect_tuple)
                page.add_redact_annot(rect, fill=(0, 0, 0))  # Black fill for redaction

            # Apply all redactions
            page.apply_redactions()

            # Clear the rectangles and re-render
            self.clear_redaction_rects()
            self.render_current_page()

            self.logger.info(f"Applied {len(redaction_rects)} redactions to page {self.current_page + 1}")
            return True, f"Applied {len(redaction_rects)} redactions"

        except Exception as e:
            self.logger.error(f"Error applying redactions: {e}")
            return False, str(e)

    def _on_pdf_clicked(self, pdf_x: float, pdf_y: float, screen_x: int, screen_y: int):
        """Handle PDF click event"""
        self.logger.info(f"PDF clicked at position: PDF({pdf_x:.2f}, {pdf_y:.2f}) Screen({screen_x}, {screen_y})")

        if self.edit_mode_type == 'text':
            # Show text box at clicked position for text editing
            self.text_box.start_editing(screen_x, screen_y, pdf_x, pdf_y,
                                       self.edit_font_size, self.edit_text_width)
        else:
            # For image mode, just emit signal
            self.pdf_clicked.emit(pdf_x, pdf_y, screen_x, screen_y)

    def _on_text_editing_finished(self, text: str, pdf_x: float, pdf_y: float, font_size: int):
        """Handle text editing finished"""
        self.logger.info(f"Text editing finished: '{text}' at ({pdf_x:.2f}, {pdf_y:.2f})")
        self.text_added.emit(text, pdf_x, pdf_y, font_size)
        self.disable_edit_mode()

    def _on_text_editing_cancelled(self):
        """Handle text editing cancelled"""
        self.logger.info("Text editing cancelled")
        self.disable_edit_mode()

    def keyPressEvent(self, event):
        """Handle keyboard shortcuts like Adobe PDF"""
        from PyQt6.QtCore import Qt

        # Page navigation
        if event.key() == Qt.Key.Key_PageDown or event.key() == Qt.Key.Key_Down:
            self.next_page()
        elif event.key() == Qt.Key.Key_PageUp or event.key() == Qt.Key.Key_Up:
            self.previous_page()
        elif event.key() == Qt.Key.Key_Home:
            self.go_to_page(0)
        elif event.key() == Qt.Key.Key_End:
            self.go_to_page(self.total_pages - 1)

        # Zoom shortcuts
        elif event.key() == Qt.Key.Key_Plus or (event.modifiers() == Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_Equal):
            self.zoom_in()
        elif event.key() == Qt.Key.Key_Minus or (event.modifiers() == Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_Minus):
            self.zoom_out()
        elif event.modifiers() == Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_0:
            self.zoom_combo.setCurrentText("100%")

        # Rotation shortcuts
        elif event.modifiers() == Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_Left:
            self.rotate_ccw()
        elif event.modifiers() == Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_Right:
            self.rotate_cw()

        # Edit text mode - Escape to exit
        elif event.key() == Qt.Key.Key_Escape and self.edit_text_mode:
            self.disable_edit_text_mode()

        else:
            super().keyPressEvent(event)

    def enable_edit_text_mode(self):
        """Enable Adobe-like edit text mode"""
        if not self.pdf_document:
            return

        self.edit_text_mode = True
        self.pdf_label.set_edit_text_mode(True)

        # Store original PDF path and create working copy
        self.original_pdf_path = self.main_window.current_file
        # Create a fresh copy of the PDF for editing
        self.temp_pdf_document = fitz.open(self.original_pdf_path)

        # Extract text blocks from current page
        self._extract_text_blocks()

        self.logger.info("Edit text mode enabled - Click on any text to edit")

    def disable_edit_text_mode(self, force=False):
        """Disable edit text mode"""
        # Check for unsaved edits
        if self.pending_edits and not force:
            reply = QMessageBox.question(
                self.main_window,
                "Unsaved Edits",
                f"You have {len(self.pending_edits)} unsaved edit(s).\n\n"
                "Do you want to save them before exiting edit mode?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Yes
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.save_all_edits()
                return  # save_all_edits will disable edit mode after saving
            elif reply == QMessageBox.StandardButton.Cancel:
                return  # Don't exit edit mode

        self.edit_text_mode = False
        self.pdf_label.set_edit_text_mode(False)
        self.text_blocks = []
        self.selected_text_block = None
        self.pending_edits = []  # Clear pending edits

        # Close temp document if exists
        if self.temp_pdf_document:
            self.temp_pdf_document.close()
            self.temp_pdf_document = None

        # Reload original PDF if we discarded changes
        if self.original_pdf_path and not force:
            # Reload to discard unsaved changes
            self.main_window.load_pdf(self.original_pdf_path)

        self.original_pdf_path = None

        # Close any open text editor
        if self.text_edit_box:
            self.text_edit_box.hide()
            self.text_edit_box = None

        # Hide instructions label
        if hasattr(self, 'edit_instructions'):
            self.edit_instructions.hide()

        self.main_window.status_label.setText("Edit mode exited")
        self.logger.info("Edit text mode disabled")

    def _extract_text_blocks(self):
        """Extract text blocks from current page with bounding boxes"""
        if not self.pdf_document:
            return

        page = self.pdf_document[self.current_page]

        # Get text with detailed structure
        text_dict = page.get_text("dict")

        # Extract blocks
        self.text_blocks = []

        for block in text_dict["blocks"]:
            if block["type"] == 0:  # Text block
                # Get block bounding box
                bbox = block["bbox"]

                # Extract all text from block
                text_lines = []
                font_info = {}

                for line in block.get("lines", []):
                    line_text = ""
                    for span in line.get("spans", []):
                        line_text += span.get("text", "")
                        # Store font info from first span
                        if not font_info:
                            font_info = {
                                "font": span.get("font", "helv"),
                                "size": span.get("size", 12),
                                "color": span.get("color", 0)
                            }
                    text_lines.append(line_text)

                # Store block info
                self.text_blocks.append({
                    "bbox": bbox,
                    "text": "\n".join(text_lines),
                    "font_info": font_info,
                    "block_data": block
                })

        # Send to label for display
        self.pdf_label.set_text_blocks(self.text_blocks, self.zoom_level)

        self.logger.info(f"Extracted {len(self.text_blocks)} text blocks from page {self.current_page + 1}")

    def _on_text_block_clicked(self, block):
        """Handle text block click - show editor"""
        self.selected_text_block = block

        # Create or update text edit box using custom EditTextBox
        if not self.text_edit_box:
            self.text_edit_box = EditTextBox(self.scroll_area)
            self.text_edit_box.setStyleSheet(f"""
                QTextEdit {{
                    background-color: white;
                    border: 3px solid {ModernTheme.PRIMARY};
                    border-radius: 4px;
                    padding: 8px;
                    font-size: 12px;
                }}
            """)
            # Connect signals
            self.text_edit_box.save_requested.connect(self._save_edited_text)
            self.text_edit_box.cancel_requested.connect(self._cancel_edit)

        # Position text box at block location
        bbox = block['bbox']
        x = int(bbox[0] * self.zoom_level)
        y = int(bbox[1] * self.zoom_level)
        w = int((bbox[2] - bbox[0]) * self.zoom_level)
        h = int((bbox[3] - bbox[1]) * self.zoom_level)

        # Position relative to pdf_label
        label_pos = self.pdf_label.pos()
        self.text_edit_box.setGeometry(label_pos.x() + x, label_pos.y() + y, max(w, 200), max(h, 60))

        # Set current text
        self.text_edit_box.setPlainText(block['text'])

        # Set font
        font_info = block.get('font_info', {})
        font = QFont("Arial", int(font_info.get('size', 12)))
        self.text_edit_box.setFont(font)

        # Show and focus
        self.text_edit_box.show()
        self.text_edit_box.setFocus()
        self.text_edit_box.selectAll()

        # Add instructions label
        from PyQt6.QtWidgets import QLabel as QtLabel
        if not hasattr(self, 'edit_instructions'):
            self.edit_instructions = QtLabel(self.scroll_area)
            self.edit_instructions.setStyleSheet(f"""
                QLabel {{
                    background-color: {ModernTheme.PRIMARY};
                    color: white;
                    padding: 8px 12px;
                    border-radius: 4px;
                    font-size: 11px;
                    font-weight: bold;
                }}
            """)
            self.edit_instructions.setText("Ctrl+S = Queue Edit | Ctrl+Shift+S = Save All | Esc = Cancel")

        self.edit_instructions.adjustSize()
        self.edit_instructions.move(label_pos.x() + x, label_pos.y() + y - 35)
        self.edit_instructions.show()
        self.edit_instructions.raise_()

        self.logger.info(f"Editing text block: '{block['text'][:50]}...'")

    def _cancel_edit(self):
        """Cancel text editing"""
        self.logger.info("Edit cancelled")
        if self.text_edit_box:
            self.text_edit_box.hide()
        if hasattr(self, 'edit_instructions'):
            self.edit_instructions.hide()

    def _save_edited_text(self):
        """Apply edit immediately and show live preview - called when Ctrl+S is pressed"""
        self.logger.info("=== APPLYING EDIT WITH LIVE PREVIEW ===")

        if not self.text_edit_box or not self.selected_text_block:
            self.logger.warning("No text edit box or selected block")
            QMessageBox.warning(
                self.main_window,
                "Error",
                "No text is currently being edited."
            )
            return

        new_text = self.text_edit_box.toPlainText()
        old_text = self.selected_text_block['text']

        self.logger.info(f"Old text: {old_text[:100]}")
        self.logger.info(f"New text: {new_text[:100]}")

        if new_text == old_text:
            self.logger.info("Text unchanged, hiding editor")
            self.text_edit_box.hide()
            if hasattr(self, 'edit_instructions'):
                self.edit_instructions.hide()
            return

        # Store the edit info
        edit = {
            'page': self.current_page,
            'bbox': self.selected_text_block['bbox'],
            'old_text': old_text,
            'new_text': new_text,
            'font_info': self.selected_text_block.get('font_info', {})
        }

        # Check if this block was already edited - replace instead of duplicate
        existing_index = None
        for i, existing_edit in enumerate(self.pending_edits):
            if existing_edit['page'] == edit['page'] and existing_edit['bbox'] == edit['bbox']:
                existing_index = i
                break

        if existing_index is not None:
            self.pending_edits[existing_index] = edit
            self.logger.info(f"Updated existing edit at index {existing_index}")
        else:
            self.pending_edits.append(edit)
            self.logger.info(f"Edit added. Total pending edits: {len(self.pending_edits)}")

        # Apply edit to temp document immediately for live preview
        self._apply_single_edit_to_temp(edit)

        # Hide editor
        self.text_edit_box.hide()
        if hasattr(self, 'edit_instructions'):
            self.edit_instructions.hide()

        # Re-render the page to show the change immediately
        self._render_from_temp_document()

        # Update status bar
        self.main_window.status_label.setText(
            f"Edit applied ({len(self.pending_edits)} changes). Click more text to edit, or Ctrl+Shift+S to save PDF."
        )

        # Re-extract text blocks from the modified document
        self._extract_text_blocks_from_temp()

    def _apply_single_edit_to_temp(self, edit):
        """Apply a single edit using text search and replace for better formatting preservation"""
        if not self.temp_pdf_document:
            return

        page = self.temp_pdf_document[edit['page']]
        old_text = edit['old_text']
        new_text = edit['new_text']
        font_info = edit.get('font_info', {})

        # Get font properties
        font_size = font_info.get('size', 12)
        font_size = max(6, min(72, font_size))
        font_name = font_info.get('font', 'helv')
        # Normalize font name for PyMuPDF
        if 'arial' in font_name.lower():
            font_name = 'helv'
        elif 'times' in font_name.lower():
            font_name = 'tiro'
        elif 'courier' in font_name.lower():
            font_name = 'cour'
        else:
            font_name = 'helv'

        self.logger.info(f"Applying edit: '{old_text[:30]}...' -> '{new_text[:30]}...' with font {font_name}, size {font_size}")

        # Try text search and replace approach first (works better for simple edits)
        # Compare old and new text to find the specific change
        if old_text.strip() and new_text.strip():
            # Find what changed between old and new text
            old_lines = old_text.split('\n')
            new_lines = new_text.split('\n')

            # Process line by line for multi-line text
            if len(old_lines) == len(new_lines):
                for i, (old_line, new_line) in enumerate(zip(old_lines, new_lines)):
                    if old_line.strip() != new_line.strip():
                        # This line changed - find and replace it
                        self._replace_text_line(page, old_line.strip(), new_line.strip(), font_name, font_size)
                self.logger.info("Applied line-by-line replacement")
                return

        # Fallback: If text structure changed significantly, use the original approach
        # but try to be more precise by searching for the text first
        search_results = page.search_for(old_text.strip())
        if search_results:
            # Found the exact text - use precise replacement
            for rect in search_results:
                page.add_redact_annot(rect, fill=(1, 1, 1))
            page.apply_redactions()

            # Insert new text at the first found location
            if search_results:
                rect = search_results[0]
                baseline_y = rect.y0 + (font_size * 0.85)
                page.insert_text(
                    (rect.x0, baseline_y),
                    new_text.replace('\n', ' '),  # Flatten for single insertion
                    fontsize=font_size,
                    fontname=font_name,
                    color=(0, 0, 0)
                )
            self.logger.info(f"Applied text search replacement at {len(search_results)} locations")
        else:
            # Text not found as-is, use bounding box approach
            bbox = edit['bbox']
            rect = fitz.Rect(bbox)
            page.add_redact_annot(rect, fill=(1, 1, 1))
            page.apply_redactions()

            if '\n' in new_text:
                # Multi-line: insert each line separately
                lines = new_text.split('\n')
                y_pos = rect.y0 + font_size
                line_height = font_size * 1.2
                for line in lines:
                    if line.strip() and y_pos < rect.y1 + 50:  # Allow some overflow
                        page.insert_text(
                            (rect.x0, y_pos),
                            line,
                            fontsize=font_size,
                            fontname=font_name,
                            color=(0, 0, 0)
                        )
                        y_pos += line_height
            else:
                baseline_y = rect.y0 + (font_size * 0.85)
                page.insert_text(
                    (rect.x0, baseline_y),
                    new_text,
                    fontsize=font_size,
                    fontname=font_name,
                    color=(0, 0, 0)
                )
            self.logger.info(f"Applied bounding box replacement")

    def _replace_text_line(self, page, old_line, new_line, font_name, font_size):
        """Replace a single line of text while preserving position"""
        if not old_line or old_line == new_line:
            return

        # Search for the old text
        search_results = page.search_for(old_line)
        if search_results:
            for rect in search_results:
                # Redact the old text
                page.add_redact_annot(rect, fill=(1, 1, 1))
            page.apply_redactions()

            # Insert new text at the same position
            if search_results:
                rect = search_results[0]
                baseline_y = rect.y0 + (font_size * 0.85)
                page.insert_text(
                    (rect.x0, baseline_y),
                    new_line,
                    fontsize=font_size,
                    fontname=font_name,
                    color=(0, 0, 0)
                )
                self.logger.info(f"Replaced line: '{old_line[:20]}...' -> '{new_line[:20]}...'")
            self.logger.info(f"Inserted text at ({rect.x0}, {baseline_y})")

    def _render_from_temp_document(self):
        """Render the current page from the temporary edited document"""
        if not self.temp_pdf_document:
            return

        page = self.temp_pdf_document[self.current_page]

        # Apply rotation
        rotation_matrix = fitz.Matrix(1, 1).prerotate(self.page_rotation)
        zoom_matrix = fitz.Matrix(self.zoom_level, self.zoom_level)
        matrix = zoom_matrix * rotation_matrix

        # Render page
        pix = page.get_pixmap(matrix=matrix)

        # Convert to QImage
        img = QImage(pix.samples, pix.width, pix.height,
                     pix.stride, QImage.Format.Format_RGB888)

        # Update display
        pixmap = QPixmap.fromImage(img)
        self.pdf_label.setPixmap(pixmap)
        self.pdf_label.setFixedSize(pixmap.size())

        self.logger.info(f"Rendered page {self.current_page + 1} from temp document")

    def _extract_text_blocks_from_temp(self):
        """Extract text blocks from the temporary edited document"""
        if not self.temp_pdf_document:
            return

        page = self.temp_pdf_document[self.current_page]
        text_dict = page.get_text("dict")

        self.text_blocks = []

        for block in text_dict["blocks"]:
            if block["type"] == 0:  # Text block
                bbox = block["bbox"]
                text_lines = []
                font_info = {}

                for line in block.get("lines", []):
                    line_text = ""
                    for span in line.get("spans", []):
                        line_text += span.get("text", "")
                        if not font_info:
                            font_info = {
                                "font": span.get("font", "helv"),
                                "size": span.get("size", 12),
                                "color": span.get("color", 0)
                            }
                    text_lines.append(line_text)

                self.text_blocks.append({
                    "bbox": bbox,
                    "text": "\n".join(text_lines),
                    "font_info": font_info,
                    "block_data": block
                })

        self.pdf_label.set_text_blocks(self.text_blocks, self.zoom_level)
        self.logger.info(f"Extracted {len(self.text_blocks)} text blocks from temp document")

    def show_find_replace_dialog(self):
        """Show the Find & Replace dialog for simple text editing"""
        if not self.pdf_document:
            QMessageBox.warning(
                self.main_window,
                "No PDF",
                "Please open a PDF file first."
            )
            return

        # Create and show the dialog
        if not hasattr(self, 'find_replace_dialog') or self.find_replace_dialog is None:
            self.find_replace_dialog = FindReplaceDialog(self.main_window, self)

        self.find_replace_dialog.show()
        self.find_replace_dialog.raise_()
        self.find_replace_dialog.find_input.setFocus()

        self.logger.info("Find & Replace dialog opened")

    def save_all_edits(self):
        """Save the edited PDF (edits are already applied to temp document)"""
        import os

        if not self.pending_edits or not self.temp_pdf_document:
            QMessageBox.information(
                self.main_window,
                "No Edits",
                "No edits to save. Make some changes first."
            )
            return

        self.logger.info(f"=== SAVING {len(self.pending_edits)} EDITS TO FILE ===")

        try:
            # Generate default output filename
            base_name = os.path.splitext(self.original_pdf_path)[0]
            default_output = f"{base_name}_edited.pdf"

            # Show save dialog
            self.logger.info("Showing save file dialog")
            output_file, _ = QFileDialog.getSaveFileName(
                self.main_window,
                "Save Edited PDF",
                default_output,
                "PDF Files (*.pdf)"
            )

            if output_file:
                self.logger.info(f"Saving to: {output_file}")
                # Save the temp document which already has all edits applied
                self.temp_pdf_document.save(output_file, garbage=4, deflate=True, clean=True)

                # Close temp document
                self.temp_pdf_document.close()
                self.temp_pdf_document = None

                # Clear pending edits
                self.pending_edits = []

                # Reload the saved PDF
                self.logger.info("Reloading PDF")
                self.main_window.load_pdf(output_file)

                QMessageBox.information(
                    self.main_window,
                    "Success",
                    f"All edits saved successfully!\n\nSaved to: {output_file}"
                )

                # Disable edit text mode
                self.disable_edit_text_mode(force=True)

                self.logger.info("All edits saved successfully")
            else:
                self.logger.warning("User cancelled save dialog")

        except Exception as e:
            self.logger.error(f"Error saving edits: {e}", exc_info=True)
            QMessageBox.critical(
                self.main_window,
                "Error",
                f"Failed to save edits:\n\n{str(e)}\n\nPlease check the logs for details."
            )
