"""
PDF Redaction - Secure and irreversible content removal
CRITICAL: Redacted data must NOT exist in underlying PDF objects
"""

import fitz  # PyMuPDF
import re
from typing import List, Tuple, Optional, Dict
from src.utilities.logger import get_logger


class PDFRedaction:
    """PDF redaction operations"""

    # Regex patterns for Indian identification numbers
    PATTERNS = {
        'PAN': r'[A-Z]{5}[0-9]{4}[A-Z]{1}',
        'AADHAAR': r'\b\d{4}\s?\d{4}\s?\d{4}\b',
        'GSTIN': r'\d{2}[A-Z]{5}\d{4}[A-Z]{1}[A-Z\d]{1}[Z]{1}[A-Z\d]{1}',
        'BANK_ACCOUNT': r'\b\d{9,18}\b'
    }

    def __init__(self):
        self.logger = get_logger()

    def redact_area(self, pdf_document, page_num: int, rect: Tuple[float, float, float, float],
                   fill_color: Tuple = (0, 0, 0)) -> bool:
        """
        Manually redact specific area (draw box)

        Args:
            pdf_document: PyMuPDF document object
            page_num: Page number
            rect: Rectangle coordinates (x0, y0, x1, y1)
            fill_color: Fill color RGB tuple (0-1 range)

        Returns:
            True if successful
        """
        try:
            page = pdf_document[page_num]

            # Add redaction annotation
            redact_rect = fitz.Rect(rect)
            page.add_redact_annot(redact_rect, fill=fill_color)

            # Apply redaction (this removes the content permanently)
            page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_PIXELS)

            self.logger.info(f"Redacted area on page {page_num}: {rect}")
            return True

        except Exception as e:
            self.logger.error(f"Error redacting area: {e}")
            return False

    def redact_text(self, pdf_document, text_to_redact: str,
                   pages: Optional[List[int]] = None,
                   fill_color: Tuple = (0, 0, 0)) -> int:
        """
        Redact specific text across pages

        Args:
            pdf_document: PyMuPDF document object
            text_to_redact: Text to find and redact
            pages: List of page numbers (None = all pages)
            fill_color: Fill color RGB tuple

        Returns:
            Number of instances redacted
        """
        try:
            total_count = 0

            # Determine pages to process
            if pages is None:
                pages = range(len(pdf_document))

            for page_num in pages:
                page = pdf_document[page_num]

                # Search for text
                text_instances = page.search_for(text_to_redact)

                # Add redaction annotations
                for inst in text_instances:
                    page.add_redact_annot(inst, fill=fill_color)
                    total_count += 1

                # Apply redactions permanently
                if text_instances:
                    page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_PIXELS)

            self.logger.info(f"Redacted {total_count} instances of '{text_to_redact}' across {len(pages)} pages")
            return total_count

        except Exception as e:
            self.logger.error(f"Error redacting text: {e}")
            return 0

    def redact_pattern(self, pdf_document, pattern_type: str,
                      pages: Optional[List[int]] = None,
                      fill_color: Tuple = (0, 0, 0)) -> int:
        """
        Redact using predefined patterns (PAN, Aadhaar, GSTIN, Bank Account)

        Args:
            pdf_document: PyMuPDF document object
            pattern_type: Type of pattern ('PAN', 'AADHAAR', 'GSTIN', 'BANK_ACCOUNT')
            pages: List of page numbers (None = all pages)
            fill_color: Fill color RGB tuple

        Returns:
            Total number of instances redacted
        """
        try:
            if pattern_type not in self.PATTERNS:
                raise ValueError(f"Unknown pattern type: {pattern_type}")

            pattern = self.PATTERNS[pattern_type]
            total_redacted = 0

            # Determine pages to process
            if pages is None:
                pages = range(len(pdf_document))

            for page_num in pages:
                page = pdf_document[page_num]

                # Extract text with positions
                text = page.get_text()

                # Find matches
                matches = re.finditer(pattern, text)

                for match in matches:
                    matched_text = match.group()

                    # Search for exact text on page
                    text_instances = page.search_for(matched_text)

                    # Add redaction annotations
                    for inst in text_instances:
                        page.add_redact_annot(inst, fill=fill_color)
                        total_redacted += 1

                # Apply redactions
                if total_redacted > 0:
                    page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_PIXELS)

            self.logger.info(f"Redacted {total_redacted} instances of {pattern_type}")
            return total_redacted

        except Exception as e:
            self.logger.error(f"Error redacting pattern: {e}")
            return 0

    def redact_pan(self, pdf_document, pages: Optional[List[int]] = None) -> int:
        """Redact PAN numbers"""
        return self.redact_pattern(pdf_document, 'PAN', pages)

    def redact_aadhaar(self, pdf_document, pages: Optional[List[int]] = None) -> int:
        """Redact Aadhaar numbers"""
        return self.redact_pattern(pdf_document, 'AADHAAR', pages)

    def redact_gstin(self, pdf_document, pages: Optional[List[int]] = None) -> int:
        """Redact GSTIN numbers"""
        return self.redact_pattern(pdf_document, 'GSTIN', pages)

    def redact_bank_account(self, pdf_document, pages: Optional[List[int]] = None) -> int:
        """Redact bank account numbers"""
        return self.redact_pattern(pdf_document, 'BANK_ACCOUNT', pages)

    def remove_metadata(self, pdf_document) -> bool:
        """
        Remove all PDF metadata

        Args:
            pdf_document: PyMuPDF document object

        Returns:
            True if successful
        """
        try:
            # Clear all metadata
            metadata = {
                'title': '',
                'author': '',
                'subject': '',
                'keywords': '',
                'creator': '',
                'producer': '',
                'creationDate': '',
                'modDate': ''
            }

            pdf_document.set_metadata(metadata)

            self.logger.info("Metadata removed")
            return True

        except Exception as e:
            self.logger.error(f"Error removing metadata: {e}")
            return False

    def search_and_redact(self, pdf_document, search_terms: List[str],
                         pages: Optional[List[int]] = None,
                         fill_color: Tuple = (0, 0, 0)) -> Dict:
        """
        Search for multiple terms and redact them

        Args:
            pdf_document: PyMuPDF document object
            search_terms: List of terms to search and redact
            pages: List of page numbers (None = all pages)
            fill_color: Fill color RGB tuple

        Returns:
            Dictionary with redaction counts per term
        """
        results = {}

        try:
            if pages is None:
                pages = range(len(pdf_document))

            for term in search_terms:
                count = 0

                for page_num in pages:
                    page = pdf_document[page_num]

                    # Search for term
                    text_instances = page.search_for(term)

                    # Add redaction annotations
                    for inst in text_instances:
                        page.add_redact_annot(inst, fill=fill_color)
                        count += 1

                    # Apply redactions
                    if text_instances:
                        page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_PIXELS)

                results[term] = count
                self.logger.info(f"Redacted {count} instances of '{term}'")

            return results

        except Exception as e:
            self.logger.error(f"Error in search and redact: {e}")
            return results

    def flatten_pdf(self, pdf_document) -> bool:
        """
        Flatten PDF to make redactions irreversible
        Converts all content to images if needed

        Args:
            pdf_document: PyMuPDF document object

        Returns:
            True if successful
        """
        try:
            # Note: PyMuPDF's apply_redactions already makes redactions permanent
            # This method is for additional flattening if needed

            for page_num in range(len(pdf_document)):
                page = pdf_document[page_num]

                # Remove all annotations
                for annot in page.annots():
                    page.delete_annot(annot)

            self.logger.info("PDF flattened")
            return True

        except Exception as e:
            self.logger.error(f"Error flattening PDF: {e}")
            return False

    def verify_redaction(self, pdf_document, page_num: int, original_text: str) -> bool:
        """
        Verify that redacted text no longer exists in PDF

        Args:
            pdf_document: PyMuPDF document object
            page_num: Page number
            original_text: Text that should have been redacted

        Returns:
            True if text is not found (redaction successful)
        """
        try:
            page = pdf_document[page_num]
            text = page.get_text()

            # Check if text exists
            is_redacted = original_text not in text

            if is_redacted:
                self.logger.info(f"Verified: '{original_text}' successfully redacted")
            else:
                self.logger.warning(f"Warning: '{original_text}' still exists in PDF!")

            return is_redacted

        except Exception as e:
            self.logger.error(f"Error verifying redaction: {e}")
            return False
