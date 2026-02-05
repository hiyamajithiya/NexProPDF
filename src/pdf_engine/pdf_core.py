"""
Core PDF engine using PyMuPDF and pikepdf
"""

import fitz  # PyMuPDF
import pikepdf
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from src.utilities.logger import get_logger


class PDFCore:
    """Core PDF operations wrapper"""

    def __init__(self):
        self.logger = get_logger()
        self.document = None
        self.file_path = None

    def open(self, file_path: str) -> bool:
        """
        Open PDF file

        Args:
            file_path: Path to PDF file

        Returns:
            True if successful, False otherwise
        """
        try:
            self.file_path = Path(file_path)
            self.document = fitz.open(str(file_path))
            self.logger.info(f"Opened PDF: {file_path}")
            return True
        except Exception as e:
            self.logger.error(f"Error opening PDF: {e}")
            return False

    def close(self):
        """Close current PDF"""
        if self.document:
            self.document.close()
            self.document = None
            self.file_path = None
            self.logger.info("PDF closed")

    def save(self, output_path: Optional[str] = None, **kwargs) -> bool:
        """
        Save PDF

        Args:
            output_path: Output file path (None = overwrite current)
            **kwargs: Additional save options

        Returns:
            True if successful
        """
        try:
            if not self.document:
                raise ValueError("No PDF document open")

            save_path = output_path or str(self.file_path)

            # Save with options
            self.document.save(
                save_path,
                garbage=kwargs.get('garbage', 4),  # Remove unused objects
                deflate=kwargs.get('deflate', True),  # Compress
                clean=kwargs.get('clean', True),  # Clean up
                incremental=kwargs.get('incremental', False),
                encryption=kwargs.get('encryption', fitz.PDF_ENCRYPT_NONE)
            )

            self.logger.info(f"PDF saved: {save_path}")
            return True

        except Exception as e:
            self.logger.error(f"Error saving PDF: {e}")
            return False

    def get_page_count(self) -> int:
        """Get number of pages"""
        return len(self.document) if self.document else 0

    def get_page(self, page_num: int):
        """Get specific page"""
        if self.document and 0 <= page_num < len(self.document):
            return self.document[page_num]
        return None

    def get_metadata(self) -> Dict:
        """
        Get PDF metadata

        Returns:
            Dictionary with metadata
        """
        if not self.document:
            return {}

        metadata = self.document.metadata
        return {
            'title': metadata.get('title', ''),
            'author': metadata.get('author', ''),
            'subject': metadata.get('subject', ''),
            'keywords': metadata.get('keywords', ''),
            'creator': metadata.get('creator', ''),
            'producer': metadata.get('producer', ''),
            'creationDate': metadata.get('creationDate', ''),
            'modDate': metadata.get('modDate', ''),
            'format': metadata.get('format', ''),
            'encryption': metadata.get('encryption', None)
        }

    def set_metadata(self, metadata: Dict) -> bool:
        """
        Set PDF metadata

        Args:
            metadata: Dictionary with metadata fields

        Returns:
            True if successful
        """
        try:
            if not self.document:
                raise ValueError("No PDF document open")

            self.document.set_metadata(metadata)
            self.logger.info("Metadata updated")
            return True

        except Exception as e:
            self.logger.error(f"Error setting metadata: {e}")
            return False

    def get_toc(self) -> List:
        """
        Get table of contents (bookmarks)

        Returns:
            List of bookmarks
        """
        if not self.document:
            return []

        return self.document.get_toc()

    def set_toc(self, toc: List) -> bool:
        """
        Set table of contents

        Args:
            toc: List of bookmarks

        Returns:
            True if successful
        """
        try:
            if not self.document:
                raise ValueError("No PDF document open")

            self.document.set_toc(toc)
            self.logger.info("TOC updated")
            return True

        except Exception as e:
            self.logger.error(f"Error setting TOC: {e}")
            return False

    def insert_page(self, page_num: int, width: float = 595, height: float = 842) -> bool:
        """
        Insert blank page

        Args:
            page_num: Position to insert
            width: Page width (default A4)
            height: Page height (default A4)

        Returns:
            True if successful
        """
        try:
            if not self.document:
                raise ValueError("No PDF document open")

            self.document.insert_page(page_num, width=width, height=height)
            self.logger.info(f"Inserted page at position {page_num}")
            return True

        except Exception as e:
            self.logger.error(f"Error inserting page: {e}")
            return False

    def delete_page(self, page_num: int) -> bool:
        """
        Delete page

        Args:
            page_num: Page number to delete

        Returns:
            True if successful
        """
        try:
            if not self.document:
                raise ValueError("No PDF document open")

            self.document.delete_page(page_num)
            self.logger.info(f"Deleted page {page_num}")
            return True

        except Exception as e:
            self.logger.error(f"Error deleting page: {e}")
            return False

    def move_page(self, from_page: int, to_page: int) -> bool:
        """
        Move page to new position

        Args:
            from_page: Source page number
            to_page: Destination page number

        Returns:
            True if successful
        """
        try:
            if not self.document:
                raise ValueError("No PDF document open")

            self.document.move_page(from_page, to_page)
            self.logger.info(f"Moved page {from_page} to {to_page}")
            return True

        except Exception as e:
            self.logger.error(f"Error moving page: {e}")
            return False

    def rotate_page(self, page_num: int, rotation: int) -> bool:
        """
        Rotate page

        Args:
            page_num: Page number
            rotation: Rotation angle (90, 180, 270)

        Returns:
            True if successful
        """
        try:
            if not self.document:
                raise ValueError("No PDF document open")

            page = self.document[page_num]
            page.set_rotation(rotation)
            self.logger.info(f"Rotated page {page_num} by {rotation} degrees")
            return True

        except Exception as e:
            self.logger.error(f"Error rotating page: {e}")
            return False

    def extract_text(self, page_num: int) -> str:
        """
        Extract text from page

        Args:
            page_num: Page number

        Returns:
            Extracted text
        """
        try:
            if not self.document:
                raise ValueError("No PDF document open")

            page = self.document[page_num]
            return page.get_text()

        except Exception as e:
            self.logger.error(f"Error extracting text: {e}")
            return ""

    def search_text(self, text: str, page_num: Optional[int] = None) -> List[Tuple[int, List]]:
        """
        Search for text in PDF

        Args:
            text: Text to search
            page_num: Specific page (None = all pages)

        Returns:
            List of (page_num, rectangles) tuples
        """
        results = []

        try:
            if not self.document:
                raise ValueError("No PDF document open")

            pages = [page_num] if page_num is not None else range(len(self.document))

            for pnum in pages:
                page = self.document[pnum]
                instances = page.search_for(text)
                if instances:
                    results.append((pnum, instances))

        except Exception as e:
            self.logger.error(f"Error searching text: {e}")

        return results

    def add_text(self, page_num: int, text: str, position: Tuple[float, float],
                 fontsize: int = 12, fontname: str = "helv", color: Tuple = (0, 0, 0)) -> bool:
        """
        Add text to page

        Args:
            page_num: Page number
            text: Text to add
            position: (x, y) position
            fontsize: Font size
            fontname: Font name
            color: RGB color tuple

        Returns:
            True if successful
        """
        try:
            if not self.document:
                raise ValueError("No PDF document open")

            page = self.document[page_num]
            page.insert_text(position, text, fontsize=fontsize,
                           fontname=fontname, color=color)

            self.logger.info(f"Added text to page {page_num}")
            return True

        except Exception as e:
            self.logger.error(f"Error adding text: {e}")
            return False

    def add_image(self, page_num: int, image_path: str,
                  rect: Tuple[float, float, float, float]) -> bool:
        """
        Add image to page

        Args:
            page_num: Page number
            image_path: Path to image file
            rect: Rectangle (x0, y0, x1, y1)

        Returns:
            True if successful
        """
        try:
            if not self.document:
                raise ValueError("No PDF document open")

            page = self.document[page_num]
            page.insert_image(fitz.Rect(rect), filename=image_path)

            self.logger.info(f"Added image to page {page_num}")
            return True

        except Exception as e:
            self.logger.error(f"Error adding image: {e}")
            return False

    def get_file_size(self) -> str:
        """Get file size in human-readable format"""
        if not self.file_path or not self.file_path.exists():
            return "Unknown"

        size_bytes = self.file_path.stat().st_size

        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0

        return f"{size_bytes:.2f} TB"
