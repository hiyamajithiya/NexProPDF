"""
Connected Ribbon toolbar - All buttons wired to backend actions
"""

from PyQt6.QtWidgets import QMessageBox
from src.ui.ribbon import RibbonBar


class ConnectedRibbonBar(RibbonBar):
    """Ribbon with all buttons connected to actions"""

    def __init__(self, parent=None, actions=None):
        self.actions = actions
        self.main_window = parent
        super().__init__(parent)

    def _create_file_tab_tools(self):
        """Create File tab tools WITH CONNECTIONS"""
        self._clear_tool_area()

        # New section
        new_btn = self._create_tool_button("New", "Create new PDF")
        new_btn.clicked.connect(self.main_window.new_file)

        open_btn = self._create_tool_button("Open", "Open existing PDF")
        open_btn.clicked.connect(self.main_window.open_file)

        save_btn = self._create_tool_button("Save", "Save current PDF")
        save_btn.clicked.connect(self.main_window.save_file)

        save_as_btn = self._create_tool_button("Save As", "Save PDF with new name")
        save_as_btn.clicked.connect(self.main_window.save_file_as)

        close_btn = self._create_tool_button("Close", "Close current PDF file")
        close_btn.clicked.connect(self.main_window.close_file)

        self.tool_layout.addWidget(new_btn)
        self.tool_layout.addWidget(open_btn)
        self.tool_layout.addWidget(save_btn)
        self.tool_layout.addWidget(save_as_btn)
        self.tool_layout.addWidget(close_btn)
        self.tool_layout.addWidget(self._create_separator())

        # Metadata
        metadata_btn = self._create_tool_button("Metadata", "Edit PDF metadata")
        metadata_btn.clicked.connect(self.actions.edit_metadata)
        self.tool_layout.addWidget(metadata_btn)

        self.tool_layout.addStretch()

    def _create_convert_tab_tools(self):
        """Create Convert tab tools WITH CONNECTIONS"""
        self._clear_tool_area()

        # PDF to other formats
        to_word_btn = self._create_tool_button("To Word", "Convert PDF to Word document")
        to_word_btn.clicked.connect(self.actions.convert_to_word)

        self.tool_layout.addWidget(to_word_btn)
        self.tool_layout.addWidget(self._create_separator())

        # Other formats to PDF
        from_word_btn = self._create_tool_button("From Word", "Create PDF from Word document")
        from_word_btn.clicked.connect(self.actions.create_from_word)

        from_excel_btn = self._create_tool_button("From Excel", "Create PDF from Excel spreadsheet")
        from_excel_btn.clicked.connect(self.actions.create_from_excel)

        from_ppt_btn = self._create_tool_button("From PPT", "Create PDF from PowerPoint")
        from_ppt_btn.clicked.connect(self.actions.create_from_powerpoint)

        from_images_btn = self._create_tool_button("From Images", "Create PDF from images")
        from_images_btn.clicked.connect(self.actions.create_from_images)

        self.tool_layout.addWidget(from_word_btn)
        self.tool_layout.addWidget(from_excel_btn)
        self.tool_layout.addWidget(from_ppt_btn)
        self.tool_layout.addWidget(from_images_btn)

        self.tool_layout.addStretch()

    def _create_edit_tab_tools(self):
        """Create Edit tab tools WITH CONNECTIONS"""
        self._clear_tool_area()

        # Find & Replace - Simple and reliable text editing
        find_replace_btn = self._create_tool_button("Find & Replace", "Find and replace text in PDF (Recommended)")
        find_replace_btn.clicked.connect(self.actions.find_replace)

        # Edit existing text - Advanced mode with bounding boxes
        edit_text_btn = self._create_tool_button("Edit Text", "Advanced text editing with bounding boxes")
        edit_text_btn.clicked.connect(self.actions.edit_text_advanced)

        save_edits_btn = self._create_tool_button("Save Edits", "Save all pending text edits (Ctrl+Shift+S)")
        save_edits_btn.clicked.connect(self.actions.save_all_edits)

        self.tool_layout.addWidget(find_replace_btn)
        self.tool_layout.addWidget(edit_text_btn)
        self.tool_layout.addWidget(save_edits_btn)
        self.tool_layout.addWidget(self._create_separator())

        # Add content
        add_text_btn = self._create_tool_button("Add Text", "Add new text box")
        add_text_btn.clicked.connect(self.actions.add_text)

        add_image_btn = self._create_tool_button("Add Image", "Insert new image")
        add_image_btn.clicked.connect(self.actions.add_image)

        self.tool_layout.addWidget(add_text_btn)
        self.tool_layout.addWidget(add_image_btn)
        self.tool_layout.addWidget(self._create_separator())

        # Comments/Annotations
        comment_btn = self._create_tool_button("Add Comment", "Add comment or annotation")
        comment_btn.clicked.connect(self.actions.add_comment)
        self.tool_layout.addWidget(comment_btn)

        self.tool_layout.addStretch()

    def _create_pages_tab_tools(self):
        """Create Pages tab tools WITH CONNECTIONS"""
        self._clear_tool_area()

        insert_btn = self._create_tool_button("Insert", "Insert pages")
        insert_btn.clicked.connect(self.actions.insert_pages)

        delete_btn = self._create_tool_button("Delete", "Delete pages")
        delete_btn.clicked.connect(self.actions.delete_pages)

        extract_btn = self._create_tool_button("Extract", "Extract pages")
        extract_btn.clicked.connect(self.actions.extract_pages)

        rotate_btn = self._create_tool_button("Rotate", "Rotate pages")
        rotate_btn.clicked.connect(self.actions.rotate_pages)

        crop_btn = self._create_tool_button("Crop", "Crop pages")
        crop_btn.clicked.connect(self.actions.crop_pages)

        self.tool_layout.addWidget(insert_btn)
        self.tool_layout.addWidget(delete_btn)
        self.tool_layout.addWidget(extract_btn)
        self.tool_layout.addWidget(rotate_btn)
        self.tool_layout.addWidget(crop_btn)
        self.tool_layout.addWidget(self._create_separator())

        # Merge & Split - CONNECTED
        merge_btn = self._create_tool_button("Merge", "Merge multiple PDFs")
        merge_btn.clicked.connect(self.actions.merge_pdfs)

        split_btn = self._create_tool_button("Split", "Split PDF")
        split_btn.clicked.connect(self.actions.split_pdf)

        self.tool_layout.addWidget(merge_btn)
        self.tool_layout.addWidget(split_btn)
        self.tool_layout.addWidget(self._create_separator())

        # Bookmarks
        bookmarks_btn = self._create_tool_button("Bookmarks", "Manage bookmarks")
        bookmarks_btn.clicked.connect(self.actions.manage_bookmarks)

        self.tool_layout.addWidget(bookmarks_btn)

        self.tool_layout.addStretch()

    def _create_security_tab_tools(self):
        """Create Security tab tools WITH CONNECTIONS"""
        self._clear_tool_area()

        # Security features - CONNECTED
        encrypt_btn = self._create_tool_button("Encrypt", "Encrypt PDF with password & permissions")
        encrypt_btn.clicked.connect(self.actions.encrypt_pdf)

        watermark_btn = self._create_tool_button("Watermark", "Add watermark")
        watermark_btn.clicked.connect(self.actions.add_watermark)

        self.tool_layout.addWidget(encrypt_btn)
        self.tool_layout.addWidget(watermark_btn)

        self.tool_layout.addStretch()

    def _create_redaction_tab_tools(self):
        """Create Redaction tab tools WITH CONNECTIONS"""
        self._clear_tool_area()

        manual_btn = self._create_tool_button("Manual", "Draw redaction box")
        manual_btn.clicked.connect(self.actions.manual_redaction)

        text_btn = self._create_tool_button("Text", "Redact specific text")
        text_btn.clicked.connect(self.actions.text_redaction)

        self.tool_layout.addWidget(manual_btn)
        self.tool_layout.addWidget(text_btn)
        self.tool_layout.addWidget(self._create_separator())

        # Pattern-based redaction - CONNECTED
        pan_btn = self._create_tool_button("PAN", "Redact PAN numbers")
        pan_btn.clicked.connect(self.actions.redact_pan)

        aadhaar_btn = self._create_tool_button("Aadhaar", "Redact Aadhaar numbers")
        aadhaar_btn.clicked.connect(self.actions.redact_aadhaar)

        gstin_btn = self._create_tool_button("GSTIN", "Redact GSTIN numbers")
        gstin_btn.clicked.connect(self.actions.redact_gstin)

        bank_btn = self._create_tool_button("Bank Acc", "Redact bank account numbers")
        bank_btn.clicked.connect(self.actions.redact_bank)

        self.tool_layout.addWidget(pan_btn)
        self.tool_layout.addWidget(aadhaar_btn)
        self.tool_layout.addWidget(gstin_btn)
        self.tool_layout.addWidget(bank_btn)

        self.tool_layout.addStretch()

    def _create_forms_tab_tools(self):
        """Create Forms tab tools WITH CONNECTIONS"""
        self._clear_tool_area()

        create_btn = self._create_tool_button("Create Field", "Create form field")
        create_btn.clicked.connect(self.actions.create_form_field)

        fill_btn = self._create_tool_button("Fill Form", "Fill form fields interactively")
        fill_btn.clicked.connect(self.actions.fill_form)

        flatten_btn = self._create_tool_button("Flatten", "Flatten form fields")
        flatten_btn.clicked.connect(self.actions.flatten_form)

        export_btn = self._create_tool_button("Export Data", "Export form data to Excel")
        export_btn.clicked.connect(self.actions.export_form_data)

        self.tool_layout.addWidget(create_btn)
        self.tool_layout.addWidget(fill_btn)
        self.tool_layout.addWidget(flatten_btn)
        self.tool_layout.addWidget(export_btn)

        self.tool_layout.addStretch()

    def _create_signature_tab_tools(self):
        """Create Signature tab tools WITH CONNECTIONS"""
        self._clear_tool_area()

        add_sig_btn = self._create_tool_button("Add Signature", "Add digital signature")
        add_sig_btn.clicked.connect(self.actions.add_signature)

        verify_btn = self._create_tool_button("Verify", "Verify signatures")
        verify_btn.clicked.connect(self.actions.verify_signature)

        cert_btn = self._create_tool_button("Certificates", "Manage certificates")
        cert_btn.clicked.connect(self.actions.manage_certificates)

        self.tool_layout.addWidget(add_sig_btn)
        self.tool_layout.addWidget(verify_btn)
        self.tool_layout.addWidget(cert_btn)

        self.tool_layout.addStretch()

    def _create_tools_tab_tools(self):
        """Create Tools tab tools WITH CONNECTIONS"""
        self._clear_tool_area()

        # All tools - CONNECTED
        bates_btn = self._create_tool_button("Bates Number", "Add Bates numbering")
        bates_btn.clicked.connect(self.actions.add_bates_numbering)

        page_num_btn = self._create_tool_button("Page Numbers", "Add page numbers")
        page_num_btn.clicked.connect(self.actions.add_page_numbers)

        header_btn = self._create_tool_button("Header/Footer", "Add headers and footers")
        header_btn.clicked.connect(self.actions.add_header_footer)

        compress_btn = self._create_tool_button("Compress", "Compress PDF file size")
        compress_btn.clicked.connect(self.actions.compress_pdf)

        self.tool_layout.addWidget(bates_btn)
        self.tool_layout.addWidget(page_num_btn)
        self.tool_layout.addWidget(header_btn)
        self.tool_layout.addWidget(compress_btn)
        self.tool_layout.addWidget(self._create_separator())

        # Batch processing
        batch_btn = self._create_tool_button("Batch Process", "Process multiple PDFs")
        batch_btn.clicked.connect(self.actions.batch_process)
        self.tool_layout.addWidget(batch_btn)

        self.tool_layout.addStretch()

    def _switch_tab(self, tab_name: str):
        """Switch ribbon tab WITH PROPER TAB CREATION"""
        # Uncheck all tabs
        for btn in [self.file_tab, self.edit_tab, self.convert_tab, self.pages_tab,
                    self.security_tab, self.redaction_tab, self.forms_tab,
                    self.signature_tab, self.tools_tab, self.help_tab]:
            btn.setChecked(False)

        # Load appropriate tab content
        if tab_name == "file":
            self.file_tab.setChecked(True)
            self._create_file_tab_tools()
        elif tab_name == "edit":
            self.edit_tab.setChecked(True)
            self._create_edit_tab_tools()
        elif tab_name == "convert":
            self.convert_tab.setChecked(True)
            self._create_convert_tab_tools()
        elif tab_name == "pages":
            self.pages_tab.setChecked(True)
            self._create_pages_tab_tools()
        elif tab_name == "security":
            self.security_tab.setChecked(True)
            self._create_security_tab_tools()
        elif tab_name == "redaction":
            self.redaction_tab.setChecked(True)
            self._create_redaction_tab_tools()
        elif tab_name == "forms":
            self.forms_tab.setChecked(True)
            self._create_forms_tab_tools()
        elif tab_name == "signature":
            self.signature_tab.setChecked(True)
            self._create_signature_tab_tools()
        elif tab_name == "tools":
            self.tools_tab.setChecked(True)
            self._create_tools_tab_tools()

    def _setup_ribbon(self):
        """Override to add all tab connections"""
        super()._setup_ribbon()

        # Connect additional tabs (not connected in parent class)
        self.forms_tab.clicked.connect(lambda: self._switch_tab("forms"))
        self.signature_tab.clicked.connect(lambda: self._switch_tab("signature"))
        self.tools_tab.clicked.connect(lambda: self._switch_tab("tools"))

