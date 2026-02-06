"""
PDF Utilities - Bates numbering, page numbering, headers/footers, bookmarks, hyperlinks
"""

import fitz  # PyMuPDF
from typing import List, Optional, Tuple, Dict
from datetime import datetime
from src.utilities.logger import get_logger


class PDFUtilities:
    """PDF utility operations"""

    def __init__(self):
        self.logger = get_logger()

    def add_bates_numbering(self, pdf_document, prefix: str = "", suffix: str = "",
                           start_number: int = 1, digits: int = 6,
                           position: str = "bottom_right",
                           font_size: int = 10, color: Tuple = (0, 0, 0)) -> bool:
        """
        Add Bates numbering to PDF

        Args:
            pdf_document: PyMuPDF document
            prefix: Prefix text (e.g., "DOC")
            suffix: Suffix text
            start_number: Starting number
            digits: Number of digits (zero-padded)
            position: Position ("top_left", "top_right", "bottom_left", "bottom_right")
            font_size: Font size
            color: RGB color tuple

        Returns:
            True if successful
        """
        try:
            current_number = start_number

            for page_num in range(len(pdf_document)):
                page = pdf_document[page_num]
                page_rect = page.rect

                # Format Bates number
                bates_number = f"{prefix}{str(current_number).zfill(digits)}{suffix}"

                # Calculate position
                if position == "top_left":
                    x, y = 20, 20
                elif position == "top_right":
                    x, y = page_rect.width - 100, 20
                elif position == "bottom_left":
                    x, y = 20, page_rect.height - 20
                elif position == "bottom_right":
                    x, y = page_rect.width - 100, page_rect.height - 20
                else:
                    x, y = page_rect.width - 100, page_rect.height - 20

                # Insert Bates number
                page.insert_text(
                    (x, y),
                    bates_number,
                    fontsize=font_size,
                    color=color
                )

                current_number += 1

            self.logger.info(f"Added Bates numbering: {prefix}[numbers]{suffix}")
            return True

        except Exception as e:
            self.logger.error(f"Error adding Bates numbering: {e}")
            return False

    def add_page_numbers(self, pdf_document, format_string: str = "Page {page} of {total}",
                        position: str = "bottom_center",
                        font_size: int = 10, color: Tuple = (0, 0, 0),
                        start_page: int = 1, exclude_first: bool = False) -> bool:
        """
        Add page numbers to PDF

        Args:
            pdf_document: PyMuPDF document
            format_string: Format string (e.g., "Page {page} of {total}")
            position: Position of page numbers
            font_size: Font size
            color: RGB color tuple
            start_page: Starting page number
            exclude_first: Exclude first page

        Returns:
            True if successful
        """
        try:
            total_pages = len(pdf_document)

            for page_num in range(len(pdf_document)):
                # Skip first page if requested
                if exclude_first and page_num == 0:
                    continue

                page = pdf_document[page_num]
                page_rect = page.rect

                # Calculate page number
                page_number = start_page + page_num - (1 if exclude_first else 0)

                # Format page number string
                page_text = format_string.format(
                    page=page_number,
                    total=total_pages
                )

                # Calculate position
                if position == "top_left":
                    x, y = 20, 20
                elif position == "top_center":
                    x, y = page_rect.width / 2 - 30, 20
                elif position == "top_right":
                    x, y = page_rect.width - 80, 20
                elif position == "bottom_left":
                    x, y = 20, page_rect.height - 20
                elif position == "bottom_center":
                    x, y = page_rect.width / 2 - 30, page_rect.height - 20
                elif position == "bottom_right":
                    x, y = page_rect.width - 80, page_rect.height - 20
                else:
                    x, y = page_rect.width / 2 - 30, page_rect.height - 20

                # Insert page number
                page.insert_text(
                    (x, y),
                    page_text,
                    fontsize=font_size,
                    color=color
                )

            self.logger.info(f"Added page numbers to PDF")
            return True

        except Exception as e:
            self.logger.error(f"Error adding page numbers: {e}")
            return False

    def add_header(self, pdf_document, text: str, position: str = "center",
                  font_size: int = 12, color: Tuple = (0, 0, 0),
                  exclude_first: bool = False) -> bool:
        """
        Add header to all pages with proper background

        Args:
            pdf_document: PyMuPDF document
            text: Header text
            position: Position ("left", "center", "right")
            font_size: Font size
            color: RGB color tuple
            exclude_first: Exclude first page

        Returns:
            True if successful
        """
        try:
            import fitz

            # Header area height (margin from top)
            header_height = 40
            header_margin = 10

            for page_num in range(len(pdf_document)):
                if exclude_first and page_num == 0:
                    continue

                page = pdf_document[page_num]
                page_rect = page.rect

                # Create white background rectangle for header area
                header_rect = fitz.Rect(0, 0, page_rect.width, header_height)
                shape = page.new_shape()
                shape.draw_rect(header_rect)
                shape.finish(color=(1, 1, 1), fill=(1, 1, 1))  # White background
                shape.commit()

                # Draw a subtle line below header
                line_y = header_height - 2
                shape = page.new_shape()
                shape.draw_line((header_margin, line_y), (page_rect.width - header_margin, line_y))
                shape.finish(color=(0.7, 0.7, 0.7), width=0.5)  # Light gray line
                shape.commit()

                # Calculate text position
                font = fitz.Font("helv")
                text_width = font.text_length(text, fontsize=font_size)

                if position == "left":
                    x = header_margin + 10
                elif position == "right":
                    x = page_rect.width - text_width - header_margin - 10
                else:  # center
                    x = (page_rect.width - text_width) / 2

                # Text baseline position (vertically centered in header area)
                y = (header_height + font_size) / 2

                # Insert header text
                page.insert_text(
                    (x, y),
                    text,
                    fontsize=font_size,
                    fontname="helv",
                    color=color
                )

            self.logger.info(f"Added header: {text}")
            return True

        except Exception as e:
            self.logger.error(f"Error adding header: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            return False

    def add_footer(self, pdf_document, text: str, position: str = "center",
                  font_size: int = 10, color: Tuple = (0, 0, 0),
                  exclude_first: bool = False) -> bool:
        """
        Add footer to all pages with proper background

        Args:
            pdf_document: PyMuPDF document
            text: Footer text
            position: Position ("left", "center", "right")
            font_size: Font size
            color: RGB color tuple
            exclude_first: Exclude first page

        Returns:
            True if successful
        """
        try:
            import fitz

            # Footer area height (margin from bottom)
            footer_height = 35
            footer_margin = 10

            for page_num in range(len(pdf_document)):
                if exclude_first and page_num == 0:
                    continue

                page = pdf_document[page_num]
                page_rect = page.rect

                # Create white background rectangle for footer area
                footer_rect = fitz.Rect(0, page_rect.height - footer_height, page_rect.width, page_rect.height)
                shape = page.new_shape()
                shape.draw_rect(footer_rect)
                shape.finish(color=(1, 1, 1), fill=(1, 1, 1))  # White background
                shape.commit()

                # Draw a subtle line above footer
                line_y = page_rect.height - footer_height + 2
                shape = page.new_shape()
                shape.draw_line((footer_margin, line_y), (page_rect.width - footer_margin, line_y))
                shape.finish(color=(0.7, 0.7, 0.7), width=0.5)  # Light gray line
                shape.commit()

                # Calculate text position
                font = fitz.Font("helv")
                text_width = font.text_length(text, fontsize=font_size)

                if position == "left":
                    x = footer_margin + 10
                elif position == "right":
                    x = page_rect.width - text_width - footer_margin - 10
                else:  # center
                    x = (page_rect.width - text_width) / 2

                # Text baseline position (vertically centered in footer area)
                y = page_rect.height - (footer_height - font_size) / 2 - 5

                # Insert footer text
                page.insert_text(
                    (x, y),
                    text,
                    fontsize=font_size,
                    fontname="helv",
                    color=color
                )

            self.logger.info(f"Added footer: {text}")
            return True

        except Exception as e:
            self.logger.error(f"Error adding footer: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            return False

    def add_hyperlink(self, pdf_document, page_num: int,
                     rect: Tuple[float, float, float, float],
                     url: str, border_color: Optional[Tuple] = None) -> bool:
        """
        Add hyperlink to PDF

        Args:
            pdf_document: PyMuPDF document
            page_num: Page number
            rect: Link rectangle (x0, y0, x1, y1)
            url: URL to link to
            border_color: Optional border color

        Returns:
            True if successful
        """
        try:
            page = pdf_document[page_num]

            # Create link annotation
            link = fitz.Link()
            link.set_border(width=1, dashes=None)
            link.uri = url
            link.rect = fitz.Rect(rect)

            if border_color:
                link.set_colors(stroke=border_color)

            # Add link to page
            page.insert_link(link.to_dict())

            self.logger.info(f"Added hyperlink on page {page_num}: {url}")
            return True

        except Exception as e:
            self.logger.error(f"Error adding hyperlink: {e}")
            return False

    def add_internal_link(self, pdf_document, from_page: int,
                         rect: Tuple[float, float, float, float],
                         to_page: int, zoom: float = 0) -> bool:
        """
        Add internal link to another page

        Args:
            pdf_document: PyMuPDF document
            from_page: Source page number
            rect: Link rectangle
            to_page: Destination page number
            zoom: Zoom level (0 = fit page)

        Returns:
            True if successful
        """
        try:
            page = pdf_document[from_page]

            # Create internal link
            link_dict = {
                'kind': fitz.LINK_GOTO,
                'from': fitz.Rect(rect),
                'page': to_page,
                'to': fitz.Point(0, 0),
                'zoom': zoom
            }

            page.insert_link(link_dict)

            self.logger.info(f"Added internal link from page {from_page} to {to_page}")
            return True

        except Exception as e:
            self.logger.error(f"Error adding internal link: {e}")
            return False

    def create_bookmark(self, pdf_document, title: str, page_num: int,
                       level: int = 1) -> bool:
        """
        Create bookmark (table of contents entry)

        Args:
            pdf_document: PyMuPDF document
            title: Bookmark title
            page_num: Page number
            level: Bookmark level (1, 2, 3...)

        Returns:
            True if successful
        """
        try:
            # Get existing TOC
            toc = pdf_document.get_toc()

            # Add new bookmark
            toc.append([level, title, page_num + 1])  # Page numbers are 1-indexed in TOC

            # Set TOC
            pdf_document.set_toc(toc)

            self.logger.info(f"Created bookmark: {title}")
            return True

        except Exception as e:
            self.logger.error(f"Error creating bookmark: {e}")
            return False

    def add_background(self, pdf_document, background_pdf: str,
                      pages: Optional[List[int]] = None) -> bool:
        """
        Add background from another PDF

        Args:
            pdf_document: PyMuPDF document
            background_pdf: Path to background PDF
            pages: List of page numbers (None = all pages)

        Returns:
            True if successful
        """
        try:
            bg_doc = fitz.open(background_pdf)

            if not pages:
                pages = range(len(pdf_document))

            for page_num in pages:
                if page_num >= len(pdf_document):
                    continue

                page = pdf_document[page_num]

                # Use first page of background PDF
                bg_page = bg_doc[0]

                # Show background PDF as underlay
                page.show_pdf_page(page.rect, bg_doc, 0)

            bg_doc.close()

            self.logger.info(f"Added background from: {background_pdf}")
            return True

        except Exception as e:
            self.logger.error(f"Error adding background: {e}")
            return False

    def add_stamp(self, pdf_document, stamp_text: str,
                 position: str = "center", opacity: float = 0.3,
                 rotation: int = 45, font_size: int = 60,
                 color: Tuple = (1, 0, 0), pages: Optional[List[int]] = None) -> bool:
        """
        Add stamp (e.g., CONFIDENTIAL, DRAFT) to pages

        Args:
            pdf_document: PyMuPDF document
            stamp_text: Stamp text
            position: Position ("center", "top", "bottom", "diagonal")
            opacity: Opacity (0.0 - 1.0)
            rotation: Rotation angle
            font_size: Font size
            color: RGB color tuple
            pages: List of page numbers (None = all pages)

        Returns:
            True if successful
        """
        try:
            if not pages:
                pages = range(len(pdf_document))

            for page_num in pages:
                if page_num >= len(pdf_document):
                    continue

                page = pdf_document[page_num]
                page_rect = page.rect

                # Calculate position
                if position == "center":
                    x, y = page_rect.width / 2, page_rect.height / 2
                elif position == "top":
                    x, y = page_rect.width / 2, 100
                elif position == "bottom":
                    x, y = page_rect.width / 2, page_rect.height - 100
                else:  # diagonal
                    x, y = page_rect.width / 2, page_rect.height / 2

                # Create text writer for stamp
                tw = fitz.TextWriter(page_rect)
                tw.append(
                    fitz.Point(x, y),
                    stamp_text,
                    fontsize=font_size,
                    color=color,
                    rotate=rotation
                )

                # Write with opacity
                tw.write_text(page, opacity=opacity)

            self.logger.info(f"Added stamp: {stamp_text}")
            return True

        except Exception as e:
            self.logger.error(f"Error adding stamp: {e}")
            return False

    def compress_pdf(self, input_file: str, output_file: str,
                    image_quality: int = 50, max_image_size: int = 1200,
                    convert_to_images: bool = False) -> bool:
        """
        Compress PDF by re-encoding embedded images at lower quality.

        Preserves text selectability and structure while significantly reducing
        file size by re-encoding images with JPEG compression and downscaling
        oversized images.

        Args:
            input_file: Input PDF path
            output_file: Output PDF path
            image_quality: JPEG quality for images (1-100, lower = smaller)
            max_image_size: Maximum pixel dimension for images
            convert_to_images: If True, convert entire pages to images (maximum
                compression but loses text selectability)

        Returns:
            True if successful
        """
        try:
            import os
            from PIL import Image
            import io

            pdf = fitz.open(input_file)
            original_size = os.path.getsize(input_file)

            if convert_to_images:
                self._compress_as_images(pdf, output_file, image_quality, max_image_size)
            else:
                self._compress_reencoding(pdf, output_file, image_quality, max_image_size)

            compressed_size = os.path.getsize(output_file)
            reduction = original_size - compressed_size
            ratio = (reduction / original_size) * 100 if original_size > 0 else 0

            self.logger.info(
                f"PDF Compression: {original_size:,} bytes -> {compressed_size:,} bytes "
                f"({ratio:.1f}% reduction, saved {reduction:,} bytes)"
            )
            return True

        except Exception as e:
            self.logger.error(f"Error compressing PDF: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            return False

    def _compress_reencoding(self, pdf, output_file: str,
                             image_quality: int, max_image_size: int):
        """Re-encode embedded images in-place, preserving text and structure."""
        from PIL import Image
        import io

        processed_xrefs = set()

        for page_num in range(len(pdf)):
            page = pdf[page_num]
            images = page.get_images(full=True)

            for img_info in images:
                xref = img_info[0]
                if xref in processed_xrefs:
                    continue
                processed_xrefs.add(xref)

                try:
                    base = pdf.extract_image(xref)
                    if not base or not base.get("image"):
                        continue

                    image_bytes = base["image"]
                    img_w = base.get("width", 0)
                    img_h = base.get("height", 0)
                    orig_cs = base.get("colorspace", 0)  # colorspace component count

                    # Skip very small images (icons, logos) - not worth recompressing
                    if img_w * img_h < 2500 or len(image_bytes) < 5000:
                        continue

                    pil_img = Image.open(io.BytesIO(image_bytes))
                    is_grayscale = pil_img.mode == 'L'

                    # Convert palette/indexed/CMYK/RGBA to appropriate mode
                    if pil_img.mode in ('P', 'PA'):
                        pil_img = pil_img.convert('RGBA').convert('RGB')
                        is_grayscale = False
                    elif pil_img.mode == 'CMYK':
                        pil_img = pil_img.convert('RGB')
                        is_grayscale = False
                    elif pil_img.mode in ('RGBA', 'LA'):
                        # Flatten alpha onto white background
                        bg = Image.new('RGB', pil_img.size, (255, 255, 255))
                        bg.paste(pil_img, mask=pil_img.split()[-1])
                        pil_img = bg
                        is_grayscale = False
                    elif pil_img.mode == 'L':
                        # Keep grayscale as-is for JPEG (saves space)
                        is_grayscale = True
                    elif pil_img.mode != 'RGB':
                        pil_img = pil_img.convert('RGB')
                        is_grayscale = False

                    # Downscale oversized images
                    max_dim = max(pil_img.width, pil_img.height)
                    if max_dim > max_image_size:
                        ratio = max_image_size / max_dim
                        new_w = max(1, int(pil_img.width * ratio))
                        new_h = max(1, int(pil_img.height * ratio))
                        pil_img = pil_img.resize((new_w, new_h), Image.Resampling.LANCZOS)

                    # Re-encode as JPEG
                    buf = io.BytesIO()
                    jpeg_q = max(10, min(95, image_quality))
                    pil_img.save(buf, format='JPEG', quality=jpeg_q, optimize=True)
                    new_data = buf.getvalue()

                    # Only replace if actually smaller
                    if len(new_data) < len(image_bytes):
                        pdf.update_stream(xref, new_data)
                        pdf.xref_set_key(xref, "Filter", "/DCTDecode")
                        if is_grayscale:
                            pdf.xref_set_key(xref, "ColorSpace", "/DeviceGray")
                        else:
                            pdf.xref_set_key(xref, "ColorSpace", "/DeviceRGB")
                        pdf.xref_set_key(xref, "BitsPerComponent", "8")
                        pdf.xref_set_key(xref, "Width", str(pil_img.width))
                        pdf.xref_set_key(xref, "Height", str(pil_img.height))
                        pdf.xref_set_key(xref, "DecodeParms", "null")

                except Exception as e:
                    self.logger.debug(f"Skipping image xref {xref}: {e}")
                    continue

        # NOTE: Do NOT use clean=True here - it rebuilds the PDF structure
        # and can discard valid content after manual stream/xref modifications
        pdf.save(
            output_file,
            garbage=4,
            deflate=True,
            deflate_images=True,
            deflate_fonts=True,
        )
        pdf.close()

    def _compress_as_images(self, pdf, output_file: str,
                            image_quality: int, max_image_size: int):
        """Convert entire pages to images for maximum compression (loses text)."""
        from PIL import Image
        import io

        temp_pdf = fitz.open()

        for page_num in range(len(pdf)):
            page = pdf[page_num]
            page_rect = page.rect

            # DPI based on quality
            if image_quality >= 30:
                zoom = 1.5   # ~108 DPI
            elif image_quality >= 20:
                zoom = 1.2   # ~86 DPI
            else:
                zoom = 1.0   # 72 DPI

            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat, alpha=False)
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

            # Downscale if exceeds max
            max_dim = max(img.width, img.height)
            target_max = int(max_image_size * zoom)
            if max_dim > target_max:
                ratio = target_max / max_dim
                img = img.resize(
                    (max(1, int(img.width * ratio)), max(1, int(img.height * ratio))),
                    Image.Resampling.LANCZOS
                )

            buf = io.BytesIO()
            img.save(buf, format='JPEG', quality=max(15, image_quality), optimize=True)

            new_page = temp_pdf.new_page(width=page_rect.width, height=page_rect.height)
            new_page.insert_image(page_rect, stream=buf.getvalue())

        pdf.close()
        temp_pdf.save(output_file, garbage=4, deflate=True, deflate_images=True, clean=True)
        temp_pdf.close()
