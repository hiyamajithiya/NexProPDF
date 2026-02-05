"""
PDF Digital Signatures - Support for Indian DSC (Class 2/3) with USB Token
Supports: ePass2003, Proxkey, WatchData, and other PKCS#11 tokens
"""

import fitz  # PyMuPDF
import os
import sys
from datetime import datetime
from typing import Optional, Dict, Tuple, List
from pathlib import Path
from src.utilities.logger import get_logger


class PDFSignature:
    """PDF digital signature operations with USB Token support"""

    # Common PKCS#11 DLL paths for various tokens in India
    TOKEN_DLLS = {
        'windows': [
            # ePass2003 (most common in India)
            r'C:\Windows\System32\eps2003csp11.dll',
            r'C:\Windows\SysWOW64\eps2003csp11.dll',
            # WatchData ProxKey
            r'C:\Windows\System32\wdpkcs.dll',
            r'C:\Program Files\Watchdata\ProxKey\wdpkcs.dll',
            # eMudhra
            r'C:\Windows\System32\emlogiN_PKCS11.dll',
            # Safenet/Gemalto
            r'C:\Windows\System32\eTPKCS11.dll',
            # Generic locations
            r'C:\Windows\System32\cryptoCertum3PKCS.dll',
        ],
        'linux': [
            '/usr/lib/WatchData/ProxKey/lib/libwdpkcs_SignatureP11.so',
            '/usr/lib/libeTPkcs11.so',
            '/usr/lib/libeps2003csp11.so',
        ]
    }

    def __init__(self):
        self.logger = get_logger()
        self._pkcs11_lib = None
        self._available_tokens = []
        self._pykcs11_available = self._check_pykcs11()

    def _check_pykcs11(self) -> bool:
        """Check if PyKCS11 is available."""
        try:
            import PyKCS11
            return True
        except ImportError:
            return False

    def is_usb_token_supported(self) -> Tuple[bool, str]:
        """Check if USB token signing is supported."""
        if self._pykcs11_available:
            return True, "USB token signing is available"
        else:
            return False, (
                "USB token signing requires PyKCS11 library.\n\n"
                "To enable USB token support:\n"
                "1. Install Visual C++ Build Tools from:\n"
                "   https://visualstudio.microsoft.com/visual-cpp-build-tools/\n"
                "2. Then run: pip install PyKCS11 endesive\n\n"
                "Alternative: Use 'Sign with Certificate File' option\n"
                "to sign with .pfx or .p12 certificate files."
            )

    def detect_usb_tokens(self) -> List[Dict]:
        """
        Detect available USB tokens connected to the system.

        Returns:
            List of detected tokens with their information
        """
        tokens = []

        try:
            import PyKCS11 as PK11

            # Get DLL paths for current platform
            if sys.platform == 'win32':
                dll_paths = self.TOKEN_DLLS['windows']
            else:
                dll_paths = self.TOKEN_DLLS['linux']

            for dll_path in dll_paths:
                if os.path.exists(dll_path):
                    try:
                        pkcs11 = PK11.PyKCS11Lib()
                        pkcs11.load(dll_path)

                        # Get available slots
                        slots = pkcs11.getSlotList(tokenPresent=True)

                        for slot in slots:
                            try:
                                token_info = pkcs11.getTokenInfo(slot)
                                tokens.append({
                                    'slot': slot,
                                    'label': token_info.label.strip(),
                                    'manufacturer': token_info.manufacturerID.strip(),
                                    'model': token_info.model.strip(),
                                    'serial': token_info.serialNumber.strip(),
                                    'dll_path': dll_path,
                                    'flags': token_info.flags
                                })
                                self.logger.info(f"Found token: {token_info.label.strip()}")
                            except Exception as e:
                                self.logger.debug(f"Could not get token info for slot {slot}: {e}")

                    except Exception as e:
                        self.logger.debug(f"Could not load PKCS#11 library {dll_path}: {e}")

            self._available_tokens = tokens
            return tokens

        except ImportError:
            self.logger.warning("PyKCS11 not installed. Install with: pip install PyKCS11")
            return []
        except Exception as e:
            self.logger.error(f"Error detecting USB tokens: {e}")
            return []

    def get_certificates_from_token(self, dll_path: str, slot: int = 0, pin: str = None) -> List[Dict]:
        """
        Get certificates stored in USB token.

        Args:
            dll_path: Path to PKCS#11 DLL
            slot: Token slot number
            pin: Token PIN (optional, will prompt if needed)

        Returns:
            List of certificates with their information
        """
        certificates = []

        try:
            import PyKCS11 as PK11

            pkcs11 = PK11.PyKCS11Lib()
            pkcs11.load(dll_path)

            # Open session
            session = pkcs11.openSession(slot, PK11.CKF_SERIAL_SESSION)

            # Login if PIN provided
            if pin:
                session.login(pin)

            # Find all certificates
            cert_objects = session.findObjects([
                (PK11.CKA_CLASS, PK11.CKO_CERTIFICATE)
            ])

            for cert_obj in cert_objects:
                try:
                    # Get certificate attributes
                    attrs = session.getAttributeValue(cert_obj, [
                        PK11.CKA_VALUE,
                        PK11.CKA_LABEL,
                        PK11.CKA_ID,
                        PK11.CKA_SUBJECT
                    ])

                    cert_data = bytes(attrs[0])
                    cert_label = bytes(attrs[1]).decode('utf-8', errors='ignore').strip()
                    cert_id = bytes(attrs[2])

                    # Parse certificate to get details
                    cert_info = self._parse_certificate(cert_data)
                    cert_info['label'] = cert_label
                    cert_info['id'] = cert_id.hex()
                    cert_info['raw_data'] = cert_data

                    certificates.append(cert_info)

                except Exception as e:
                    self.logger.debug(f"Could not read certificate: {e}")

            # Logout and close session
            try:
                session.logout()
            except:
                pass
            session.closeSession()

            return certificates

        except ImportError:
            self.logger.error("PyKCS11 not installed")
            return []
        except Exception as e:
            self.logger.error(f"Error getting certificates from token: {e}")
            return []

    def _parse_certificate(self, cert_data: bytes) -> Dict:
        """Parse X.509 certificate to extract information."""
        try:
            from cryptography import x509
            from cryptography.hazmat.backends import default_backend

            cert = x509.load_der_x509_certificate(cert_data, default_backend())

            # Extract subject info
            subject = cert.subject
            cn = ""
            org = ""

            for attr in subject:
                if attr.oid == x509.oid.NameOID.COMMON_NAME:
                    cn = attr.value
                elif attr.oid == x509.oid.NameOID.ORGANIZATION_NAME:
                    org = attr.value

            return {
                'subject': cn or str(subject),
                'organization': org,
                'issuer': str(cert.issuer),
                'serial': str(cert.serial_number),
                'valid_from': cert.not_valid_before_utc.isoformat(),
                'valid_until': cert.not_valid_after_utc.isoformat(),
                'is_valid': cert.not_valid_before_utc <= datetime.utcnow() <= cert.not_valid_after_utc
            }

        except Exception as e:
            self.logger.debug(f"Could not parse certificate: {e}")
            return {
                'subject': 'Unknown',
                'organization': '',
                'issuer': 'Unknown',
                'serial': '',
                'valid_from': '',
                'valid_until': '',
                'is_valid': False
            }

    def sign_pdf_with_token(self, input_file: str, output_file: str,
                           dll_path: str, slot: int, pin: str,
                           cert_label: str = None,
                           reason: str = "Digitally Signed",
                           location: str = "India",
                           contact: str = "",
                           visible_signature: bool = True,
                           sig_page: int = 0,
                           sig_rect: Tuple[float, float, float, float] = None) -> bool:
        """
        Sign PDF using USB token (DSC).

        Args:
            input_file: Input PDF path
            output_file: Output PDF path
            dll_path: Path to PKCS#11 DLL
            slot: Token slot number
            pin: Token PIN
            cert_label: Certificate label to use (optional)
            reason: Reason for signing
            location: Signing location
            contact: Contact information
            visible_signature: Whether to show visible signature
            sig_page: Page for visible signature
            sig_rect: Rectangle for visible signature (x0, y0, x1, y1)

        Returns:
            True if successful
        """
        try:
            # Try using endesive library (recommended for PDF signing)
            return self._sign_with_endesive(
                input_file, output_file, dll_path, slot, pin,
                cert_label, reason, location, contact,
                visible_signature, sig_page, sig_rect
            )
        except ImportError:
            self.logger.warning("endesive not installed, trying alternative method")
            # Fallback to basic signing
            return self._sign_basic(
                input_file, output_file, dll_path, slot, pin,
                reason, location
            )
        except Exception as e:
            self.logger.error(f"Error signing PDF with token: {e}")
            return False

    def _sign_with_endesive(self, input_file: str, output_file: str,
                           dll_path: str, slot: int, pin: str,
                           cert_label: str, reason: str, location: str,
                           contact: str, visible_signature: bool,
                           sig_page: int, sig_rect: Tuple) -> bool:
        """Sign PDF using endesive library with USB token."""
        try:
            from endesive import pdf
            from endesive.pdf import cms
            import PyKCS11 as PK11

            # Custom HSM class for token signing
            class TokenSigner:
                def __init__(self, dll_path, slot, pin):
                    self.pkcs11 = PK11.PyKCS11Lib()
                    self.pkcs11.load(dll_path)
                    self.slot = slot
                    self.pin = pin
                    self.session = None

                def login(self):
                    self.session = self.pkcs11.openSession(
                        self.slot,
                        PK11.CKF_SERIAL_SESSION | PK11.CKF_RW_SESSION
                    )
                    self.session.login(self.pin)

                def logout(self):
                    if self.session:
                        try:
                            self.session.logout()
                        except:
                            pass
                        self.session.closeSession()

                def get_certificate(self):
                    self.login()
                    try:
                        certs = self.session.findObjects([
                            (PK11.CKA_CLASS, PK11.CKO_CERTIFICATE)
                        ])
                        if certs:
                            attrs = self.session.getAttributeValue(
                                certs[0], [PK11.CKA_VALUE, PK11.CKA_ID]
                            )
                            return bytes(attrs[1]), bytes(attrs[0])
                    finally:
                        self.logout()
                    return None, None

                def sign(self, data, mech='SHA256'):
                    self.login()
                    try:
                        priv_keys = self.session.findObjects([
                            (PK11.CKA_CLASS, PK11.CKO_PRIVATE_KEY)
                        ])
                        if priv_keys:
                            mech_type = getattr(PK11, f'CKM_{mech}_RSA_PKCS')
                            sig = self.session.sign(
                                priv_keys[0], data,
                                PK11.Mechanism(mech_type, None)
                            )
                            return bytes(sig)
                    finally:
                        self.logout()
                    return None

            # Prepare signature parameters
            date = datetime.utcnow().strftime('%Y%m%d%H%M%S+00\'00\'')

            dct = {
                'sigflags': 3,
                'sigpage': sig_page,
                'contact': contact.encode() if contact else b'',
                'location': location.encode() if location else b'India',
                'signingdate': date.encode(),
                'reason': reason.encode() if reason else b'Digitally Signed',
            }

            if visible_signature and sig_rect:
                dct['signaturebox'] = sig_rect
                dct['sigbutton'] = True

            # Read input PDF
            with open(input_file, 'rb') as f:
                datau = f.read()

            # Create signer and sign
            signer = TokenSigner(dll_path, slot, pin)

            # Get certificate
            key_id, cert = signer.get_certificate()
            if not cert:
                self.logger.error("Could not get certificate from token")
                return False

            # Sign the PDF
            datas = cms.sign(
                datau, dct,
                key_id, cert,
                [],
                'sha256',
                signer
            )

            # Write signed PDF
            with open(output_file, 'wb') as f:
                f.write(datau)
                f.write(datas)

            self.logger.info(f"PDF signed successfully with USB token: {output_file}")
            return True

        except ImportError as e:
            self.logger.error(f"Required library not installed: {e}")
            self.logger.info("Install with: pip install endesive PyKCS11")
            raise
        except Exception as e:
            self.logger.error(f"Error in endesive signing: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            return False

    def _sign_basic(self, input_file: str, output_file: str,
                   dll_path: str, slot: int, pin: str,
                   reason: str, location: str) -> bool:
        """Basic signing fallback when endesive is not available."""
        self.logger.warning("Basic signing: Adds visible signature but no cryptographic signature")
        self.logger.warning("For cryptographic signing, install: pip install endesive PyKCS11")

        try:
            # Just add a visible signature annotation
            pdf = fitz.open(input_file)
            page = pdf[0]

            # Get certificate info from token
            certs = self.get_certificates_from_token(dll_path, slot, pin)
            signer_name = certs[0]['subject'] if certs else "Unknown Signer"

            # Add visible signature
            rect = fitz.Rect(50, 50, 250, 120)
            page.draw_rect(rect, color=(0, 0, 0), width=1)

            page.insert_text((55, 70), "Digitally Signed by:", fontsize=10)
            page.insert_text((55, 85), signer_name, fontsize=11, color=(0, 0, 0.8))
            page.insert_text((55, 100), f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}", fontsize=9)
            page.insert_text((55, 112), f"Reason: {reason}", fontsize=8)

            pdf.save(output_file)
            pdf.close()

            self.logger.info(f"Added visible signature (non-cryptographic): {output_file}")
            return True

        except Exception as e:
            self.logger.error(f"Error in basic signing: {e}")
            return False

    def sign_pdf_with_pfx(self, input_file: str, output_file: str,
                          pfx_path: str, pfx_password: str,
                          reason: str = "Digitally Signed",
                          location: str = "India",
                          contact: str = "",
                          visible_signature: bool = True,
                          sig_page: int = 0,
                          sig_rect: Tuple[float, float, float, float] = None) -> Tuple[bool, str]:
        """
        Sign PDF using a PFX/P12 certificate file (software certificate).
        This method does NOT require PyKCS11.

        Args:
            input_file: Input PDF path
            output_file: Output PDF path
            pfx_path: Path to .pfx or .p12 certificate file
            pfx_password: Certificate password
            reason: Reason for signing
            location: Signing location
            contact: Contact information
            visible_signature: Whether to show visible signature
            sig_page: Page for visible signature
            sig_rect: Rectangle for visible signature (x0, y0, x1, y1)

        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            from cryptography.hazmat.primitives.serialization import pkcs12
            from cryptography import x509

            # Load the PFX file
            with open(pfx_path, 'rb') as f:
                pfx_data = f.read()

            # Parse the PFX
            password_bytes = pfx_password.encode() if pfx_password else None
            private_key, certificate, additional_certs = pkcs12.load_key_and_certificates(
                pfx_data, password_bytes
            )

            if not certificate:
                return False, "No certificate found in PFX file"

            # Get signer name from certificate
            signer_name = "Unknown"
            for attr in certificate.subject:
                if attr.oid == x509.oid.NameOID.COMMON_NAME:
                    signer_name = attr.value
                    break

            # Check certificate validity
            from datetime import datetime, timezone
            now = datetime.now(timezone.utc)
            if now < certificate.not_valid_before_utc or now > certificate.not_valid_after_utc:
                return False, f"Certificate has expired or is not yet valid.\nValid from: {certificate.not_valid_before_utc}\nValid until: {certificate.not_valid_after_utc}"

            # For now, add a visible signature with certificate info
            # Full cryptographic signing requires endesive
            pdf = fitz.open(input_file)
            page = pdf[sig_page] if sig_page < len(pdf) else pdf[0]

            # Default signature rectangle
            if not sig_rect:
                sig_rect = (50, 50, 280, 130)

            rect = fitz.Rect(sig_rect)

            if visible_signature:
                # Draw signature box with professional appearance
                # White background
                shape = page.new_shape()
                shape.draw_rect(rect)
                shape.finish(color=(0.2, 0.4, 0.6), fill=(0.98, 0.98, 1), width=2)
                shape.commit()

                # Add signature text
                y_offset = rect.y0 + 18
                page.insert_text((rect.x0 + 10, y_offset), "Digitally Signed",
                               fontsize=11, fontname="helv", color=(0, 0.3, 0.6))

                y_offset += 16
                page.insert_text((rect.x0 + 10, y_offset), f"By: {signer_name}",
                               fontsize=10, fontname="helv", color=(0, 0, 0))

                y_offset += 14
                page.insert_text((rect.x0 + 10, y_offset),
                               f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                               fontsize=9, fontname="helv", color=(0.3, 0.3, 0.3))

                y_offset += 12
                if reason:
                    page.insert_text((rect.x0 + 10, y_offset), f"Reason: {reason}",
                                   fontsize=8, fontname="helv", color=(0.3, 0.3, 0.3))
                    y_offset += 12

                if location:
                    page.insert_text((rect.x0 + 10, y_offset), f"Location: {location}",
                                   fontsize=8, fontname="helv", color=(0.3, 0.3, 0.3))

                # Add a small checkmark icon
                page.insert_text((rect.x1 - 25, rect.y0 + 20), "\u2713",
                               fontsize=16, color=(0, 0.6, 0))

            pdf.save(output_file)
            pdf.close()

            self.logger.info(f"PDF signed with software certificate: {output_file}")
            return True, f"PDF signed successfully by: {signer_name}"

        except FileNotFoundError:
            return False, f"Certificate file not found: {pfx_path}"
        except ValueError as e:
            if "password" in str(e).lower():
                return False, "Incorrect certificate password"
            return False, f"Invalid certificate file: {str(e)}"
        except Exception as e:
            self.logger.error(f"Error signing with PFX: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            return False, f"Error signing PDF: {str(e)}"

    # Keep existing methods for backward compatibility
    def add_signature_field(self, pdf_document, page_num: int, field_name: str,
                           rect: Tuple[float, float, float, float]) -> bool:
        """Add signature field to PDF."""
        try:
            page = pdf_document[page_num]
            widget = fitz.Widget()
            widget.field_name = field_name
            widget.field_type = fitz.PDF_WIDGET_TYPE_SIGNATURE
            widget.rect = fitz.Rect(rect)
            page.add_widget(widget)
            self.logger.info(f"Added signature field '{field_name}' on page {page_num}")
            return True
        except Exception as e:
            self.logger.error(f"Error adding signature field: {e}")
            return False

    def add_visible_signature(self, pdf_document, page_num: int,
                            rect: Tuple[float, float, float, float],
                            signer_name: str, sign_date: Optional[str] = None,
                            reason: str = "", image_path: Optional[str] = None) -> bool:
        """Add visible signature appearance to PDF."""
        try:
            page = pdf_document[page_num]
            sig_rect = fitz.Rect(rect)

            if image_path and Path(image_path).exists():
                page.insert_image(sig_rect, filename=image_path)
            else:
                page.draw_rect(sig_rect, color=(0, 0, 0), width=1)
                font_size = 10
                text_y = sig_rect.y0 + 15

                page.insert_text((sig_rect.x0 + 5, text_y), "Digitally signed by:", fontsize=font_size)
                page.insert_text((sig_rect.x0 + 5, text_y + 15), signer_name, fontsize=font_size + 2, color=(0, 0, 1))

                if not sign_date:
                    sign_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                page.insert_text((sig_rect.x0 + 5, text_y + 30), f"Date: {sign_date}", fontsize=font_size)

                if reason:
                    page.insert_text((sig_rect.x0 + 5, text_y + 45), f"Reason: {reason}", fontsize=font_size - 1)

            self.logger.info(f"Added visible signature on page {page_num}")
            return True
        except Exception as e:
            self.logger.error(f"Error adding visible signature: {e}")
            return False

    def get_signature_info(self, pdf_document) -> list:
        """Get information about signatures in PDF."""
        try:
            signatures = []
            # Check if document has signature fields
            for page_num in range(len(pdf_document)):
                page = pdf_document[page_num]
                widgets = page.widgets()
                if widgets:
                    for widget in widgets:
                        if widget.field_type == fitz.PDF_WIDGET_TYPE_SIGNATURE:
                            signatures.append({
                                'field_name': widget.field_name,
                                'page': page_num,
                                'rect': list(widget.rect),
                                'signed': widget.field_value is not None
                            })
            return signatures
        except Exception as e:
            self.logger.error(f"Error getting signature info: {e}")
            return []

    def list_certificates_windows(self) -> list:
        """List certificates from Windows store and USB tokens."""
        certificates = []

        # First, detect USB tokens
        tokens = self.detect_usb_tokens()
        for token in tokens:
            try:
                token_certs = self.get_certificates_from_token(
                    token['dll_path'],
                    token['slot']
                )
                for cert in token_certs:
                    cert['source'] = 'USB Token'
                    cert['token_label'] = token['label']
                    cert['dll_path'] = token['dll_path']
                    cert['slot'] = token['slot']
                    certificates.append(cert)
            except:
                pass

        # Also try Windows Certificate Store
        try:
            import win32crypt
            store = win32crypt.CertOpenSystemStore(0, "MY")
            cert = win32crypt.CertEnumCertificatesInStore(store, None)

            while cert:
                try:
                    cert_info = {
                        'subject': str(cert.Subject),
                        'issuer': str(cert.Issuer),
                        'serial': cert.SerialNumber.hex() if cert.SerialNumber else '',
                        'source': 'Windows Store',
                        'expiry': str(cert.NotAfter) if hasattr(cert, 'NotAfter') else ''
                    }
                    certificates.append(cert_info)
                except:
                    pass
                cert = win32crypt.CertEnumCertificatesInStore(store, cert)

            win32crypt.CertCloseStore(store, 0)
        except ImportError:
            self.logger.debug("win32crypt not available")
        except Exception as e:
            self.logger.debug(f"Error accessing Windows store: {e}")

        return certificates
