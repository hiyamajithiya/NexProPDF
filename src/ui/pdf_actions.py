"""
PDF Actions Controller - Connects UI to backend operations
"""

from PyQt6.QtWidgets import (QFileDialog, QMessageBox, QProgressDialog, QInputDialog,
                             QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
                             QApplication)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from pathlib import Path
from typing import Optional, List
from src.utilities.logger import get_logger
from src.pdf_engine.pdf_core import PDFCore
from src.pdf_engine.pdf_creator import PDFCreator
from src.pdf_engine.pdf_merger import PDFMerger
from src.pdf_engine.pdf_forms import PDFForms
from src.pdf_engine.pdf_utilities import PDFUtilities
from src.pdf_engine.pdf_converter import PDFConverter
from src.security.pdf_security import PDFSecurity
from src.security.pdf_redaction import PDFRedaction
from src.security.pdf_signature import PDFSignature
from src.ui.dialogs import *


class PDFWorker(QThread):
    """Worker thread for PDF operations"""
    finished = pyqtSignal(bool, str)
    progress = pyqtSignal(int)

    def __init__(self, operation, *args, **kwargs):
        super().__init__()
        self.operation = operation
        self.args = args
        self.kwargs = kwargs

    def run(self):
        try:
            result = self.operation(*self.args, **self.kwargs)
            self.finished.emit(result, "Operation completed successfully")
        except Exception as e:
            self.finished.emit(False, str(e))


