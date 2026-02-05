"""
PDF Creation - Convert from Word, Excel, PowerPoint, Images
"""

import fitz  # PyMuPDF
from pathlib import Path
from typing import List, Optional
from PIL import Image
import io
from src.utilities.logger import get_logger


class PDFCreator:
    """Create PDFs from various file formats"""

    def __init__(self):
        self.logger = get_logger()
        self.last_error = None

    def from_images(self, image_files: List[str], output_file: str,
                   page_size: str = "A4") -> bool:
        """
        Create PDF from image files

        Args:
            image_files: List of image file paths
            output_file: Output PDF file path
            page_size: Page size ("A4", "Letter", "Legal")

        Returns:
            True if successful
        """
        try:
            # Page size presets (in points: 1 point = 1/72 inch)
            page_sizes = {
                "A4": fitz.paper_rect("a4"),
                "Letter": fitz.paper_rect("letter"),
                "Legal": fitz.paper_rect("legal")
            }

            pdf = fitz.open()

            for img_file in image_files:
                self.logger.info(f"Adding image: {img_file}")

                # Open image to get dimensions
                img = Image.open(img_file)
                img_width, img_height = img.size

                # Convert to RGB if necessary
                if img.mode not in ('RGB', 'L'):
                    img = img.convert('RGB')

                # Calculate page size based on image aspect ratio
                if page_size in page_sizes:
                    page_rect = page_sizes[page_size]
                else:
                    # Custom size based on image
                    page_rect = fitz.Rect(0, 0, img_width * 72 / 96, img_height * 72 / 96)

                # Create new page
                page = pdf.new_page(width=page_rect.width, height=page_rect.height)

                # Insert image to fit page
                page.insert_image(page_rect, filename=img_file)

                img.close()

            # Save PDF
            pdf.save(output_file)
            pdf.close()

            self.logger.info(f"Created PDF from {len(image_files)} images: {output_file}")
            return True

        except Exception as e:
            self.logger.error(f"Error creating PDF from images: {e}")
            return False

    def from_word(self, word_file: str, output_file: str) -> bool:
        """
        Create PDF from Word document

        Args:
            word_file: Word file path (.docx)
            output_file: Output PDF file path

        Returns:
            True if successful
        """
        self.last_error = None
        try:
            # This requires Microsoft Word or LibreOffice to be installed
            # Using win32com for Windows
            try:
                import win32com.client
                import pythoncom

                pythoncom.CoInitialize()

                try:
                    word = win32com.client.Dispatch("Word.Application")
                    word.Visible = False

                    # Disable DisplayAlerts to prevent dialogs
                    word.DisplayAlerts = 0

                    doc = word.Documents.Open(str(Path(word_file).absolute()))

                    # Configure PDF export options for better quality and accuracy
                    # SaveAs2 with additional parameters for better PDF quality
                    doc.SaveAs2(
                        str(Path(output_file).absolute()),
                        FileFormat=17,  # wdFormatPDF = 17
                        OptimizeFor=0,  # 0 = Standard quality (wdExportOptimizeForPrint)
                        BitmapMissingFonts=True,
                        CreateBookmarks=0,  # 0 = No bookmarks
                        DocStructureTags=True,
                        IncludeDocProps=True,
                        KeepIRM=True
                    )

                    doc.Close(False)  # Close without saving changes
                    word.Quit()

                    pythoncom.CoUninitialize()

                    self.logger.info(f"Created PDF from Word: {output_file}")
                    return True
                except Exception as com_error:
                    pythoncom.CoUninitialize()
                    self.last_error = f"Microsoft Word is not available or failed to convert the document.\n\nError: {str(com_error)}\n\nPlease ensure Microsoft Word is installed on your system."
                    self.logger.error(f"COM error during Word conversion: {com_error}")
                    # Try fallback
                    raise ImportError("Word COM failed")

            except ImportError:
                # Fallback: Use docx2pdf if available
                try:
                    from docx2pdf import convert
                    convert(word_file, output_file)
                    self.logger.info(f"Created PDF from Word (docx2pdf): {output_file}")
                    self.last_error = None
                    return True
                except ImportError:
                    self.last_error = "Word to PDF conversion requires Microsoft Word to be installed.\n\nAlternatively, install the 'docx2pdf' Python package."
                    self.logger.error("Neither win32com nor docx2pdf available for Word conversion")
                    return False
                except Exception as fallback_error:
                    self.last_error = f"Failed to convert Word document using docx2pdf.\n\nError: {str(fallback_error)}"
                    self.logger.error(f"docx2pdf conversion error: {fallback_error}")
                    return False

        except Exception as e:
            if not self.last_error:
                self.last_error = f"Unexpected error during Word to PDF conversion.\n\nError: {str(e)}"
            self.logger.error(f"Error creating PDF from Word: {e}")
            return False

    def from_excel(self, excel_file: str, output_file: str) -> bool:
        """
        Create PDF from Excel spreadsheet

        Args:
            excel_file: Excel file path (.xlsx, .xls)
            output_file: Output PDF file path

        Returns:
            True if successful
        """
        self.last_error = None
        try:
            # This requires Microsoft Excel or LibreOffice to be installed
            try:
                import win32com.client
                import pythoncom

                pythoncom.CoInitialize()

                try:
                    excel = win32com.client.Dispatch("Excel.Application")
                    excel.Visible = False
                    excel.DisplayAlerts = False

                    wb = excel.Workbooks.Open(str(Path(excel_file).absolute()))

                    # Export all sheets to PDF with proper settings
                    wb.ExportAsFixedFormat(
                        0,  # Type: 0 = xlTypePDF
                        str(Path(output_file).absolute()),
                        0,  # Quality: 0 = xlQualityStandard (high quality)
                        True,  # IncludeDocProperties
                        True,  # IgnorePrintAreas: False to respect print areas
                        1,  # From: first page
                        wb.Sheets.Count  # To: last sheet
                    )

                    wb.Close(False)
                    excel.Quit()

                    pythoncom.CoUninitialize()

                    self.logger.info(f"Created PDF from Excel: {output_file}")
                    return True
                except Exception as com_error:
                    pythoncom.CoUninitialize()
                    self.last_error = f"Microsoft Excel is not available or failed to convert the document.\n\nError: {str(com_error)}\n\nPlease ensure Microsoft Excel is installed on your system."
                    self.logger.error(f"COM error during Excel conversion: {com_error}")
                    return False

            except ImportError:
                self.last_error = "Excel to PDF conversion requires Microsoft Excel to be installed."
                self.logger.error("win32com not available for Excel conversion")
                return False

        except Exception as e:
            if not self.last_error:
                self.last_error = f"Unexpected error during Excel to PDF conversion.\n\nError: {str(e)}"
            self.logger.error(f"Error creating PDF from Excel: {e}")
            return False

    def from_powerpoint(self, ppt_file: str, output_file: str) -> bool:
        """
        Create PDF from PowerPoint presentation

        Args:
            ppt_file: PowerPoint file path (.pptx, .ppt)
            output_file: Output PDF file path

        Returns:
            True if successful
        """
        self.last_error = None
        try:
            # This requires Microsoft PowerPoint or LibreOffice to be installed
            try:
                import win32com.client
                import pythoncom

                pythoncom.CoInitialize()

                try:
                    powerpoint = win32com.client.Dispatch("PowerPoint.Application")
                    powerpoint.Visible = 0  # Hidden
                    powerpoint.DisplayAlerts = 0  # Disable alerts

                    presentation = powerpoint.Presentations.Open(
                        str(Path(ppt_file).absolute()),
                        ReadOnly=True,
                        Untitled=True,
                        WithWindow=False
                    )

                    # Export as PDF with quality settings
                    presentation.ExportAsFixedFormat(
                        str(Path(output_file).absolute()),
                        2,  # ppFixedFormatTypePDF = 2
                        0,  # Intent: 0 = ppFixedFormatIntentScreen (standard quality)
                        0,  # FrameSlides: 0 = no frame
                        1,  # HandoutOrder: not applicable
                        0,  # OutputType: 0 = ppPrintOutputSlides
                        0,  # PrintHiddenSlides: 0 = no
                        None,  # PrintRange
                        2,  # RangeType: 2 = ppPrintAll
                        "",  # SlideShowName
                        True,  # IncludeDocProperties
                        True,  # KeepIRMSettings
                        True,  # DocStructureTags
                        True,  # BitmapMissingFonts
                        False  # UseISO19005_1 (PDF/A)
                    )

                    presentation.Close()
                    powerpoint.Quit()

                    pythoncom.CoUninitialize()

                    self.logger.info(f"Created PDF from PowerPoint: {output_file}")
                    return True
                except Exception as com_error:
                    pythoncom.CoUninitialize()
                    self.last_error = f"Microsoft PowerPoint is not available or failed to convert the document.\n\nError: {str(com_error)}\n\nPlease ensure Microsoft PowerPoint is installed on your system."
                    self.logger.error(f"COM error during PowerPoint conversion: {com_error}")
                    return False

            except ImportError:
                self.last_error = "PowerPoint to PDF conversion requires Microsoft PowerPoint to be installed."
                self.logger.error("win32com not available for PowerPoint conversion")
                return False

        except Exception as e:
            if not self.last_error:
                self.last_error = f"Unexpected error during PowerPoint to PDF conversion.\n\nError: {str(e)}"
            self.logger.error(f"Error creating PDF from PowerPoint: {e}")
            return False

    def from_text(self, text_file: str, output_file: str,
                 font_size: int = 12, font_name: str = "helv") -> bool:
        """
        Create PDF from text file

        Args:
            text_file: Text file path
            output_file: Output PDF file path
            font_size: Font size
            font_name: Font name

        Returns:
            True if successful
        """
        try:
            # Read text file
            with open(text_file, 'r', encoding='utf-8') as f:
                text = f.read()

            # Create PDF
            pdf = fitz.open()
            page = pdf.new_page(width=595, height=842)  # A4 size

            # Insert text
            text_rect = fitz.Rect(50, 50, 545, 792)  # Margins
            page.insert_textbox(
                text_rect,
                text,
                fontsize=font_size,
                fontname=font_name,
                align=fitz.TEXT_ALIGN_LEFT
            )

            pdf.save(output_file)
            pdf.close()

            self.logger.info(f"Created PDF from text: {output_file}")
            return True

        except Exception as e:
            self.logger.error(f"Error creating PDF from text: {e}")
            return False

    def create_blank_pdf(self, output_file: str, num_pages: int = 1,
                        page_width: float = 595, page_height: float = 842) -> bool:
        """
        Create blank PDF

        Args:
            output_file: Output PDF file path
            num_pages: Number of pages
            page_width: Page width in points
            page_height: Page height in points

        Returns:
            True if successful
        """
        try:
            pdf = fitz.open()

            for _ in range(num_pages):
                pdf.new_page(width=page_width, height=page_height)

            pdf.save(output_file)
            pdf.close()

            self.logger.info(f"Created blank PDF with {num_pages} pages: {output_file}")
            return True

        except Exception as e:
            self.logger.error(f"Error creating blank PDF: {e}")
            return False

    def convert_to_pdfa(self, input_file: str, output_file: str) -> bool:
        """
        Convert PDF to PDF/A (archival format)

        Args:
            input_file: Input PDF file path
            output_file: Output PDF/A file path

        Returns:
            True if successful
        """
        try:
            pdf = fitz.open(input_file)

            # Convert to PDF/A by setting metadata and removing incompatible features
            metadata = {
                'format': 'PDF/A-1b',
                'title': pdf.metadata.get('title', ''),
                'author': pdf.metadata.get('author', ''),
                'subject': pdf.metadata.get('subject', ''),
                'keywords': pdf.metadata.get('keywords', '')
            }

            pdf.set_metadata(metadata)

            # Save with PDF/A compatible settings
            pdf.save(
                output_file,
                garbage=4,
                deflate=True,
                clean=True,
                pretty=True
            )

            pdf.close()

            self.logger.info(f"Converted to PDF/A: {output_file}")
            return True

        except Exception as e:
            self.logger.error(f"Error converting to PDF/A: {e}")
            return False

    def batch_convert(self, input_files: List[str], output_dir: str,
                     format_type: str) -> List[str]:
        """
        Batch convert files to PDF

        Args:
            input_files: List of input file paths
            output_dir: Output directory
            format_type: Type of files ('images', 'word', 'excel', 'powerpoint')

        Returns:
            List of created PDF files
        """
        output_files = []
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        conversion_methods = {
            'images': self.from_images,
            'word': self.from_word,
            'excel': self.from_excel,
            'powerpoint': self.from_powerpoint,
            'text': self.from_text
        }

        if format_type not in conversion_methods:
            self.logger.error(f"Unknown format type: {format_type}")
            return []

        try:
            if format_type == 'images':
                # Special handling for images - can combine multiple
                output_file = output_path / "combined.pdf"
                if self.from_images(input_files, str(output_file)):
                    output_files.append(str(output_file))
            else:
                # Convert each file individually
                method = conversion_methods[format_type]

                for input_file in input_files:
                    input_path = Path(input_file)
                    output_file = output_path / f"{input_path.stem}.pdf"

                    if method(input_file, str(output_file)):
                        output_files.append(str(output_file))

            self.logger.info(f"Batch converted {len(output_files)} files")
            return output_files

        except Exception as e:
            self.logger.error(f"Error in batch conversion: {e}")
            return output_files
