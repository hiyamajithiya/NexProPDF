"""
PDF Security - encryption, password protection, permissions
"""

import fitz  # PyMuPDF
import pikepdf
from pathlib import Path
from typing import Optional, Dict
from src.utilities.logger import get_logger


class PDFSecurity:
    """PDF security operations"""

    def __init__(self):
        self.logger = get_logger()

    def encrypt_pdf(self, input_file: str, output_file: str,
                   user_password: str = "", owner_password: str = "",
                   permissions: Optional[Dict] = None) -> bool:
        """
        Encrypt PDF with AES-256

        Args:
            input_file: Input PDF file path
            owner_password: Owner password (full permissions)
            permissions: Dictionary of permissions

        Returns:
            True if successful
        """
        try:
            # Default permissions
            if permissions is None:
                permissions = {
                    'print': True,
                    'copy': True,
                    'modify': True,
                    'annotate': True
                }

            # Set permission flags
            perm_flags = fitz.PDF_PERM_ACCESSIBILITY  # Always allow accessibility

            if permissions.get('print', False):
                perm_flags |= fitz.PDF_PERM_PRINT

            if permissions.get('copy', False):
                perm_flags |= fitz.PDF_PERM_COPY

            if permissions.get('modify', False):
                perm_flags |= fitz.PDF_PERM_MODIFY

            if permissions.get('annotate', False):
                perm_flags |= fitz.PDF_PERM_ANNOTATE

            # Open and encrypt PDF
            pdf = fitz.open(input_file)

            # Save with encryption
            pdf.save(
                output_file,
                encryption=fitz.PDF_ENCRYPT_AES_256,
                owner_pw=owner_password,
                user_pw=user_password,
                permissions=perm_flags
            )

            pdf.close()

            self.logger.info(f"PDF encrypted: {output_file}")
            return True

        except Exception as e:
            self.logger.error(f"Error encrypting PDF: {e}")
            return False

    def set_password(self, input_file: str, output_file: str,
                    user_password: str, owner_password: Optional[str] = None) -> bool:
        """
        Set password protection on PDF

        Args:
            input_file: Input PDF file path
            output_file: Output PDF file path
            user_password: User password (for opening)
            owner_password: Owner password (for full access)

        Returns:
            True if successful
        """
        try:
            owner_pw = owner_password or user_password

            pdf = fitz.open(input_file)

            pdf.save(
                output_file,
                encryption=fitz.PDF_ENCRYPT_AES_256,
                user_pw=user_password,
                owner_pw=owner_pw,
                permissions=fitz.PDF_PERM_ACCESSIBILITY |
                          fitz.PDF_PERM_PRINT |
                          fitz.PDF_PERM_COPY |
                          fitz.PDF_PERM_MODIFY
            )

            pdf.close()

            self.logger.info(f"Password protection applied: {output_file}")
            return True

        except Exception as e:
            self.logger.error(f"Error setting password: {e}")
            return False

    def remove_password(self, input_file: str, output_file: str, password: str) -> bool:
        """
        Remove password protection from PDF

        Args:
            input_file: Input PDF file path
            output_file: Output PDF file path
            password: Current password

        Returns:
            True if successful
        """
        try:
            with pikepdf.open(input_file, password=password) as pdf:
                pdf.save(output_file)

            self.logger.info(f"Password removed: {output_file}")
            return True

        except Exception as e:
            self.logger.error(f"Error removing password: {e}")
            return False

    def set_permissions(self, input_file: str, output_file: str,
                       permissions: Dict, owner_password: str = "") -> bool:
        """
        Set document permissions

        Args:
            input_file: Input PDF file path
            output_file: Output PDF file path
            permissions: Dictionary with permission flags
            owner_password: Owner password

        Returns:
            True if successful
        """
        try:
            perm_flags = fitz.PDF_PERM_ACCESSIBILITY

            if permissions.get('print', False):
                perm_flags |= fitz.PDF_PERM_PRINT

            if permissions.get('copy', False):
                perm_flags |= fitz.PDF_PERM_COPY

            if permissions.get('modify', False):
                perm_flags |= fitz.PDF_PERM_MODIFY

            if permissions.get('annotate', False):
                perm_flags |= fitz.PDF_PERM_ANNOTATE

            pdf = fitz.open(input_file)

            pdf.save(
                output_file,
                encryption=fitz.PDF_ENCRYPT_AES_256,
                owner_pw=owner_password,
                permissions=perm_flags
            )

            pdf.close()

            self.logger.info(f"Permissions set: {output_file}")
            return True

        except Exception as e:
            self.logger.error(f"Error setting permissions: {e}")
            return False

    def get_security_info(self, file_path: str) -> Dict:
        """
        Get PDF security information

        Args:
            file_path: PDF file path

        Returns:
            Dictionary with security info
        """
        try:
            with pikepdf.open(file_path, allow_overwriting_input=False) as pdf:
                encryption = pdf.encryption if hasattr(pdf, 'encryption') else None

                return {
                    'is_encrypted': pdf.is_encrypted,
                    'encryption_method': str(encryption) if encryption else None,
                    'permissions': self._get_permissions(pdf) if hasattr(pdf, 'allow') else {}
                }

        except pikepdf.PasswordError:
            return {
                'is_encrypted': True,
                'encryption_method': 'Unknown (password required)',
                'permissions': {}
            }
        except Exception as e:
            self.logger.error(f"Error getting security info: {e}")
            return {
                'is_encrypted': False,
                'encryption_method': None,
                'permissions': {}
            }

    def _get_permissions(self, pdf) -> Dict:
        """Extract permissions from PDF"""
        try:
            return {
                'print': pdf.allow.print,
                'modify': pdf.allow.modify,
                'extract': pdf.allow.extract,
                'annotate': pdf.allow.annotate,
                'form': pdf.allow.form,
                'accessibility': pdf.allow.accessibility
            }
        except:
            return {}

    def add_watermark(self, input_file: str, output_file: str,
                     watermark_text: str, opacity: float = 0.3,
                     font_size: int = 50, color: tuple = (0.7, 0.7, 0.7),
                     rotation: int = 45) -> bool:
        """
        Add text watermark to PDF

        Args:
            input_file: Input PDF file path
            output_file: Output PDF file path
            watermark_text: Watermark text
            opacity: Opacity (0.0 - 1.0)
            font_size: Font size
            color: RGB color tuple (0-1 range)
            rotation: Rotation angle

        Returns:
            True if successful
        """
        try:
            pdf = fitz.open(input_file)

            for page_num in range(len(pdf)):
                page = pdf[page_num]
                page_rect = page.rect

                # Calculate center position
                center_x = page_rect.width / 2
                center_y = page_rect.height / 2

                # Get text dimensions for centering
                font = fitz.Font("helv")
                text_width = font.text_length(watermark_text, fontsize=font_size)

                # Calculate starting point (centered)
                start_x = center_x - text_width / 2
                start_y = center_y

                # Create rotation matrix for morph
                pivot = fitz.Point(center_x, center_y)
                import math
                rad = math.radians(rotation)
                rot_matrix = fitz.Matrix(
                    math.cos(rad), math.sin(rad),
                    -math.sin(rad), math.cos(rad),
                    0, 0
                )

                # Insert watermark text with rotation using morph
                rc = page.insert_text(
                    fitz.Point(start_x, start_y),
                    watermark_text,
                    fontsize=font_size,
                    fontname="helv",
                    color=color,
                    fill_opacity=opacity,
                    stroke_opacity=opacity,
                    morph=(pivot, rot_matrix)
                )

                if rc < 0:
                    self.logger.warning(f"insert_text returned {rc} for page {page_num}")

            pdf.save(output_file)
            pdf.close()

            self.logger.info(f"Watermark added: {output_file}")
            return True

        except Exception as e:
            self.logger.error(f"Error adding watermark: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            return False

    def add_image_watermark(self, input_file: str, output_file: str,
                           watermark_image: str, opacity: float = 0.3,
                           position: str = "center") -> bool:
        """
        Add image watermark to PDF

        Args:
            input_file: Input PDF file path
            output_file: Output PDF file path
            watermark_image: Path to watermark image
            opacity: Opacity (0.0 - 1.0)
            position: Position ("center", "topleft", "topright", "bottomleft", "bottomright")

        Returns:
            True if successful
        """
        try:
            from PIL import Image

            pdf = fitz.open(input_file)

            import io

            # Get image and apply opacity using PIL
            pil_img = Image.open(watermark_image)

            # Scale down large images to fit reasonably on page
            img_width, img_height = pil_img.size
            max_watermark_size = 200
            if img_width > max_watermark_size or img_height > max_watermark_size:
                scale = max_watermark_size / max(img_width, img_height)
                img_width = int(img_width * scale)
                img_height = int(img_height * scale)
                pil_img = pil_img.resize((img_width, img_height), Image.Resampling.LANCZOS)

            # Apply opacity via alpha channel
            rgba_img = pil_img.convert('RGBA')
            alpha_channel = rgba_img.split()[3]
            alpha_channel = alpha_channel.point(lambda p: int(p * opacity))
            rgba_img.putalpha(alpha_channel)

            buf = io.BytesIO()
            rgba_img.save(buf, format='PNG')
            watermark_bytes = buf.getvalue()
            pil_img.close()

            for page_num in range(len(pdf)):
                page = pdf[page_num]
                page_rect = page.rect

                # Convert position string to lowercase for comparison
                pos = position.lower().replace(" ", "")

                # Calculate position
                if pos == "center":
                    x = (page_rect.width - img_width) / 2
                    y = (page_rect.height - img_height) / 2
                elif pos == "topleft":
                    x, y = 20, 20
                elif pos == "topright":
                    x = page_rect.width - img_width - 20
                    y = 20
                elif pos == "bottomleft":
                    x = 20
                    y = page_rect.height - img_height - 20
                elif pos == "bottomright":
                    x = page_rect.width - img_width - 20
                    y = page_rect.height - img_height - 20
                else:
                    x = (page_rect.width - img_width) / 2
                    y = (page_rect.height - img_height) / 2

                rect = fitz.Rect(x, y, x + img_width, y + img_height)
                page.insert_image(rect, stream=watermark_bytes, overlay=True)

            pdf.save(output_file)
            pdf.close()

            self.logger.info(f"Image watermark added: {output_file}")
            return True

        except Exception as e:
            self.logger.error(f"Error adding image watermark: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            return False