class PDFActions:
    """PDF operations controller"""

    def __init__(self, main_window):
        self.main_window = main_window
        self.logger = get_logger()

        # Initialize backends
        self.pdf_core = PDFCore()
        self.pdf_creator = PDFCreator()
        self.pdf_merger = PDFMerger()
        self.pdf_forms = PDFForms()
        self.pdf_utilities = PDFUtilities()
        self.pdf_security = PDFSecurity()
        self.pdf_redaction = PDFRedaction()
        self.pdf_signature = PDFSignature()
        self.pdf_converter = PDFConverter()

        self.current_pdf_document = None

    # File Operations
    def create_from_word(self):
        """Create PDF from Word document"""
        file_path, _ = QFileDialog.getOpenFileName(
            self.main_window,
            "Select Word Document",
            "",
            "Word Files (*.docx *.doc)"
        )

        if not file_path:
            return

        output_path, _ = QFileDialog.getSaveFileName(
            self.main_window,
            "Save PDF As",
            "",
            "PDF Files (*.pdf)"
        )

        if not output_path:
            return

        if self.pdf_creator.from_word(file_path, output_path):
            QMessageBox.information(
                self.main_window,
                "Success",
                f"PDF created successfully:\n{output_path}"
            )
            self.main_window.load_pdf(output_path)
        else:
            error_msg = self.pdf_creator.last_error or "Failed to create PDF from Word document"
            QMessageBox.critical(
                self.main_window,
                "Error",
                error_msg
            )

    def create_from_excel(self):
        """Create PDF from Excel spreadsheet"""
        file_path, _ = QFileDialog.getOpenFileName(
            self.main_window,
            "Select Excel Spreadsheet",
            "",
            "Excel Files (*.xlsx *.xls)"
        )

        if not file_path:
            return

        output_path, _ = QFileDialog.getSaveFileName(
            self.main_window,
            "Save PDF As",
            "",
            "PDF Files (*.pdf)"
        )

        if not output_path:
            return

        if self.pdf_creator.from_excel(file_path, output_path):
            QMessageBox.information(
                self.main_window,
                "Success",
                f"PDF created successfully:\n{output_path}"
            )
            self.main_window.load_pdf(output_path)
        else:
            error_msg = self.pdf_creator.last_error or "Failed to create PDF from Excel"
            QMessageBox.critical(
                self.main_window,
                "Error",
                error_msg
            )

    def create_from_powerpoint(self):
        """Create PDF from PowerPoint presentation"""
        file_path, _ = QFileDialog.getOpenFileName(
            self.main_window,
            "Select PowerPoint Presentation",
            "",
            "PowerPoint Files (*.pptx *.ppt)"
        )

        if not file_path:
            return

        output_path, _ = QFileDialog.getSaveFileName(
            self.main_window,
            "Save PDF As",
            "",
            "PDF Files (*.pdf)"
        )

        if not output_path:
            return

        if self.pdf_creator.from_powerpoint(file_path, output_path):
            QMessageBox.information(
                self.main_window,
                "Success",
                f"PDF created successfully:\n{output_path}"
            )
            self.main_window.load_pdf(output_path)
        else:
            error_msg = self.pdf_creator.last_error or "Failed to create PDF from PowerPoint"
            QMessageBox.critical(
                self.main_window,
                "Error",
                error_msg
            )

    def create_from_images(self):
        """Create PDF from images"""
        file_paths, _ = QFileDialog.getOpenFileNames(
            self.main_window,
            "Select Images",
            "",
            "Images (*.jpg *.jpeg *.png)"
        )

        if not file_paths:
            return

        output_path, _ = QFileDialog.getSaveFileName(
            self.main_window,
            "Save PDF As",
            "",
            "PDF Files (*.pdf)"
        )

        if not output_path:
            return

        if self.pdf_creator.from_images(file_paths, output_path):
            QMessageBox.information(
                self.main_window,
                "Success",
                f"PDF created from {len(file_paths)} images"
            )
            self.main_window.load_pdf(output_path)
        else:
            QMessageBox.critical(
                self.main_window,
                "Error",
                "Failed to create PDF from images"
            )

    def convert_to_word(self):
        """Convert PDF to Word document with options dialog"""
        # Check if a PDF is open, if not ask to select one
        pdf_file = self.main_window.current_file

        if not pdf_file:
            pdf_file, _ = QFileDialog.getOpenFileName(
                self.main_window,
                "Select PDF File to Convert",
                "",
                "PDF Files (*.pdf)"
            )

            if not pdf_file:
                return

        # Detect PDF type
        detected_type = self.pdf_converter.detect_pdf_type(pdf_file)

        # Check if Tesseract is available
        tesseract_available = self.pdf_converter.is_tesseract_available()
        available_languages = self.pdf_converter.get_available_ocr_languages() if tesseract_available else ['eng']

        # Show conversion options dialog
        dialog = ConvertToWordDialog(
            self.main_window,
            tesseract_available=tesseract_available,
            available_languages=available_languages,
            detected_type=detected_type
        )

        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        settings = dialog.get_settings()

        # Get output file location
        default_name = Path(pdf_file).stem + ".docx"
        default_path = str(Path(pdf_file).parent / default_name)

        output_file, _ = QFileDialog.getSaveFileName(
            self.main_window,
            "Save Word Document As",
            default_path,
            "Word Documents (*.docx)"
        )

        if not output_file:
            return

        # Show progress dialog
        progress = QProgressDialog(
            "Converting PDF to Word...",
            "Cancel",
            0, 100,
            self.main_window
        )
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.setWindowTitle("Converting")
        progress.setMinimumDuration(0)
        progress.setValue(5)
        QApplication.processEvents()

        try:
            # Define progress callback
            def update_progress(current, total):
                if total > 0:
                    percent = int((current / total) * 90) + 5
                    progress.setValue(min(percent, 99))
                    progress.setLabelText(f"Processing page {current + 1} of {total}...")
                    QApplication.processEvents()

            # Perform conversion based on selected mode
            mode = settings['mode']

            if mode == 'auto':
                success, message = self.pdf_converter.to_word_auto(
                    pdf_file, output_file,
                    include_images=settings['include_images'],
                    ocr_language=settings['ocr_language'],
                    progress_callback=update_progress
                )
            elif mode == 'text':
                success, message = self.pdf_converter.to_word_text_mode(
                    pdf_file, output_file,
                    include_images=settings['include_images'],
                    progress_callback=update_progress
                )
            elif mode == 'ocr':
                progress.setLabelText("Running OCR (this may take a while)...")
                QApplication.processEvents()
                success, message = self.pdf_converter.to_word_ocr_mode(
                    pdf_file, output_file,
                    language=settings['ocr_language'],
                    progress_callback=update_progress
                )
            else:
                success, message = self.pdf_converter.to_word_text_mode(
                    pdf_file, output_file,
                    include_images=settings['include_images'],
                    progress_callback=update_progress
                )

            progress.setValue(100)
            progress.close()

            if success:
                QMessageBox.information(
                    self.main_window,
                    "Success",
                    message
                )
            else:
                QMessageBox.critical(
                    self.main_window,
                    "Error",
                    message
                )

        except Exception as e:
            progress.close()
            QMessageBox.critical(
                self.main_window,
                "Error",
                f"Failed to convert PDF to Word:\n{str(e)}"
            )

    # Merge & Split
    def merge_pdfs(self):
        """Merge multiple PDFs"""
        dialog = MergeDialog(self.main_window)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            files = dialog.get_files()
            output_file = dialog.get_output_file()

            if self.pdf_merger.merge_pdfs(files, output_file):
                QMessageBox.information(
                    self.main_window,
                    "Success",
                    f"Merged {len(files)} PDFs successfully"
                )
                self.main_window.load_pdf(output_file)
            else:
                QMessageBox.critical(
                    self.main_window,
                    "Error",
                    "Failed to merge PDFs"
                )

    def split_pdf(self):
        """Split PDF"""
        if not self.main_window.current_file:
            QMessageBox.warning(
                self.main_window,
                "No PDF Open",
                "Please open a PDF file first"
            )
            return

        # Ask split method
        methods = ["By Page Range", "By Page Count", "By File Size"]
        method, ok = QInputDialog.getItem(
            self.main_window,
            "Split PDF",
            "Select split method:",
            methods,
            0,
            False
        )

        if not ok:
            return

        output_dir = QFileDialog.getExistingDirectory(
            self.main_window,
            "Select Output Directory"
        )

        if not output_dir:
            return

        input_file = self.main_window.current_file

        if method == "By Page Range":
            # Simple split: one page per file
            files = self.pdf_merger.split_by_pages(input_file, output_dir, 1)
        elif method == "By Page Count":
            count, ok = QInputDialog.getInt(
                self.main_window,
                "Pages Per File",
                "Pages per file:",
                1, 1, 1000
            )
            if ok:
                files = self.pdf_merger.split_by_pages(input_file, output_dir, count)
            else:
                return
        else:  # By File Size
            size, ok = QInputDialog.getDouble(
                self.main_window,
                "File Size",
                "Maximum size (MB):",
                5.0, 0.1, 100.0, 1
            )
            if ok:
                files = self.pdf_merger.split_by_size(input_file, output_dir, size)
            else:
                return

        if files:
            QMessageBox.information(
                self.main_window,
                "Success",
                f"Split into {len(files)} files"
            )
        else:
            QMessageBox.critical(
                self.main_window,
                "Error",
                "Failed to split PDF"
            )

    # Security Operations
    def set_password(self):
        """Set password protection"""
        if not self.main_window.current_file:
            QMessageBox.warning(
                self.main_window,
                "No PDF Open",
                "Please open a PDF file first"
            )
            return

        dialog = PasswordDialog(self.main_window)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            passwords = dialog.get_passwords()

            output_file, _ = QFileDialog.getSaveFileName(
                self.main_window,
                "Save Protected PDF As",
                "",
                "PDF Files (*.pdf)"
            )

            if not output_file:
                return

            if self.pdf_security.set_password(
                self.main_window.current_file,
                output_file,
                passwords['user_password'],
                passwords['owner_password']
            ):
                QMessageBox.information(
                    self.main_window,
                    "Success",
                    "Password protection applied"
                )
                self.main_window.load_pdf(output_file)
            else:
                QMessageBox.critical(
                    self.main_window,
                    "Error",
                    "Failed to set password"
                )

    def encrypt_pdf(self):
        """Encrypt PDF with passwords and permission control"""
        if not self.main_window.current_file:
            QMessageBox.warning(
                self.main_window,
                "No PDF Open",
                "Please open a PDF file first"
            )
            return

        dialog = EncryptDialog(self.main_window)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            settings = dialog.get_settings()

            output_file, _ = QFileDialog.getSaveFileName(
                self.main_window,
                "Save Encrypted PDF As",
                "",
                "PDF Files (*.pdf)"
            )

            if not output_file:
                return

            if self.pdf_security.encrypt_pdf(
                self.main_window.current_file,
                output_file,
                settings['user_password'],
                settings['owner_password'],
                settings['permissions']
            ):
                QMessageBox.information(
                    self.main_window,
                    "Success",
                    "PDF encrypted successfully with AES-256"
                )
                self.main_window.load_pdf(output_file)
            else:
                QMessageBox.critical(
                    self.main_window,
                    "Error",
                    "Failed to encrypt PDF"
                )

    def set_permissions(self):
        """Set document permissions"""
        if not self.main_window.current_file:
            QMessageBox.warning(
                self.main_window,
                "No PDF Open",
                "Please open a PDF file first"
            )
            return

        dialog = PermissionsDialog(self.main_window)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            settings = dialog.get_permissions()

            output_file, _ = QFileDialog.getSaveFileName(
                self.main_window,
                "Save PDF As",
                "",
                "PDF Files (*.pdf)"
            )

            if not output_file:
                return

            permissions = {
                'print': settings['print'],
                'copy': settings['copy'],
                'modify': settings['modify'],
                'annotate': settings['annotate']
            }

            if self.pdf_security.set_permissions(
                self.main_window.current_file,
                output_file,
                permissions,
                settings['owner_password']
            ):
                QMessageBox.information(
                    self.main_window,
                    "Success",
                    "Permissions set successfully"
                )
                self.main_window.load_pdf(output_file)
            else:
                QMessageBox.critical(
                    self.main_window,
                    "Error",
                    "Failed to set permissions"
                )

    def add_watermark(self):
        """Add watermark"""
        if not self.main_window.current_file:
            QMessageBox.warning(
                self.main_window,
                "No PDF Open",
                "Please open a PDF file first"
            )
            return

        dialog = WatermarkDialog(self.main_window)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            settings = dialog.get_watermark_settings()

            output_file, _ = QFileDialog.getSaveFileName(
                self.main_window,
                "Save PDF As",
                "",
                "PDF Files (*.pdf)"
            )

            if not output_file:
                return

            if settings['type'] == 'text':
                success = self.pdf_security.add_watermark(
                    self.main_window.current_file,
                    output_file,
                    settings['text'],
                    settings['opacity'],
                    settings['font_size'],
                    (0.7, 0.7, 0.7),
                    settings['rotation']
                )
            else:
                success = self.pdf_security.add_image_watermark(
                    self.main_window.current_file,
                    output_file,
                    settings['image_path'],
                    settings['opacity'],
                    settings['position']
                )

            if success:
                QMessageBox.information(
                    self.main_window,
                    "Success",
                    "Watermark added successfully"
                )
                self.main_window.load_pdf(output_file)
            else:
                QMessageBox.critical(
                    self.main_window,
                    "Error",
                    "Failed to add watermark"
                )

    # Redaction Operations
    def redact_pan(self):
        """Redact PAN numbers"""
        self._redact_pattern("PAN", "PAN Numbers")

    def redact_aadhaar(self):
        """Redact Aadhaar numbers"""
        self._redact_pattern("AADHAAR", "Aadhaar Numbers")

    def redact_gstin(self):
        """Redact GSTIN numbers"""
        self._redact_pattern("GSTIN", "GSTIN Numbers")

    def redact_bank(self):
        """Redact bank account numbers"""
        self._redact_pattern("BANK_ACCOUNT", "Bank Account Numbers")

    def _redact_pattern(self, pattern_type: str, display_name: str):
        """Helper method for pattern-based redaction"""
        # If no file is open, allow user to select a PDF file directly
        input_file = self.main_window.current_file
        if not input_file:
            input_file, _ = QFileDialog.getOpenFileName(
                self.main_window,
                "Select PDF for Redaction",
                "",
                "PDF Files (*.pdf)"
            )
            if not input_file:
                return

        # Confirm
        reply = QMessageBox.question(
            self.main_window,
            "Confirm Redaction",
            f"This will permanently redact all {display_name}.\n\n"
            "This action CANNOT be undone!\n\n"
            "Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        # Open PDF
        import fitz
        pdf_doc = fitz.open(input_file)

        # Redact
        count = self.pdf_redaction.redact_pattern(pdf_doc, pattern_type)

        if count > 0:
            # Save
            output_file, _ = QFileDialog.getSaveFileName(
                self.main_window,
                "Save Redacted PDF As",
                "",
                "PDF Files (*.pdf)"
            )

            if output_file:
                pdf_doc.save(output_file)
                pdf_doc.close()

                QMessageBox.information(
                    self.main_window,
                    "Success",
                    f"Redacted {count} instances of {display_name}"
                )
                self.main_window.load_pdf(output_file)
        else:
            pdf_doc.close()
            QMessageBox.information(
                self.main_window,
                "No Matches",
                f"No {display_name} found in document"
            )

    # Utilities
    def add_bates_numbering(self):
        """Add Bates numbering"""
        if not self.main_window.current_file:
            QMessageBox.warning(
                self.main_window,
                "No PDF Open",
                "Please open a PDF file first"
            )
            return

        dialog = BatesNumberingDialog(self.main_window)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            settings = dialog.get_settings()

            import fitz
            pdf_doc = fitz.open(self.main_window.current_file)

            if self.pdf_utilities.add_bates_numbering(
                pdf_doc,
                settings['prefix'],
                settings['suffix'],
                settings['start_number'],
                settings['digits'],
                settings['position'],
                settings['font_size']
            ):
                output_file, _ = QFileDialog.getSaveFileName(
                    self.main_window,
                    "Save PDF As",
                    "",
                    "PDF Files (*.pdf)"
                )

                if output_file:
                    pdf_doc.save(output_file)
                    pdf_doc.close()

                    QMessageBox.information(
                        self.main_window,
                        "Success",
                        "Bates numbering added successfully"
                    )
                    self.main_window.load_pdf(output_file)
            else:
                pdf_doc.close()
                QMessageBox.critical(
                    self.main_window,
                    "Error",
                    "Failed to add Bates numbering"
                )

    # Edit Operations
    def edit_text(self):
        """Edit existing text in PDF using Find & Replace (simpler and more reliable)"""
        if not self.main_window.current_file:
            QMessageBox.warning(
                self.main_window,
                "No PDF Open",
                "Please open a PDF file first"
            )
            return

        # Open the Find & Replace dialog
        self.main_window.pdf_viewer.show_find_replace_dialog()
        self.main_window.status_label.setText("Find & Replace: Search for text and replace it")

    def edit_text_advanced(self):
        """Edit existing text in PDF (Adobe-like functionality with bounding boxes)"""
        if not self.main_window.current_file:
            QMessageBox.warning(
                self.main_window,
                "No PDF Open",
                "Please open a PDF file first"
            )
            return

        # Show instructions dialog
        msg = QMessageBox(self.main_window)
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setWindowTitle("Advanced Edit Text Mode")
        msg.setText("Advanced Edit Text Mode Activated")
        msg.setInformativeText(
            "<b>How to use:</b><br><br>"
            "1. Text blocks are highlighted with bounding boxes<br>"
            "2. Click on any text block to edit it<br>"
            "3. Make your changes in the text box<br>"
            "4. Press <b>Ctrl+S</b> to queue the edit (you can make more edits)<br>"
            "5. Edit more text blocks if needed<br>"
            "6. Press <b>Ctrl+Shift+S</b> or click 'Save Edits' to save all changes<br>"
            "7. Press <b>Esc</b> to exit edit mode<br><br>"
            "<i>Note: This mode may have issues if text doesn't fit the bounding box.<br>"
            "For simple changes, use 'Edit Text' (Find & Replace) instead.</i>"
        )
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()

        # Enable edit text mode in viewer
        self.main_window.pdf_viewer.enable_edit_text_mode()
        self.main_window.status_label.setText("Advanced Edit Mode: Click on any text block to edit...")

    def find_replace(self):
        """Open Find & Replace dialog for PDF text editing"""
        if not self.main_window.current_file:
            QMessageBox.warning(
                self.main_window,
                "No PDF Open",
                "Please open a PDF file first"
            )
            return

        # Open the Find & Replace dialog
        self.main_window.pdf_viewer.show_find_replace_dialog()
        self.main_window.status_label.setText("Find & Replace: Search for text and replace it")

    def save_all_edits(self):
        """Save all pending text edits to PDF"""
        if not self.main_window.current_file:
            QMessageBox.warning(
                self.main_window,
                "No PDF Open",
                "Please open a PDF file first"
            )
            return

        if not self.main_window.pdf_viewer.edit_text_mode:
            QMessageBox.information(
                self.main_window,
                "Not in Edit Mode",
                "Edit text mode is not active.\n\nUse 'Edit Text' button to start editing."
            )
            return

        # Call the pdf_viewer's save_all_edits method
        self.main_window.pdf_viewer.save_all_edits()

    def add_text(self):
        """Add text to PDF by selecting area first, then entering text"""
        if not self.main_window.current_file:
            QMessageBox.warning(
                self.main_window,
                "No PDF Open",
                "Please open a PDF file first"
            )
            return

        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QDialogButtonBox

        # Show instructions dialog
        dialog = QDialog(self.main_window)
        dialog.setWindowTitle("Add Text")
        layout = QVBoxLayout()

        instructions = QLabel(
            "<b>Instructions:</b><br><br>"
            "1. Click OK below<br>"
            "2. <b>Draw a rectangle</b> on the PDF where you want to add text<br>"
            "3. A text input dialog will appear<br>"
            "4. Enter your text and formatting options<br>"
            "5. Click Save to add the text"
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("padding: 15px; background-color: #E8F4F8; border: 1px solid #B3D9E6; border-radius: 5px; font-size: 13px;")
        layout.addWidget(instructions)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        dialog.setLayout(layout)
        dialog.setMinimumWidth(350)

        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        # Enable selection mode
        self.main_window.pdf_viewer.enable_selection_mode('text')

        # Connect to area_selected signal
        def on_area_selected(x0, y0, x1, y1):
            # Disconnect signal first
            try:
                self.main_window.pdf_viewer.area_selected.disconnect(on_area_selected)
            except:
                pass
            # Disable selection mode
            self.main_window.pdf_viewer.disable_selection_mode()
            # Show text input dialog
            self._show_text_input_dialog(x0, y0, x1, y1)

        self.main_window.pdf_viewer.area_selected.connect(on_area_selected)

        # Show status message
        self.main_window.status_label.setText("Draw a rectangle where you want to add text...")

    def _show_text_input_dialog(self, x0: float, y0: float, x1: float, y1: float):
        """Show dialog to enter text for the selected area"""
        from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                                     QSpinBox, QDialogButtonBox, QTextEdit, QComboBox)

        dialog = QDialog(self.main_window)
        dialog.setWindowTitle("Enter Text")
        dialog.setMinimumWidth(400)
        dialog.setMinimumHeight(300)
        layout = QVBoxLayout()

        # Text input
        layout.addWidget(QLabel("Enter your text:"))
        text_edit = QTextEdit()
        text_edit.setPlaceholderText("Type your text here...")
        text_edit.setMinimumHeight(100)
        layout.addWidget(text_edit)

        # Font size
        font_layout = QHBoxLayout()
        font_layout.addWidget(QLabel("Font Size:"))
        font_size_spin = QSpinBox()
        font_size_spin.setRange(6, 72)
        font_size_spin.setValue(12)
        font_layout.addWidget(font_size_spin)
        font_layout.addStretch()
        layout.addLayout(font_layout)

        # Text alignment
        align_layout = QHBoxLayout()
        align_layout.addWidget(QLabel("Alignment:"))
        align_combo = QComboBox()
        align_combo.addItems(["Left", "Center", "Right", "Justify"])
        align_layout.addWidget(align_combo)
        align_layout.addStretch()
        layout.addLayout(align_layout)

        # Area info
        area_info = QLabel(f"Selected area: ({int(x1-x0)} x {int(y1-y0)} points)")
        area_info.setStyleSheet("color: #666; font-size: 11px;")
        layout.addWidget(area_info)

        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        dialog.setLayout(layout)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            text = text_edit.toPlainText().strip()
            if text:
                font_size = font_size_spin.value()
                align_index = align_combo.currentIndex()  # 0=Left, 1=Center, 2=Right, 3=Justify
                self._save_text_to_area(text, x0, y0, x1, y1, font_size, align_index)
            else:
                self.main_window.status_label.setText("No text entered")
        else:
            self.main_window.status_label.setText("Text addition cancelled")

    def _save_text_to_area(self, text: str, x0: float, y0: float, x1: float, y1: float,
                           font_size: int, align: int = 0):
        """Save text to the selected area in PDF"""
        import fitz

        try:
            # Use the viewer's existing document to avoid resource conflicts
            pdf_doc = self.main_window.pdf_viewer.pdf_document
            if not pdf_doc:
                QMessageBox.warning(self.main_window, "Error", "No PDF document loaded")
                return

            current_page_num = self.main_window.pdf_viewer.current_page
            page = pdf_doc[current_page_num]

            # Create rectangle for text box
            rect = fitz.Rect(x0, y0, x1, y1)

            # Insert text with alignment
            page.insert_textbox(
                rect,
                text,
                fontsize=font_size,
                fontname="helv",
                color=(0, 0, 0),
                align=align  # 0=Left, 1=Center, 2=Right, 3=Justify
            )

            # Save to a new file (incremental save to same file not safe while open)
            output_file, _ = QFileDialog.getSaveFileName(
                self.main_window,
                "Save PDF As",
                self.main_window.current_file,
                "PDF Files (*.pdf)"
            )

            if output_file:
                pdf_doc.save(output_file, garbage=4, deflate=True, clean=True)
                QMessageBox.information(
                    self.main_window,
                    "Success",
                    "Text added successfully!"
                )
                # Reload the saved file
                self.main_window.load_pdf(output_file)
                self.main_window.status_label.setText("Text added successfully")
            else:
                # User cancelled - undo the text insertion by reloading
                current_file = self.main_window.current_file
                self.main_window.load_pdf(current_file)
                self.main_window.status_label.setText("Text addition cancelled")
        except Exception as e:
            self.main_window.status_label.setText(f"Error adding text: {e}")
            QMessageBox.critical(self.main_window, "Error", f"Failed to add text: {e}")

    def add_image(self):
        """Add image to PDF by selecting area first"""
        if not self.main_window.current_file:
            QMessageBox.warning(
                self.main_window,
                "No PDF Open",
                "Please open a PDF file first"
            )
            return

        # Select image first
        image_path, _ = QFileDialog.getOpenFileName(
            self.main_window,
            "Select Image",
            "",
            "Images (*.jpg *.jpeg *.png *.gif *.bmp)"
        )

        if not image_path:
            return

        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QDialogButtonBox

        # Show instructions dialog
        dialog = QDialog(self.main_window)
        dialog.setWindowTitle("Add Image")
        layout = QVBoxLayout()

        instructions = QLabel(
            f"<b>Selected Image:</b> {Path(image_path).name}<br><br>"
            "<b>Instructions:</b><br><br>"
            "1. Click OK below<br>"
            "2. <b>Draw a rectangle</b> on the PDF where you want to place the image<br>"
            "3. The image will be scaled to fit the selected area"
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("padding: 15px; background-color: #E8F4F8; border: 1px solid #B3D9E6; border-radius: 5px; font-size: 13px;")
        layout.addWidget(instructions)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        dialog.setLayout(layout)
        dialog.setMinimumWidth(400)

        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        # Store image path for when area is selected
        self._pending_image_path = image_path

        # Enable selection mode
        self.main_window.pdf_viewer.enable_selection_mode('image')

        # Connect to area_selected signal
        def on_area_selected(x0, y0, x1, y1):
            try:
                self.main_window.pdf_viewer.area_selected.disconnect(on_area_selected)
            except:
                pass
            self.main_window.pdf_viewer.disable_selection_mode()
            self._complete_add_image(x0, y0, x1, y1)

        self.main_window.pdf_viewer.area_selected.connect(on_area_selected)

        # Show status message
        self.main_window.status_label.setText("Draw a rectangle where you want to place the image...")

    def _complete_add_image(self, x0: float, y0: float, x1: float, y1: float):
        """Complete image addition in selected area"""
        if not hasattr(self, '_pending_image_path'):
            return

        image_path = self._pending_image_path
        delattr(self, '_pending_image_path')

        import fitz
        pdf_doc = fitz.open(self.main_window.current_file)

        # Get current page
        current_page_num = self.main_window.pdf_viewer.current_page
        page = pdf_doc[current_page_num]

        # Create image rectangle from selection
        rect = fitz.Rect(x0, y0, x1, y1)

        # Insert image (it will be scaled to fit the rectangle)
        page.insert_image(rect, filename=image_path)

        # Save
        output_file, _ = QFileDialog.getSaveFileName(
            self.main_window,
            "Save PDF As",
            "",
            "PDF Files (*.pdf)"
        )

        if output_file:
            pdf_doc.save(output_file)
            pdf_doc.close()
            QMessageBox.information(
                self.main_window,
                "Success",
                "Image added successfully!"
            )
            self.main_window.load_pdf(output_file)
            self.main_window.status_label.setText("Image added successfully")
        else:
            pdf_doc.close()
            self.main_window.status_label.setText("Save cancelled")

    # Page Operations
    def insert_pages(self):
        """Insert pages from another PDF"""
        if not self.main_window.current_file:
            QMessageBox.warning(
                self.main_window,
                "No PDF Open",
                "Please open a PDF file first"
            )
            return

        source_file, _ = QFileDialog.getOpenFileName(
            self.main_window,
            "Select PDF to Insert",
            "",
            "PDF Files (*.pdf)"
        )

        if not source_file:
            return

        position, ok = QInputDialog.getInt(
            self.main_window,
            "Insert Position",
            "Insert at page number:",
            1, 1, 9999
        )

        if not ok:
            return

        import fitz
        target_doc = fitz.open(self.main_window.current_file)
        source_doc = fitz.open(source_file)

        target_doc.insert_pdf(source_doc, start_at=position - 1)
        source_doc.close()

        output_file, _ = QFileDialog.getSaveFileName(
            self.main_window,
            "Save PDF As",
            "",
            "PDF Files (*.pdf)"
        )

        if output_file:
            target_doc.save(output_file)
            target_doc.close()
            QMessageBox.information(
                self.main_window,
                "Success",
                "Pages inserted successfully"
            )
            self.main_window.load_pdf(output_file)
        else:
            target_doc.close()

    def delete_pages(self):
        """Delete pages from PDF"""
        if not self.main_window.current_file:
            QMessageBox.warning(
                self.main_window,
                "No PDF Open",
                "Please open a PDF file first"
            )
            return

        import fitz
        pdf_doc = fitz.open(self.main_window.current_file)
        total_pages = len(pdf_doc)

        pages_str, ok = QInputDialog.getText(
            self.main_window,
            "Delete Pages",
            f"Enter pages to delete (e.g., 1,3,5 or 1-5):\nTotal pages: {total_pages}"
        )

        if not ok or not pages_str:
            pdf_doc.close()
            return

        # Parse page numbers
        pages_to_delete = []
        for part in pages_str.split(','):
            if '-' in part:
                start, end = map(int, part.split('-'))
                pages_to_delete.extend(range(start - 1, end))
            else:
                pages_to_delete.append(int(part) - 1)

        # Delete in reverse order
        for page_num in sorted(pages_to_delete, reverse=True):
            if 0 <= page_num < total_pages:
                pdf_doc.delete_page(page_num)

        output_file, _ = QFileDialog.getSaveFileName(
            self.main_window,
            "Save PDF As",
            "",
            "PDF Files (*.pdf)"
        )

        if output_file:
            pdf_doc.save(output_file)
            pdf_doc.close()
            QMessageBox.information(
                self.main_window,
                "Success",
                f"Deleted {len(pages_to_delete)} pages"
            )
            self.main_window.load_pdf(output_file)
        else:
            pdf_doc.close()

    def rotate_pages(self):
        """Rotate pages in PDF"""
        if not self.main_window.current_file:
            QMessageBox.warning(
                self.main_window,
                "No PDF Open",
                "Please open a PDF file first"
            )
            return

        angles = ["90", "180", "270"]
        angle, ok = QInputDialog.getItem(
            self.main_window,
            "Rotate Pages",
            "Select rotation angle:",
            angles,
            0,
            False
        )

        if not ok:
            return

        import fitz
        pdf_doc = fitz.open(self.main_window.current_file)

        for page in pdf_doc:
            page.set_rotation(int(angle))

        output_file, _ = QFileDialog.getSaveFileName(
            self.main_window,
            "Save PDF As",
            "",
            "PDF Files (*.pdf)"
        )

        if output_file:
            pdf_doc.save(output_file)
            pdf_doc.close()
            QMessageBox.information(
                self.main_window,
                "Success",
                f"Rotated all pages by {angle} degrees"
            )
            self.main_window.load_pdf(output_file)
        else:
            pdf_doc.close()

    def crop_pages(self):
        """Crop pages in PDF"""
        if not self.main_window.current_file:
            QMessageBox.warning(
                self.main_window,
                "No PDF Open",
                "Please open a PDF file first"
            )
            return

        # Get crop margins
        margin, ok = QInputDialog.getInt(
            self.main_window,
            "Crop Pages",
            "Enter margin to crop (in points):",
            50, 0, 200
        )

        if not ok:
            return

        import fitz
        pdf_doc = fitz.open(self.main_window.current_file)

        for page in pdf_doc:
            rect = page.rect
            new_rect = fitz.Rect(
                rect.x0 + margin,
                rect.y0 + margin,
                rect.x1 - margin,
                rect.y1 - margin
            )
            page.set_cropbox(new_rect)

        output_file, _ = QFileDialog.getSaveFileName(
            self.main_window,
            "Save PDF As",
            "",
            "PDF Files (*.pdf)"
        )

        if output_file:
            pdf_doc.save(output_file)
            pdf_doc.close()
            QMessageBox.information(
                self.main_window,
                "Success",
                "Pages cropped successfully"
            )
            self.main_window.load_pdf(output_file)
        else:
            pdf_doc.close()

    # Redaction Operations (additional)
    def manual_redaction(self):
        """Manual redaction - draw redaction boxes on PDF"""
        # If no file is open, allow user to select a PDF file directly
        input_file = self.main_window.current_file
        if not input_file:
            input_file, _ = QFileDialog.getOpenFileName(
                self.main_window,
                "Select PDF for Manual Redaction",
                "",
                "PDF Files (*.pdf)"
            )
            if not input_file:
                return
            # Load the selected PDF
            self.main_window.load_pdf(input_file)

        # Show instructions
        msg = QMessageBox(self.main_window)
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setWindowTitle("Manual Redaction Mode")
        msg.setText("Manual Redaction Mode Activated")
        msg.setInformativeText(
            "<b>How to use:</b><br><br>"
            "1. Click and drag on the PDF to draw redaction rectangles<br>"
            "2. Draw as many rectangles as needed<br>"
            "3. Click <b>'Apply Redactions'</b> button when done<br>"
            "4. Save the redacted PDF<br><br>"
            "<i>Note: Redactions are permanent once applied!</i>"
        )
        msg.setStandardButtons(QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)

        if msg.exec() != QMessageBox.StandardButton.Ok:
            return

        # Enable redaction mode in viewer
        if self.main_window.pdf_viewer.enable_redaction_mode():
            self.main_window.status_label.setText("Redaction Mode: Draw rectangles on the PDF, then click 'Apply Redactions'")

            # Show apply redaction button dialog
            self._show_redaction_toolbar()

    def _show_redaction_toolbar(self):
        """Show a floating toolbar for redaction operations"""
        from PyQt6.QtWidgets import QToolBar
        from PyQt6.QtGui import QAction

        # Create a dialog with Apply and Cancel buttons
        toolbar_dialog = QDialog(self.main_window)
        toolbar_dialog.setWindowTitle("Redaction Tools")
        toolbar_dialog.setModal(False)
        toolbar_dialog.setFixedSize(300, 100)

        layout = QVBoxLayout(toolbar_dialog)

        # Instructions
        label = QLabel("Draw rectangles on the PDF to mark areas for redaction")
        label.setWordWrap(True)
        layout.addWidget(label)

        # Buttons
        btn_layout = QHBoxLayout()

        apply_btn = QPushButton("Apply Redactions")
        apply_btn.setStyleSheet("""
            QPushButton {
                background-color: #DC3545;
                color: white;
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #C82333;
            }
        """)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet("""
            QPushButton {
                padding: 8px 16px;
                border: 1px solid #ccc;
                border-radius: 4px;
            }
        """)

        def apply_redactions():
            success, message = self.main_window.pdf_viewer.apply_redactions()
            if success:
                # Ask to save
                output_file, _ = QFileDialog.getSaveFileName(
                    self.main_window,
                    "Save Redacted PDF As",
                    "",
                    "PDF Files (*.pdf)"
                )
                if output_file:
                    self.main_window.pdf_viewer.pdf_document.save(output_file)
                    QMessageBox.information(
                        self.main_window,
                        "Success",
                        f"Redactions applied and saved successfully!\n\n{message}"
                    )
                    self.main_window.load_pdf(output_file)

                self.main_window.pdf_viewer.disable_redaction_mode()
                self.main_window.status_label.setText("Ready")
                toolbar_dialog.close()
            else:
                QMessageBox.warning(
                    self.main_window,
                    "Redaction",
                    message
                )

        def cancel_redaction():
            self.main_window.pdf_viewer.disable_redaction_mode()
            self.main_window.pdf_viewer.clear_redaction_rects()
            self.main_window.status_label.setText("Ready")
            toolbar_dialog.close()

        apply_btn.clicked.connect(apply_redactions)
        cancel_btn.clicked.connect(cancel_redaction)

        btn_layout.addWidget(apply_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

        # Position the dialog
        toolbar_dialog.move(
            self.main_window.x() + self.main_window.width() - 320,
            self.main_window.y() + 150
        )

        toolbar_dialog.show()

    def text_redaction(self):
        """Redact specific text"""
        # If no file is open, allow user to select a PDF file directly
        input_file = self.main_window.current_file
        if not input_file:
            input_file, _ = QFileDialog.getOpenFileName(
                self.main_window,
                "Select PDF for Text Redaction",
                "",
                "PDF Files (*.pdf)"
            )
            if not input_file:
                return

        text, ok = QInputDialog.getText(
            self.main_window,
            "Text Redaction",
            "Enter text to redact:"
        )

        if not ok or not text:
            return

        import fitz
        pdf_doc = fitz.open(input_file)

        count = self.pdf_redaction.redact_text(pdf_doc, text)

        if count > 0:
            output_file, _ = QFileDialog.getSaveFileName(
                self.main_window,
                "Save Redacted PDF As",
                "",
                "PDF Files (*.pdf)"
            )

            if output_file:
                pdf_doc.save(output_file)
                pdf_doc.close()
                QMessageBox.information(
                    self.main_window,
                    "Success",
                    f"Redacted {count} instances"
                )
                self.main_window.load_pdf(output_file)
            else:
                pdf_doc.close()
        else:
            pdf_doc.close()
            QMessageBox.information(
                self.main_window,
                "No Matches",
                f"Text '{text}' not found in document"
            )

    # Forms Operations
    def flatten_form(self):
        """Flatten form fields"""
        if not self.main_window.current_file:
            QMessageBox.warning(
                self.main_window,
                "No PDF Open",
                "Please open a PDF file first"
            )
            return

        import fitz
        pdf_doc = fitz.open(self.main_window.current_file)

        if self.pdf_forms.flatten_form(pdf_doc):
            output_file, _ = QFileDialog.getSaveFileName(
                self.main_window,
                "Save PDF As",
                "",
                "PDF Files (*.pdf)"
            )

            if output_file:
                pdf_doc.save(output_file)
                pdf_doc.close()
                QMessageBox.information(
                    self.main_window,
                    "Success",
                    "Form fields flattened successfully"
                )
                self.main_window.load_pdf(output_file)
            else:
                pdf_doc.close()
        else:
            pdf_doc.close()
            QMessageBox.information(
                self.main_window,
                "No Forms",
                "No form fields found in document"
            )

    def export_form_data(self):
        """Export form data to Excel"""
        if not self.main_window.current_file:
            QMessageBox.warning(
                self.main_window,
                "No PDF Open",
                "Please open a PDF file first"
            )
            return

        output_file, _ = QFileDialog.getSaveFileName(
            self.main_window,
            "Save Excel File As",
            "",
            "Excel Files (*.xlsx)"
        )

        if not output_file:
            return

        import fitz
        pdf_doc = fitz.open(self.main_window.current_file)

        if self.pdf_forms.export_to_excel(pdf_doc, output_file):
            pdf_doc.close()
            QMessageBox.information(
                self.main_window,
                "Success",
                f"Form data exported to:\n{output_file}"
            )
        else:
            pdf_doc.close()
            QMessageBox.warning(
                self.main_window,
                "No Data",
                "No form fields found to export"
            )

    # Signature Operations
    def add_signature(self):
        """Add digital signature using USB Token (DSC)"""
        if not self.main_window.current_file:
            QMessageBox.warning(
                self.main_window,
                "No PDF Open",
                "Please open a PDF file first"
            )
            return

        # Check if USB token signing is supported
        usb_supported, usb_message = self.pdf_signature.is_usb_token_supported()
        if not usb_supported:
            QMessageBox.warning(
                self.main_window,
                "USB Token Not Supported",
                f"USB Token signing is not available.\n\n{usb_message}"
            )
            return

        # Go directly to USB token signing
        self._sign_with_usb_token()

    def _sign_with_usb_token(self):
        """Sign PDF using USB Token (DSC) - detects token and shows certificate holder's name"""
        # Detect USB tokens
        self.main_window.statusBar().showMessage("Detecting USB tokens...")
        QApplication.processEvents()

        tokens = self.pdf_signature.detect_usb_tokens()

        if not tokens:
            msg = QMessageBox(self.main_window)
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setWindowTitle("No USB Token Detected")
            msg.setText("No USB Token (DSC) detected!")
            msg.setInformativeText(
                "<b>Please check:</b><br><br>"
                "1. USB Token is inserted in USB port<br>"
                "2. Token driver software is installed<br>"
                "3. Token LED is blinking/lit<br><br>"
                "<b>Supported tokens:</b><br>"
                "ePass2003, WatchData ProxKey, eMudhra<br><br>"
                "If problem persists, reinstall your token driver."
            )
            msg.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg.exec()
            self.main_window.statusBar().showMessage("Ready")
            return

        # Create signature dialog
        dialog = QDialog(self.main_window)
        dialog.setWindowTitle("Digital Signature - USB Token")
        dialog.setMinimumWidth(520)

        layout = QVBoxLayout(dialog)

        # Token selection with certificate holder name
        token_group = QLabel("<b>1. Select DSC Token:</b>")
        layout.addWidget(token_group)

        from PyQt6.QtWidgets import QComboBox
        token_combo = QComboBox()
        for token in tokens:
            # Show certificate holder's name (person's name) as primary
            display = token.get('display_name', token['label'])
            org = token.get('cert_org', '')
            if org:
                combo_text = f"{display}  ({org})"
            else:
                combo_text = f"{display}  ({token['manufacturer']})"
            token_combo.addItem(combo_text, token)
        layout.addWidget(token_combo)

        # Show certificate details for selected token
        cert_info_label = QLabel()
        cert_info_label.setStyleSheet(
            "color: #444; background: #f5f5f5; padding: 8px; "
            "border-radius: 4px; font-size: 11px;"
        )

        def update_cert_info(index):
            token = token_combo.itemData(index)
            if not token:
                return
            holder = token.get('cert_holder', '') or token['label']
            org = token.get('cert_org', '')
            issuer = token.get('cert_issuer', '')
            valid_until = token.get('cert_valid_until', '')
            info_lines = [f"<b>Certificate Holder:</b> {holder}"]
            if org:
                info_lines.append(f"<b>Organization:</b> {org}")
            if issuer:
                # Clean up issuer string for display
                issuer_short = issuer
                if 'CN=' in issuer:
                    import re
                    cn_match = re.search(r'CN=([^,>]+)', issuer)
                    if cn_match:
                        issuer_short = cn_match.group(1).strip()
                info_lines.append(f"<b>Issued by:</b> {issuer_short}")
            if valid_until:
                info_lines.append(f"<b>Valid until:</b> {valid_until[:10]}")
            cert_info_label.setText("<br>".join(info_lines))

        token_combo.currentIndexChanged.connect(update_cert_info)
        update_cert_info(0)  # Show info for first token
        layout.addWidget(cert_info_label)

        layout.addSpacing(5)

        # PIN entry
        pin_group = QLabel("<b>2. Enter Token PIN:</b>")
        layout.addWidget(pin_group)

        from PyQt6.QtWidgets import QLineEdit
        pin_input = QLineEdit()
        pin_input.setEchoMode(QLineEdit.EchoMode.Password)
        pin_input.setPlaceholderText("Enter your token PIN...")
        layout.addWidget(pin_input)

        # Signature details
        details_group = QLabel("<b>3. Signature Details:</b>")
        layout.addWidget(details_group)

        reason_input = QLineEdit()
        reason_input.setPlaceholderText("Reason for signing (e.g., Approved, Verified)")
        reason_input.setText("Digitally Signed")
        layout.addWidget(reason_input)

        location_input = QLineEdit()
        location_input.setPlaceholderText("Location")
        location_input.setText("India")
        layout.addWidget(location_input)

        # Visible signature option
        from PyQt6.QtWidgets import QCheckBox
        visible_check = QCheckBox("Add visible signature on PDF")
        visible_check.setChecked(True)
        layout.addWidget(visible_check)

        # Page selection for signature
        page_layout = QHBoxLayout()
        page_label = QLabel("Signature Page:")
        from PyQt6.QtWidgets import QSpinBox
        page_spin = QSpinBox()
        page_spin.setMinimum(1)
        page_spin.setMaximum(self.main_window.pdf_viewer.total_pages or 1)
        page_spin.setValue(self.main_window.pdf_viewer.current_page + 1)
        page_layout.addWidget(page_label)
        page_layout.addWidget(page_spin)
        page_layout.addStretch()
        layout.addLayout(page_layout)

        # Info label
        info_label = QLabel(
            "<i>After clicking 'Sign', draw a rectangle on the PDF to place your signature.<br>"
            "Your private key never leaves the USB token.</i>"
        )
        info_label.setStyleSheet("color: #666; padding: 8px;")
        layout.addWidget(info_label)

        # Buttons
        btn_layout = QHBoxLayout()
        sign_btn = QPushButton("Sign - Place Signature")
        sign_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 10px 30px;
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #45a049; }
        """)
        cancel_btn = QPushButton("Cancel")

        btn_layout.addStretch()
        btn_layout.addWidget(sign_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

        result = {"proceed": False}

        def on_sign():
            if not pin_input.text():
                QMessageBox.warning(dialog, "PIN Required", "Please enter your token PIN")
                return
            result["proceed"] = True
            dialog.accept()

        sign_btn.clicked.connect(on_sign)
        cancel_btn.clicked.connect(dialog.reject)

        self.main_window.statusBar().showMessage("Ready")

        if dialog.exec() != QDialog.DialogCode.Accepted or not result["proceed"]:
            return

        # Get selected token
        selected_token = token_combo.currentData()
        pin = pin_input.text()
        reason = reason_input.text() or "Digitally Signed"
        location = location_input.text() or "India"
        visible = visible_check.isChecked()
        sig_page = page_spin.value() - 1  # 0-indexed

        # Navigate to the signature page
        if sig_page != self.main_window.pdf_viewer.current_page:
            self.main_window.pdf_viewer.go_to_page(sig_page)
            QApplication.processEvents()

        # Let user draw signature placement rectangle
        sig_rect = None
        if visible:
            sig_rect = self._get_signature_placement()
            if sig_rect is None:
                self.main_window.statusBar().showMessage("Signature cancelled", 3000)
                return

        # Select output file
        output_file, _ = QFileDialog.getSaveFileName(
            self.main_window,
            "Save Signed PDF As",
            "",
            "PDF Files (*.pdf)"
        )

        if not output_file:
            return

        # Show progress
        signer_display = selected_token.get('display_name', selected_token['label'])
        self.main_window.statusBar().showMessage(f"Signing PDF as {signer_display}...")
        QApplication.processEvents()

        # Sign the PDF
        success, message = self.pdf_signature.sign_pdf_with_token(
            self.main_window.current_file,
            output_file,
            selected_token['dll_path'],
            selected_token['slot'],
            pin,
            token_label=selected_token['label'],
            reason=reason,
            location=location,
            visible_signature=visible,
            sig_page=sig_page,
            sig_rect=sig_rect
        )

        if success:
            self.main_window.statusBar().showMessage("PDF signed successfully!", 3000)
            QMessageBox.information(
                self.main_window,
                "Success",
                f"{message}\n\nSigner: {signer_display}\nOutput: {output_file}"
            )
            self.main_window.load_pdf(output_file)
        else:
            self.main_window.statusBar().showMessage("Signing failed", 3000)
            QMessageBox.critical(
                self.main_window,
                "Signing Failed",
                f"Failed to sign PDF.\n\n{message}"
            )

    def _get_signature_placement(self):
        """Let user draw a rectangle on PDF to place signature. Returns (x0, y0, x1, y1) or None."""
        from PyQt6.QtCore import QEventLoop

        # Show instruction
        self.main_window.statusBar().showMessage(
            "Draw a rectangle on the PDF where you want to place your signature. "
            "Press Escape to cancel."
        )

        # Enable selection mode on the PDF viewer
        viewer = self.main_window.pdf_viewer
        pdf_label = viewer.pdf_label
        pdf_label.set_selection_mode(True, 'signature')

        # Wait for selection
        result = {"rect": None, "cancelled": False}
        loop = QEventLoop()

        def on_area_selected(x0, y0, x1, y1):
            result["rect"] = (x0, y0, x1, y1)
            loop.quit()

        def on_key_press(event):
            if event.key() == Qt.Key.Key_Escape:
                result["cancelled"] = True
                loop.quit()

        # Connect signals
        viewer.area_selected.connect(on_area_selected)
        original_key_handler = viewer.keyPressEvent
        viewer.keyPressEvent = on_key_press

        # Run event loop until selection or cancel
        loop.exec()

        # Cleanup
        try:
            viewer.area_selected.disconnect(on_area_selected)
        except:
            pass
        viewer.keyPressEvent = original_key_handler
        pdf_label.set_selection_mode(False)
        pdf_label.clear_selection()

        self.main_window.statusBar().showMessage("Ready")

        if result["cancelled"] or result["rect"] is None:
            return None

        return result["rect"]

    def verify_signature(self):
        """Verify signatures in PDF"""
        if not self.main_window.current_file:
            QMessageBox.warning(
                self.main_window,
                "No PDF Open",
                "Please open a PDF file first"
            )
            return

        import fitz
        pdf_doc = fitz.open(self.main_window.current_file)

        signatures = self.pdf_signature.get_signature_info(pdf_doc)
        pdf_doc.close()

        if signatures:
            sig_info = "\n\n".join([
                f"Signature {i+1}:\n"
                f"  Signer: {sig.get('signer', 'Unknown')}\n"
                f"  Date: {sig.get('date', 'Unknown')}\n"
                f"  Valid: {sig.get('valid', False)}"
                for i, sig in enumerate(signatures)
            ])
            QMessageBox.information(
                self.main_window,
                "Signature Information",
                f"Found {len(signatures)} signature(s):\n\n{sig_info}"
            )
        else:
            QMessageBox.information(
                self.main_window,
                "No Signatures",
                "No digital signatures found in this document"
            )

    def manage_certificates(self):
        """Manage certificates - detect USB tokens and Windows certificates"""
        self.main_window.statusBar().showMessage("Detecting certificates and USB tokens...")
        QApplication.processEvents()

        # Detect USB tokens first
        tokens = self.pdf_signature.detect_usb_tokens()
        certs = self.pdf_signature.list_certificates_windows()

        self.main_window.statusBar().showMessage("Ready")

        if not tokens and not certs:
            msg = QMessageBox(self.main_window)
            msg.setIcon(QMessageBox.Icon.Information)
            msg.setWindowTitle("No Certificates Found")
            msg.setText("No digital certificates or USB tokens detected.")
            msg.setInformativeText(
                "<b>To use digital signatures:</b><br><br>"
                "1. <b>USB Token (Recommended for India):</b><br>"
                "   • Insert your ePass2003/Proxkey token<br>"
                "   • Install token driver software<br><br>"
                "2. <b>Windows Certificate Store:</b><br>"
                "   • Import certificate using certmgr.msc<br><br>"
                "<b>Required Python packages:</b><br>"
                "pip install PyKCS11 endesive"
            )
            msg.exec()
            return

        # Build info text
        info_parts = []

        if tokens:
            info_parts.append("=== USB TOKENS DETECTED ===\n")
            for i, token in enumerate(tokens, 1):
                holder = token.get('cert_holder', '') or token['label']
                org = token.get('cert_org', '')
                valid_until = token.get('cert_valid_until', '')
                info_parts.append(
                    f"Token {i}:\n"
                    f"  Certificate Holder: {holder}\n"
                    f"  Organization: {org or 'N/A'}\n"
                    f"  Token: {token['label']} ({token['manufacturer']})\n"
                    f"  Model: {token['model']}\n"
                    f"  Valid Until: {valid_until[:10] if valid_until else 'N/A'}\n"
                )

        if certs:
            info_parts.append("\n=== CERTIFICATES ===\n")
            for i, cert in enumerate(certs, 1):
                source = cert.get('source', 'Unknown')
                info_parts.append(
                    f"Certificate {i} ({source}):\n"
                    f"  Subject: {cert.get('subject', 'Unknown')}\n"
                    f"  Issuer: {cert.get('issuer', 'Unknown')}\n"
                    f"  Valid: {cert.get('is_valid', 'Unknown')}\n"
                )

        cert_info = "\n".join(info_parts)

        QMessageBox.information(
            self.main_window,
            "Installed Certificates",
            f"Found {len(certs)} certificate(s):\n\n{cert_info}"
        )

    # Tools Operations
    def add_page_numbers(self):
        """Add page numbers to PDF"""
        if not self.main_window.current_file:
            QMessageBox.warning(
                self.main_window,
                "No PDF Open",
                "Please open a PDF file first"
            )
            return

        positions = ["Bottom Center", "Bottom Right", "Bottom Left", "Top Center", "Top Right", "Top Left"]
        position, ok = QInputDialog.getItem(
            self.main_window,
            "Add Page Numbers",
            "Select position:",
            positions,
            0,
            False
        )

        if not ok:
            return

        import fitz
        pdf_doc = fitz.open(self.main_window.current_file)

        if self.pdf_utilities.add_page_numbers(pdf_doc, position.lower().replace(" ", "_")):
            output_file, _ = QFileDialog.getSaveFileName(
                self.main_window,
                "Save PDF As",
                "",
                "PDF Files (*.pdf)"
            )

            if output_file:
                pdf_doc.save(output_file)
                pdf_doc.close()
                QMessageBox.information(
                    self.main_window,
                    "Success",
                    "Page numbers added successfully"
                )
                self.main_window.load_pdf(output_file)
            else:
                pdf_doc.close()
        else:
            pdf_doc.close()
            QMessageBox.critical(
                self.main_window,
                "Error",
                "Failed to add page numbers"
            )

    def add_header_footer(self):
        """Add headers and footers"""
        if not self.main_window.current_file:
            QMessageBox.warning(
                self.main_window,
                "No PDF Open",
                "Please open a PDF file first"
            )
            return

        header_text, ok1 = QInputDialog.getText(
            self.main_window,
            "Header Text",
            "Enter header text (leave empty to skip):"
        )

        footer_text, ok2 = QInputDialog.getText(
            self.main_window,
            "Footer Text",
            "Enter footer text (leave empty to skip):"
        )

        if not (ok1 or ok2):
            return

        import fitz
        pdf_doc = fitz.open(self.main_window.current_file)

        if header_text:
            self.pdf_utilities.add_header(pdf_doc, header_text)

        if footer_text:
            self.pdf_utilities.add_footer(pdf_doc, footer_text)

        output_file, _ = QFileDialog.getSaveFileName(
            self.main_window,
            "Save PDF As",
            "",
            "PDF Files (*.pdf)"
        )

        if output_file:
            pdf_doc.save(output_file)
            pdf_doc.close()
            QMessageBox.information(
                self.main_window,
                "Success",
                "Header/Footer added successfully"
            )
            self.main_window.load_pdf(output_file)
        else:
            pdf_doc.close()

    def compress_pdf(self):
        """Compress PDF file with slider-based compression control (like 11zon)"""
        from PyQt6.QtWidgets import QSlider, QFrame, QGridLayout, QGroupBox
        from PyQt6.QtCore import Qt as QtCore_Qt

        # If no file is open, allow user to select a PDF file directly
        input_file = self.main_window.current_file
        if not input_file:
            input_file, _ = QFileDialog.getOpenFileName(
                self.main_window,
                "Select PDF to Compress",
                "",
                "PDF Files (*.pdf)"
            )
            if not input_file:
                return

        original_size = Path(input_file).stat().st_size

        # Create compression dialog
        dialog = QDialog(self.main_window)
        dialog.setWindowTitle("PDF Compression - Like 11zon")
        dialog.setFixedSize(500, 400)
        dialog.setStyleSheet("""
            QDialog {
                background-color: #f5f5f5;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #ddd;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)

        main_layout = QVBoxLayout(dialog)
        main_layout.setSpacing(15)

        # File info section
        file_info = QGroupBox("File Information")
        file_layout = QVBoxLayout(file_info)

        file_name = Path(input_file).name
        size_label = QLabel(f"<b>File:</b> {file_name}")
        original_size_label = QLabel(f"<b>Original Size:</b> {original_size / 1024:.1f} KB ({original_size / (1024*1024):.2f} MB)")
        file_layout.addWidget(size_label)
        file_layout.addWidget(original_size_label)
        main_layout.addWidget(file_info)

        # Compression control section
        compression_group = QGroupBox("Compression Level")
        compression_layout = QVBoxLayout(compression_group)

        # Quick preset buttons
        preset_layout = QHBoxLayout()
        preset_label = QLabel("Quick Presets:")
        preset_layout.addWidget(preset_label)

        preset_buttons = []
        presets = [
            ("Light", 30, "#4CAF50"),
            ("Medium", 50, "#2196F3"),
            ("High", 70, "#FF9800"),
            ("Maximum", 90, "#F44336")
        ]

        for name, value, color in presets:
            btn = QPushButton(name)
            btn.setFixedWidth(80)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: white;
                    padding: 8px;
                    border: none;
                    border-radius: 4px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    opacity: 0.8;
                }}
            """)
            preset_buttons.append((btn, value))
            preset_layout.addWidget(btn)

        preset_layout.addStretch()
        compression_layout.addLayout(preset_layout)

        # Slider with labels
        slider_layout = QVBoxLayout()

        # Slider value display
        slider_value_layout = QHBoxLayout()
        slider_value_layout.addWidget(QLabel("Compression:"))
        compression_value_label = QLabel("50%")
        compression_value_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #1E88E5;")
        slider_value_layout.addWidget(compression_value_label)
        slider_value_layout.addStretch()
        slider_layout.addLayout(slider_value_layout)

        # Slider
        compression_slider = QSlider(QtCore_Qt.Orientation.Horizontal)
        compression_slider.setMinimum(10)
        compression_slider.setMaximum(95)
        compression_slider.setValue(50)
        compression_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        compression_slider.setTickInterval(10)
        compression_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #bbb;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4CAF50, stop:0.33 #2196F3, stop:0.66 #FF9800, stop:1 #F44336);
                height: 10px;
                border-radius: 5px;
            }
            QSlider::handle:horizontal {
                background: white;
                border: 2px solid #1E88E5;
                width: 20px;
                margin: -6px 0;
                border-radius: 10px;
            }
            QSlider::handle:horizontal:hover {
                background: #E3F2FD;
            }
        """)
        slider_layout.addWidget(compression_slider)

        # Scale labels
        scale_layout = QHBoxLayout()
        scale_layout.addWidget(QLabel("10%"))
        scale_layout.addStretch()
        scale_layout.addWidget(QLabel("Better Quality"))
        scale_layout.addStretch()
        scale_layout.addWidget(QLabel("Smaller Size"))
        scale_layout.addStretch()
        scale_layout.addWidget(QLabel("95%"))
        slider_layout.addLayout(scale_layout)

        compression_layout.addLayout(slider_layout)

        # Estimated size display
        estimate_layout = QHBoxLayout()
        estimate_layout.addWidget(QLabel("Estimated Size:"))
        estimated_size_label = QLabel("~330 KB")
        estimated_size_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #4CAF50;")
        estimate_layout.addWidget(estimated_size_label)
        estimate_layout.addStretch()

        reduction_label = QLabel("(~50% reduction)")
        reduction_label.setStyleSheet("color: #666;")
        estimate_layout.addWidget(reduction_label)
        compression_layout.addLayout(estimate_layout)

        main_layout.addWidget(compression_group)

        # Quality note (dynamic)
        note_label = QLabel(
            "💡 <b>Tip:</b> Images in the PDF are re-encoded at lower quality. "
            "Text remains selectable up to 85%. Maximum (90%+) converts pages to images."
        )
        note_label.setWordWrap(True)
        note_label.setStyleSheet("padding: 10px; background-color: #E3F2FD; border-radius: 5px; color: #1565C0;")
        main_layout.addWidget(note_label)

        # Warning label for high compression
        warning_label = QLabel(
            "⚠️ <b>Warning:</b> Maximum compression (90%+) will convert pages to images. "
            "Text will NOT be selectable/searchable. Use for archival only."
        )
        warning_label.setWordWrap(True)
        warning_label.setStyleSheet("padding: 10px; background-color: #FFEBEE; border-radius: 5px; color: #C62828;")
        warning_label.setVisible(False)
        main_layout.addWidget(warning_label)

        main_layout.addStretch()

        # Buttons
        btn_layout = QHBoxLayout()

        compress_btn = QPushButton("🗜️ Compress PDF")
        compress_btn.setStyleSheet("""
            QPushButton {
                background-color: #1E88E5;
                color: white;
                padding: 12px 30px;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover { background-color: #1565C0; }
        """)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet("""
            QPushButton {
                padding: 12px 20px;
                border: 1px solid #ccc;
                border-radius: 6px;
                background-color: white;
            }
            QPushButton:hover { background-color: #f0f0f0; }
        """)

        btn_layout.addStretch()
        btn_layout.addWidget(compress_btn)
        btn_layout.addWidget(cancel_btn)
        main_layout.addLayout(btn_layout)

        # Update functions
        def update_display(value):
            compression_value_label.setText(f"{value}%")

            # Estimate - actual results depend on image content in the PDF
            if value <= 30:
                reduction_factor = 0.20 + (value / 100) * 0.3    # 20-29%
            elif value <= 50:
                reduction_factor = 0.30 + ((value - 30) / 20) * 0.25  # 30-55%
            elif value <= 70:
                reduction_factor = 0.55 + ((value - 50) / 20) * 0.2   # 55-75%
            elif value <= 85:
                reduction_factor = 0.70 + ((value - 70) / 15) * 0.1   # 70-80%
            else:
                reduction_factor = 0.80 + ((value - 85) / 10) * 0.1   # 80-90%

            estimated = original_size * (1 - reduction_factor)
            estimated_size_label.setText(f"~{estimated / 1024:.0f} KB")
            reduction_label.setText(f"(~{reduction_factor * 100:.0f}% reduction)")

            # Update color based on compression level
            if value <= 30:
                color = "#4CAF50"  # Green
            elif value <= 50:
                color = "#2196F3"  # Blue
            elif value <= 70:
                color = "#FF9800"  # Orange
            else:
                color = "#F44336"  # Red

            compression_value_label.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {color};")

            # Show warning only for page-to-image conversion threshold
            warning_label.setVisible(value >= 90)

        def set_preset(value):
            compression_slider.setValue(value)
            update_display(value)

        # Connect signals
        compression_slider.valueChanged.connect(update_display)
        for btn, value in preset_buttons:
            btn.clicked.connect(lambda checked, v=value: set_preset(v))

        # Initialize display
        update_display(50)

        result = {"proceed": False, "compression": 50}

        def on_compress():
            result["proceed"] = True
            result["compression"] = compression_slider.value()
            dialog.accept()

        compress_btn.clicked.connect(on_compress)
        cancel_btn.clicked.connect(dialog.reject)

        if dialog.exec() != QDialog.DialogCode.Accepted or not result["proceed"]:
            return

        compression_level = result["compression"]

        # Map slider % to JPEG quality and max image dimension.
        # All levels up to 85% re-encode images in-place (text preserved).
        # 90%+ converts entire pages to images (maximum compression, loses text).
        convert_to_images = False
        if compression_level <= 30:
            quality = 80   # Light: mild re-encoding
            max_size = 2400
        elif compression_level <= 50:
            quality = 55   # Medium: noticeable reduction
            max_size = 1800
        elif compression_level <= 70:
            quality = 35   # High: strong re-encoding + downscale
            max_size = 1400
        elif compression_level <= 85:
            quality = 20   # Very High: aggressive re-encoding + downscale
            max_size = 1000
        else:  # 90-95%: Maximum compression
            quality = 15   # Maximum: converts pages to images
            max_size = 800
            convert_to_images = True

        output_file, _ = QFileDialog.getSaveFileName(
            self.main_window,
            "Save Compressed PDF As",
            "",
            "PDF Files (*.pdf)"
        )

        if not output_file:
            return

        # Show progress dialog
        progress = QProgressDialog("Compressing PDF...", "Cancel", 0, 100, self.main_window)
        progress.setWindowTitle("Compression in Progress")
        progress.setWindowModality(QtCore_Qt.WindowModality.WindowModal)
        progress.setMinimumDuration(0)
        progress.setValue(10)
        QApplication.processEvents()

        self.main_window.statusBar().showMessage("Compressing PDF with maximum optimization...")
        progress.setValue(30)
        QApplication.processEvents()

        # Perform compression
        if self.pdf_utilities.compress_pdf(
            input_file, output_file,
            image_quality=quality,
            max_image_size=max_size,
            convert_to_images=convert_to_images,
        ):
            progress.setValue(90)
            QApplication.processEvents()

            compressed_size = Path(output_file).stat().st_size
            reduction = ((original_size - compressed_size) / original_size) * 100

            progress.setValue(100)
            self.main_window.statusBar().showMessage("Compression complete!", 3000)

            QMessageBox.information(
                self.main_window,
                "Compression Complete",
                f"✅ PDF compressed successfully!\n\n"
                f"📁 Original: {original_size / 1024:.1f} KB\n"
                f"📦 Compressed: {compressed_size / 1024:.1f} KB\n"
                f"📉 Reduction: {reduction:.1f}%\n\n"
                f"Compression Level: {compression_level}%"
            )
            self.main_window.load_pdf(output_file)
        else:
            progress.close()
            self.main_window.statusBar().showMessage("Compression failed", 3000)
            QMessageBox.critical(
                self.main_window,
                "Error",
                "Failed to compress PDF. The file may be protected or corrupted."
            )

    def add_ca_branding(self):
        """Add CA Himanshu Majithiya branding to all pages"""
        if not self.main_window.current_file:
            QMessageBox.warning(
                self.main_window,
                "No PDF Open",
                "Please open a PDF file first"
            )
            return

        # Confirm with user
        reply = QMessageBox.question(
            self.main_window,
            "Add CA Branding",
            "Add 'Prepared by CA Himanshu Majithiya' branding to all pages?\n\n"
            "This will add the branding text at the bottom right of every page.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        import fitz
        pdf_doc = fitz.open(self.main_window.current_file)

        try:
            branding_text = "Prepared by CA Himanshu Majithiya"
            font_size = 10
            text_color = (0.3, 0.3, 0.3)  # Dark gray

            # Add branding to all pages
            for page_num in range(len(pdf_doc)):
                page = pdf_doc[page_num]
                page_rect = page.rect

                # Position at bottom right
                text_width = fitz.get_text_length(branding_text, fontname="helv", fontsize=font_size)
                x = page_rect.width - text_width - 30  # 30px from right
                y = page_rect.height - 20  # 20px from bottom

                # Insert text with professional styling
                point = fitz.Point(x, y)
                page.insert_text(
                    point,
                    branding_text,
                    fontsize=font_size,
                    fontname="helv",
                    color=text_color
                )

            # Save the PDF
            output_file, _ = QFileDialog.getSaveFileName(
                self.main_window,
                "Save Branded PDF As",
                "",
                "PDF Files (*.pdf)"
            )

            if output_file:
                pdf_doc.save(output_file)
                pdf_doc.close()
                QMessageBox.information(
                    self.main_window,
                    "Success",
                    f"CA branding added to all {len(pdf_doc)} pages successfully!"
                )
                self.main_window.load_pdf(output_file)
            else:
                pdf_doc.close()

        except Exception as e:
            pdf_doc.close()
            QMessageBox.critical(
                self.main_window,
                "Error",
                f"Failed to add branding: {str(e)}"
            )

    # Additional Features
    def create_form_field(self):
        """Create form field"""
        if not self.main_window.current_file:
            QMessageBox.warning(
                self.main_window,
                "No PDF Open",
                "Please open a PDF file first"
            )
            return

        from src.ui.dialogs import CreateFormFieldDialog
        dialog = CreateFormFieldDialog(self.main_window)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            settings = dialog.get_settings()

            import fitz
            pdf_doc = fitz.open(self.main_window.current_file)

            try:
                page_idx = settings['page'] - 1
                if page_idx < 0 or page_idx >= len(pdf_doc):
                    QMessageBox.warning(
                        self.main_window,
                        "Invalid Page",
                        f"Page {settings['page']} does not exist"
                    )
                    pdf_doc.close()
                    return

                page = pdf_doc[page_idx]
                rect = fitz.Rect(
                    settings['x'],
                    settings['y'],
                    settings['x'] + settings['width'],
                    settings['y'] + settings['height']
                )

                field_type = settings['type']
                if field_type == "Text Field":
                    self.pdf_forms.create_text_field(
                        pdf_doc,
                        page_idx,
                        settings['name'],
                        rect,
                        settings['value']
                    )
                elif field_type == "Checkbox":
                    self.pdf_forms.create_checkbox(
                        pdf_doc,
                        page_idx,
                        settings['name'],
                        rect,
                        settings['value'] == 'True'
                    )
                elif field_type == "Radio Button":
                    self.pdf_forms.create_radio_button(
                        pdf_doc,
                        page_idx,
                        settings['name'],
                        rect
                    )
                elif field_type == "Dropdown List":
                    self.pdf_forms.create_dropdown(
                        pdf_doc,
                        page_idx,
                        settings['name'],
                        rect,
                        settings.get('options', [])
                    )

                output_file, _ = QFileDialog.getSaveFileName(
                    self.main_window,
                    "Save PDF As",
                    "",
                    "PDF Files (*.pdf)"
                )

                if output_file:
                    pdf_doc.save(output_file)
                    pdf_doc.close()
                    QMessageBox.information(
                        self.main_window,
                        "Success",
                        f"Form field '{settings['name']}' created successfully"
                    )
                    self.main_window.load_pdf(output_file)
                else:
                    pdf_doc.close()
            except Exception as e:
                pdf_doc.close()
                QMessageBox.critical(
                    self.main_window,
                    "Error",
                    f"Failed to create form field: {str(e)}"
                )

    def manage_bookmarks(self):
        """Manage bookmarks"""
        if not self.main_window.current_file:
            QMessageBox.warning(
                self.main_window,
                "No PDF Open",
                "Please open a PDF file first"
            )
            return

        import fitz

        # Use the viewer's document to read current bookmarks
        viewer_doc = self.main_window.pdf_viewer.pdf_document
        if not viewer_doc:
            QMessageBox.warning(self.main_window, "Error", "No PDF document loaded")
            return

        # Get current bookmarks
        current_bookmarks = []
        try:
            toc = viewer_doc.get_toc()
            for item in toc:
                level, title, page = item
                current_bookmarks.append({'title': title, 'page': page - 1})
        except:
            pass

        # Also pass total pages so the dialog can validate page numbers
        total_pages = len(viewer_doc)

        from src.ui.dialogs import BookmarkDialog
        dialog = BookmarkDialog(self.main_window, current_bookmarks)
        # Set page range limit
        dialog.bookmark_page.setRange(1, total_pages)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            bookmarks = dialog.get_bookmarks()

            # Build new TOC
            toc = []
            for bookmark in bookmarks:
                # Format: [level, title, page_number]
                toc.append([1, bookmark['title'], bookmark['page'] + 1])

            try:
                # Set the TOC on the viewer's document
                viewer_doc.set_toc(toc)

                # Save directly to the current file using temp file approach
                import tempfile, shutil, os
                temp_fd, temp_path = tempfile.mkstemp(suffix='.pdf')
                os.close(temp_fd)

                viewer_doc.save(temp_path, garbage=4, deflate=True)
                viewer_doc.close()

                current_file = self.main_window.current_file
                shutil.move(temp_path, current_file)

                # Reload the PDF
                self.main_window.load_pdf(current_file)

                QMessageBox.information(
                    self.main_window,
                    "Success",
                    f"Bookmarks updated successfully ({len(bookmarks)} bookmarks)"
                )
            except Exception as e:
                QMessageBox.critical(
                    self.main_window,
                    "Error",
                    f"Failed to save bookmarks: {str(e)}"
                )

    def edit_metadata(self):
        """Edit PDF metadata"""
        if not self.main_window.current_file:
            QMessageBox.warning(
                self.main_window,
                "No PDF Open",
                "Please open a PDF file first"
            )
            return

        import fitz
        pdf_doc = fitz.open(self.main_window.current_file)

        # Get current metadata
        current_metadata = {
            'title': pdf_doc.metadata.get('title', ''),
            'author': pdf_doc.metadata.get('author', ''),
            'subject': pdf_doc.metadata.get('subject', ''),
            'keywords': pdf_doc.metadata.get('keywords', ''),
            'creator': pdf_doc.metadata.get('creator', ''),
            'producer': pdf_doc.metadata.get('producer', '')
        }

        from src.ui.dialogs import MetadataDialog
        dialog = MetadataDialog(self.main_window, current_metadata)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            metadata = dialog.get_metadata()

            pdf_doc.set_metadata(metadata)

            output_file, _ = QFileDialog.getSaveFileName(
                self.main_window,
                "Save PDF As",
                "",
                "PDF Files (*.pdf)"
            )

            if output_file:
                pdf_doc.save(output_file)
                pdf_doc.close()
                QMessageBox.information(
                    self.main_window,
                    "Success",
                    "Metadata updated successfully"
                )
                self.main_window.load_pdf(output_file)
            else:
                pdf_doc.close()
        else:
            pdf_doc.close()

    def extract_pages(self):
        """Extract pages to new PDF"""
        if not self.main_window.current_file:
            QMessageBox.warning(
                self.main_window,
                "No PDF Open",
                "Please open a PDF file first"
            )
            return

        import fitz
        pdf_doc = fitz.open(self.main_window.current_file)
        total_pages = len(pdf_doc)

        from src.ui.dialogs import ExtractPagesDialog
        dialog = ExtractPagesDialog(self.main_window, total_pages)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            settings = dialog.get_settings()

            try:
                # Create new PDF with extracted pages
                new_pdf = fitz.open()

                for page_idx in settings['pages']:
                    if 0 <= page_idx < total_pages:
                        new_pdf.insert_pdf(pdf_doc, from_page=page_idx, to_page=page_idx)

                pdf_doc.close()

                output_file = settings['output_file']
                new_pdf.save(output_file)
                new_pdf.close()

                QMessageBox.information(
                    self.main_window,
                    "Success",
                    f"Extracted {len(settings['pages'])} pages to:\n{output_file}"
                )
                self.main_window.load_pdf(output_file)

            except Exception as e:
                pdf_doc.close()
                QMessageBox.critical(
                    self.main_window,
                    "Error",
                    f"Failed to extract pages: {str(e)}"
                )
        else:
            pdf_doc.close()

    def add_comment(self):
        """Add comment/annotation to PDF by selecting area first"""
        if not self.main_window.current_file:
            QMessageBox.warning(
                self.main_window,
                "No PDF Open",
                "Please open a PDF file first"
            )
            return

        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QDialogButtonBox

        # Show instructions dialog
        dialog = QDialog(self.main_window)
        dialog.setWindowTitle("Add Comment")
        layout = QVBoxLayout()

        instructions = QLabel(
            "<b>Instructions:</b><br><br>"
            "1. Click OK below<br>"
            "2. <b>Draw a rectangle</b> on the PDF where you want to add the comment<br>"
            "3. Enter your comment text in the dialog that appears<br>"
            "4. The comment will be placed in the selected area"
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("padding: 15px; background-color: #E8F4F8; border: 1px solid #B3D9E6; border-radius: 5px; font-size: 13px;")
        layout.addWidget(instructions)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        dialog.setLayout(layout)
        dialog.setMinimumWidth(400)

        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        # Enable selection mode
        self.main_window.pdf_viewer.enable_selection_mode('comment')

        # Connect to area_selected signal
        def on_area_selected(x0, y0, x1, y1):
            try:
                self.main_window.pdf_viewer.area_selected.disconnect(on_area_selected)
            except:
                pass
            self.main_window.pdf_viewer.disable_selection_mode()
            self._show_comment_input_dialog(x0, y0, x1, y1)

        self.main_window.pdf_viewer.area_selected.connect(on_area_selected)

        # Show status message
        self.main_window.status_label.setText("Draw a rectangle where you want to add the comment...")

    def _show_comment_input_dialog(self, x0: float, y0: float, x1: float, y1: float):
        """Show dialog to enter comment for the selected area"""
        from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                                     QDialogButtonBox, QTextEdit, QComboBox, QLineEdit)

        dialog = QDialog(self.main_window)
        dialog.setWindowTitle("Enter Comment")
        dialog.setMinimumWidth(400)
        dialog.setMinimumHeight(250)
        layout = QVBoxLayout()

        # Comment type
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("Comment Type:"))
        type_combo = QComboBox()
        type_combo.addItems(["Text Box", "Sticky Note"])
        type_layout.addWidget(type_combo)
        type_layout.addStretch()
        layout.addLayout(type_layout)

        # Author
        author_layout = QHBoxLayout()
        author_layout.addWidget(QLabel("Author:"))
        author_edit = QLineEdit()
        author_edit.setPlaceholderText("Your name")
        author_layout.addWidget(author_edit)
        layout.addLayout(author_layout)

        # Comment text
        layout.addWidget(QLabel("Comment:"))
        comment_edit = QTextEdit()
        comment_edit.setPlaceholderText("Enter your comment here...")
        comment_edit.setMinimumHeight(80)
        layout.addWidget(comment_edit)

        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        dialog.setLayout(layout)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            comment_text = comment_edit.toPlainText().strip()
            if comment_text:
                comment_type = type_combo.currentText()
                author = author_edit.text().strip() or "Anonymous"
                self._save_comment_to_area(comment_text, x0, y0, x1, y1, comment_type, author)
            else:
                self.main_window.status_label.setText("No comment text entered")
        else:
            self.main_window.status_label.setText("Comment addition cancelled")

    def _save_comment_to_area(self, text: str, x0: float, y0: float, x1: float, y1: float,
                               comment_type: str, author: str):
        """Save comment to the selected area in PDF"""
        import fitz
        pdf_doc = fitz.open(self.main_window.current_file)

        try:
            # Get current page
            current_page_num = self.main_window.pdf_viewer.current_page
            page = pdf_doc[current_page_num]

            # Add annotation based on type
            if comment_type == "Sticky Note":
                # Add sticky note at the center-top of selected area
                point = fitz.Point((x0 + x1) / 2, y0)
                annot = page.add_text_annot(point, text)
            else:
                # Add freetext annotation in the selected rectangle
                rect = fitz.Rect(x0, y0, x1, y1)
                annot = page.add_freetext_annot(
                    rect,
                    text,
                    fontsize=10
                )

            # Set author
            annot.set_info(title=author)
            annot.update()

            # Save
            output_file, _ = QFileDialog.getSaveFileName(
                self.main_window,
                "Save PDF As",
                "",
                "PDF Files (*.pdf)"
            )

            if output_file:
                pdf_doc.save(output_file)
                pdf_doc.close()
                QMessageBox.information(
                    self.main_window,
                    "Success",
                    "Comment added successfully!"
                )
                self.main_window.load_pdf(output_file)
                self.main_window.status_label.setText("Comment added successfully")
            else:
                pdf_doc.close()
                self.main_window.status_label.setText("Save cancelled")

        except Exception as e:
            pdf_doc.close()
            QMessageBox.critical(
                self.main_window,
                "Error",
                f"Failed to add comment: {str(e)}"
            )

    def fill_form(self):
        """Fill form fields interactively"""
        if not self.main_window.current_file:
            QMessageBox.warning(
                self.main_window,
                "No PDF Open",
                "Please open a PDF file first"
            )
            return

        import fitz
        pdf_doc = fitz.open(self.main_window.current_file)

        # Get form fields
        form_fields = self.pdf_forms.get_form_fields(pdf_doc)

        if not form_fields:
            pdf_doc.close()
            QMessageBox.information(
                self.main_window,
                "No Forms",
                "This PDF does not contain any form fields"
            )
            return

        from src.ui.dialogs import FillFormDialog
        dialog = FillFormDialog(self.main_window, form_fields)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            values = dialog.get_values()

            # Fill each field
            for field_name, value in values.items():
                self.pdf_forms.fill_form_field(pdf_doc, field_name, value)

            output_file, _ = QFileDialog.getSaveFileName(
                self.main_window,
                "Save Filled Form As",
                "",
                "PDF Files (*.pdf)"
            )

            if output_file:
                pdf_doc.save(output_file)
                pdf_doc.close()
                QMessageBox.information(
                    self.main_window,
                    "Success",
                    "Form filled successfully"
                )
                self.main_window.load_pdf(output_file)
            else:
                pdf_doc.close()
        else:
            pdf_doc.close()

    def batch_process(self):
        """Batch process multiple PDFs"""
        from src.ui.dialogs import BatchProcessDialog
        dialog = BatchProcessDialog(self.main_window)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            settings = dialog.get_settings()
            files = settings['files']
            operation = settings['operation']
            output_dir = settings['output_dir']

            # Create progress dialog
            progress = QProgressDialog(
                "Processing files...",
                "Cancel",
                0,
                len(files),
                self.main_window
            )
            progress.setWindowModality(Qt.WindowModality.WindowModal)

            success_count = 0
            import fitz

            for i, file_path in enumerate(files):
                if progress.wasCanceled():
                    break

                progress.setValue(i)
                progress.setLabelText(f"Processing: {Path(file_path).name}")

                try:
                    pdf_doc = fitz.open(file_path)
                    output_file = Path(output_dir) / Path(file_path).name

                    if operation == "Add Watermark":
                        self.pdf_security.add_watermark(
                            file_path,
                            str(output_file),
                            "CONFIDENTIAL",
                            0.3
                        )
                        pdf_doc.close()
                    elif operation == "Compress Files":
                        pdf_doc.close()
                        self.pdf_utilities.compress_pdf(file_path, str(output_file), image_quality=50, max_image_size=1400)
                    elif operation == "Convert to PDF/A":
                        pdf_doc.close()
                        self.pdf_creator.convert_to_pdfa(file_path, str(output_file))
                    elif operation == "Add Page Numbers":
                        self.pdf_utilities.add_page_numbers(pdf_doc, "bottom_center")
                        pdf_doc.save(str(output_file))
                        pdf_doc.close()
                    elif operation == "Merge All into One":
                        pdf_doc.close()
                        # Handle merging separately
                        continue

                    success_count += 1

                except Exception as e:
                    self.logger.error(f"Error processing {file_path}: {e}")
                    try:
                        pdf_doc.close()
                    except:
                        pass

            progress.setValue(len(files))

            if operation == "Merge All into One":
                output_file = Path(output_dir) / "merged.pdf"
                if self.pdf_merger.merge_pdfs(files, str(output_file)):
                    success_count = len(files)

            QMessageBox.information(
                self.main_window,
                "Batch Processing Complete",
                f"Successfully processed {success_count} out of {len(files)} files\n\n"
                f"Output directory: {output_dir}"
            )
