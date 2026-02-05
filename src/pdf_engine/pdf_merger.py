"""
PDF merge and split operations
"""

import fitz  # PyMuPDF
from pathlib import Path
from typing import List, Optional, Tuple
from src.utilities.logger import get_logger


class PDFMerger:
    """PDF merge and split operations"""

    def __init__(self):
        self.logger = get_logger()

    def merge_pdfs(self, input_files: List[str], output_file: str) -> bool:
        """
        Merge multiple PDF files into one

        Args:
            input_files: List of input PDF file paths
            output_file: Output PDF file path

        Returns:
            True if successful
        """
        try:
            result_pdf = fitz.open()

            for pdf_file in input_files:
                self.logger.info(f"Merging: {pdf_file}")
                with fitz.open(pdf_file) as pdf:
                    result_pdf.insert_pdf(pdf)

            result_pdf.save(output_file)
            result_pdf.close()

            self.logger.info(f"Merged {len(input_files)} PDFs into: {output_file}")
            return True

        except Exception as e:
            self.logger.error(f"Error merging PDFs: {e}")
            return False

    def split_by_pages(self, input_file: str, output_dir: str,
                       pages_per_file: int = 1) -> List[str]:
        """
        Split PDF by number of pages

        Args:
            input_file: Input PDF file path
            output_dir: Output directory
            pages_per_file: Number of pages per output file

        Returns:
            List of created file paths
        """
        output_files = []

        try:
            pdf = fitz.open(input_file)
            total_pages = len(pdf)
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)

            file_num = 1
            for start_page in range(0, total_pages, pages_per_file):
                end_page = min(start_page + pages_per_file, total_pages)

                # Create new PDF
                new_pdf = fitz.open()
                new_pdf.insert_pdf(pdf, from_page=start_page, to_page=end_page - 1)

                # Save
                output_file = output_path / f"split_{file_num:04d}.pdf"
                new_pdf.save(str(output_file))
                new_pdf.close()

                output_files.append(str(output_file))
                file_num += 1

            pdf.close()
            self.logger.info(f"Split PDF into {len(output_files)} files")
            return output_files

        except Exception as e:
            self.logger.error(f"Error splitting PDF: {e}")
            return []

    def split_by_range(self, input_file: str, output_dir: str,
                       ranges: List[Tuple[int, int]]) -> List[str]:
        """
        Split PDF by page ranges

        Args:
            input_file: Input PDF file path
            output_dir: Output directory
            ranges: List of (start_page, end_page) tuples (0-indexed)

        Returns:
            List of created file paths
        """
        output_files = []

        try:
            pdf = fitz.open(input_file)
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)

            for idx, (start_page, end_page) in enumerate(ranges, 1):
                # Create new PDF
                new_pdf = fitz.open()
                new_pdf.insert_pdf(pdf, from_page=start_page, to_page=end_page)

                # Save
                output_file = output_path / f"range_{idx:04d}_p{start_page + 1}-{end_page + 1}.pdf"
                new_pdf.save(str(output_file))
                new_pdf.close()

                output_files.append(str(output_file))

            pdf.close()
            self.logger.info(f"Split PDF into {len(output_files)} files by range")
            return output_files

        except Exception as e:
            self.logger.error(f"Error splitting PDF by range: {e}")
            return []

    def split_by_size(self, input_file: str, output_dir: str,
                     max_size_mb: float) -> List[str]:
        """
        Split PDF by file size

        Args:
            input_file: Input PDF file path
            output_dir: Output directory
            max_size_mb: Maximum size per file in MB

        Returns:
            List of created file paths
        """
        output_files = []

        try:
            pdf = fitz.open(input_file)
            total_pages = len(pdf)
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)

            max_size_bytes = max_size_mb * 1024 * 1024
            file_num = 1
            current_pages = []

            for page_num in range(total_pages):
                current_pages.append(page_num)

                # Create temporary PDF to check size
                temp_pdf = fitz.open()
                for p in current_pages:
                    temp_pdf.insert_pdf(pdf, from_page=p, to_page=p)

                # Check size (rough estimate)
                temp_size = len(temp_pdf.tobytes())

                if temp_size >= max_size_bytes:
                    # Save current batch (excluding last page)
                    if len(current_pages) > 1:
                        new_pdf = fitz.open()
                        for p in current_pages[:-1]:
                            new_pdf.insert_pdf(pdf, from_page=p, to_page=p)

                        output_file = output_path / f"size_split_{file_num:04d}.pdf"
                        new_pdf.save(str(output_file))
                        new_pdf.close()

                        output_files.append(str(output_file))
                        file_num += 1

                        # Start new batch with last page
                        current_pages = [current_pages[-1]]

                temp_pdf.close()

            # Save remaining pages
            if current_pages:
                new_pdf = fitz.open()
                for p in current_pages:
                    new_pdf.insert_pdf(pdf, from_page=p, to_page=p)

                output_file = output_path / f"size_split_{file_num:04d}.pdf"
                new_pdf.save(str(output_file))
                new_pdf.close()

                output_files.append(str(output_file))

            pdf.close()
            self.logger.info(f"Split PDF into {len(output_files)} files by size")
            return output_files

        except Exception as e:
            self.logger.error(f"Error splitting PDF by size: {e}")
            return []

    def extract_pages(self, input_file: str, output_file: str,
                     pages: List[int]) -> bool:
        """
        Extract specific pages to new PDF

        Args:
            input_file: Input PDF file path
            output_file: Output PDF file path
            pages: List of page numbers to extract (0-indexed)

        Returns:
            True if successful
        """
        try:
            pdf = fitz.open(input_file)
            new_pdf = fitz.open()

            for page_num in sorted(pages):
                if 0 <= page_num < len(pdf):
                    new_pdf.insert_pdf(pdf, from_page=page_num, to_page=page_num)

            new_pdf.save(output_file)
            new_pdf.close()
            pdf.close()

            self.logger.info(f"Extracted {len(pages)} pages to: {output_file}")
            return True

        except Exception as e:
            self.logger.error(f"Error extracting pages: {e}")
            return False
