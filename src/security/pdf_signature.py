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
            # WatchData ProxKey - SignatureP11.dll is the primary PKCS#11 DLL
            r'C:\Windows\System32\SignatureP11.dll',
            r'C:\Windows\SysWOW64\SignatureP11.dll',
            r'C:\Windows\System32\wdpkcs.dll',
            r'C:\Windows\SysWOW64\wdpkcs.dll',
            r'C:\Program Files\Watchdata\ProxKey\wdpkcs.dll',
            r'C:\Program Files (x86)\Watchdata\ProxKey\wdpkcs.dll',
            r'C:\Program Files\Watchdata\WD PROXKey\SignatureP11.dll',
            r'C:\Program Files (x86)\Watchdata\WD PROXKey\SignatureP11.dll',
            r'C:\Program Files\ProxKey\SignatureP11.dll',
            r'C:\Program Files (x86)\ProxKey\SignatureP11.dll',
            # eMudhra
            r'C:\Windows\System32\emlogiN_PKCS11.dll',
            r'C:\Windows\SysWOW64\emlogiN_PKCS11.dll',
            # Safenet/Gemalto
            r'C:\Windows\System32\eTPKCS11.dll',
            r'C:\Windows\SysWOW64\eTPKCS11.dll',
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
                "2. Then run: pip install PyKCS11 endesive"
            )

    def _discover_token_dlls(self) -> List[str]:
        """
        Dynamically discover PKCS#11 DLL paths beyond the static list.
        Searches registry and common installation directories.
        """
        discovered = []

        if sys.platform != 'win32':
            return discovered

        # Search common DLL names in System32
        pkcs11_dll_names = [
            'SignatureP11.dll', 'wdpkcs.dll', 'eps2003csp11.dll',
            'eTPKCS11.dll', 'emlogiN_PKCS11.dll', 'cryptoCertum3PKCS.dll',
        ]
        for sys_dir in [r'C:\Windows\System32', r'C:\Windows\SysWOW64']:
            for dll_name in pkcs11_dll_names:
                full_path = os.path.join(sys_dir, dll_name)
                if os.path.exists(full_path) and full_path not in discovered:
                    discovered.append(full_path)

        # Search common installation directories for ProxKey/Watchdata
        search_dirs = [
            r'C:\Program Files\Watchdata',
            r'C:\Program Files (x86)\Watchdata',
            r'C:\Program Files\ProxKey',
            r'C:\Program Files (x86)\ProxKey',
            r'C:\Program Files\WD PROXKey',
            r'C:\Program Files (x86)\WD PROXKey',
        ]
        pkcs11_extensions = {'SignatureP11.dll', 'wdpkcs.dll'}

        for search_dir in search_dirs:
            if os.path.isdir(search_dir):
                for root, dirs, files in os.walk(search_dir):
                    for f in files:
                        if f.lower() in {n.lower() for n in pkcs11_extensions}:
                            full_path = os.path.join(root, f)
                            if full_path not in discovered:
                                discovered.append(full_path)

        # Try reading Windows registry for ProxKey CSP info
        try:
            import winreg
            # Check for ProxKey smart card entries
            reg_paths = [
                (winreg.HKEY_LOCAL_MACHINE,
                 r'SOFTWARE\Microsoft\Cryptography\Calais\SmartCards'),
                (winreg.HKEY_LOCAL_MACHINE,
                 r'SOFTWARE\Wow6432Node\Microsoft\Cryptography\Calais\SmartCards'),
            ]
            for hive, reg_path in reg_paths:
                try:
                    key = winreg.OpenKey(hive, reg_path)
                    num_subkeys = winreg.QueryInfoKey(key)[0]
                    for i in range(num_subkeys):
                        subkey_name = winreg.EnumKey(key, i)
                        if 'prox' in subkey_name.lower() or 'watchdata' in subkey_name.lower():
                            try:
                                subkey = winreg.OpenKey(key, subkey_name)
                                # Try to read the PKCS11 DLL path
                                for val_name in ['Crypto Provider', 'PKCS11 Path', '80000001']:
                                    try:
                                        val, _ = winreg.QueryValueEx(subkey, val_name)
                                        if val and val.endswith('.dll') and os.path.exists(val):
                                            if val not in discovered:
                                                discovered.append(val)
                                    except FileNotFoundError:
                                        pass
                                winreg.CloseKey(subkey)
                            except Exception:
                                pass
                    winreg.CloseKey(key)
                except FileNotFoundError:
                    pass
        except Exception as e:
            self.logger.debug(f"Registry search failed: {e}")

        return discovered

    def detect_usb_tokens(self) -> List[Dict]:
        """
        Detect available USB tokens connected to the system.
        Reads X.509 certificate CN (person's name) from each token.

        Returns:
            List of detected tokens with their information including
            certificate holder's name from the X.509 certificate.
        """
        tokens = []
        seen_serials = set()  # Avoid duplicates from multiple DLLs

        try:
            import PyKCS11 as PK11

            # Get DLL paths for current platform
            if sys.platform == 'win32':
                dll_paths = list(self.TOKEN_DLLS['windows'])
                # Add dynamically discovered DLLs
                dynamic_dlls = self._discover_token_dlls()
                for dll in dynamic_dlls:
                    if dll not in dll_paths:
                        dll_paths.append(dll)
                self.logger.info(f"Searching {len(dll_paths)} PKCS#11 DLL paths")
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
                                serial = token_info.serialNumber.strip()

                                # Skip if we already found this token via another DLL
                                if serial in seen_serials:
                                    continue
                                seen_serials.add(serial)

                                token_label = token_info.label.strip()
                                manufacturer = token_info.manufacturerID.strip()

                                # Read certificate holder's name from the X.509
                                # certificate stored on the token
                                cert_holder_name = ""
                                cert_org = ""
                                cert_valid_from = ""
                                cert_valid_until = ""
                                cert_issuer = ""
                                try:
                                    cert_holder_name, cert_org, cert_valid_from, cert_valid_until, cert_issuer = \
                                        self._read_certificate_cn_from_token(
                                            pkcs11, slot, dll_path
                                        )
                                except Exception as e:
                                    self.logger.debug(
                                        f"Could not read certificate from token "
                                        f"{token_label}: {e}"
                                    )

                                # Use certificate CN as primary display name,
                                # fall back to token label only if cert read fails
                                display_name = cert_holder_name or token_label

                                tokens.append({
                                    'slot': slot,
                                    'label': token_label,
                                    'display_name': display_name,
                                    'cert_holder': cert_holder_name,
                                    'cert_org': cert_org,
                                    'cert_issuer': cert_issuer,
                                    'cert_valid_from': cert_valid_from,
                                    'cert_valid_until': cert_valid_until,
                                    'manufacturer': manufacturer,
                                    'model': token_info.model.strip(),
                                    'serial': serial,
                                    'dll_path': dll_path,
                                    'flags': token_info.flags
                                })
                                self.logger.info(
                                    f"Found token: {token_label} | "
                                    f"Certificate holder: {cert_holder_name or 'N/A'}"
                                )
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

    def _read_certificate_cn_from_token(self, pkcs11, slot: int,
                                         dll_path: str) -> Tuple[str, str, str, str, str]:
        """
        Open a read-only PKCS#11 session (no PIN needed) to read the
        X.509 certificate and extract the holder's Common Name (CN).

        Returns:
            Tuple of (common_name, organization, valid_from, valid_until, issuer)
        """
        import PyKCS11 as PK11

        session = pkcs11.openSession(slot, PK11.CKF_SERIAL_SESSION)
        try:
            # Find certificate objects (public, no login needed)
            cert_objects = session.findObjects([
                (PK11.CKA_CLASS, PK11.CKO_CERTIFICATE)
            ])

            for cert_obj in cert_objects:
                try:
                    attrs = session.getAttributeValue(cert_obj, [PK11.CKA_VALUE])
                    cert_data = bytes(attrs[0])

                    if not cert_data:
                        continue

                    # Parse X.509 certificate to get CN
                    info = self._parse_certificate(cert_data)
                    cn = info.get('subject', '')
                    org = info.get('organization', '')
                    valid_from = info.get('valid_from', '')
                    valid_until = info.get('valid_until', '')
                    issuer = info.get('issuer', '')

                    if cn and cn != 'Unknown':
                        self.logger.info(f"Certificate CN: {cn}, Org: {org}")
                        return cn, org, valid_from, valid_until, issuer
                except Exception as e:
                    self.logger.debug(f"Could not read cert object: {e}")
                    continue

            return "", "", "", "", ""
        finally:
            session.closeSession()

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
                           token_label: str = "",
                           cert_label: str = None,
                           reason: str = "Digitally Signed",
                           location: str = "India",
                           contact: str = "",
                           visible_signature: bool = True,
                           sig_page: int = 0,
                           sig_rect: Tuple[float, float, float, float] = None) -> Tuple[bool, str]:
        """
        Sign PDF using USB token (DSC).

        Args:
            input_file: Input PDF path
            output_file: Output PDF path
            dll_path: Path to PKCS#11 DLL
            slot: Token slot number
            pin: Token PIN
            token_label: Token label (from detect_usb_tokens)
            cert_label: Certificate label to use (optional)
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
            return self._sign_with_endesive(
                input_file, output_file, dll_path, slot, pin,
                token_label, cert_label, reason, location, contact,
                visible_signature, sig_page, sig_rect
            )
        except ImportError as e:
            self.logger.warning(f"endesive not available: {e}")
            return False, (
                "Digital signature library (endesive) is not available.\n\n"
                "Please install it with: pip install endesive\n\n"
                "Without endesive, cryptographic PDF signing is not possible."
            )
        except Exception as e:
            self.logger.error(f"Error signing PDF with token: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            return False, f"Signing failed: {str(e)}"

    def _sign_with_endesive(self, input_file: str, output_file: str,
                           dll_path: str, slot: int, pin: str,
                           token_label: str, cert_label: str,
                           reason: str, location: str,
                           contact: str, visible_signature: bool,
                           sig_page: int, sig_rect: Tuple) -> Tuple[bool, str]:
        """Sign PDF using endesive library with USB token (proper PKCS#11)."""
        from endesive import pdf, hsm
        from endesive.pdf import cms
        import PyKCS11 as PK11

        # Get the token label for HSM login
        if not token_label:
            try:
                pkcs11 = PK11.PyKCS11Lib()
                pkcs11.load(dll_path)
                slots = pkcs11.getSlotList(tokenPresent=True)
                for s in slots:
                    info = pkcs11.getTokenInfo(s)
                    token_label = info.label.strip()
                    break
            except Exception as e:
                self.logger.warning(f"Could not get token label: {e}")
                token_label = ""

        # Create proper HSM signer class that extends endesive's HSM
        _pin = pin
        _logger = self.logger

        class TokenSigner(hsm.HSM):
            def certificate(self):
                self.login(token_label, _pin)
                try:
                    pk11objects = self.session.findObjects(
                        [(PK11.CKA_CLASS, PK11.CKO_CERTIFICATE)]
                    )
                    for pk11object in pk11objects:
                        try:
                            attributes = self.session.getAttributeValue(
                                pk11object, [PK11.CKA_VALUE, PK11.CKA_ID]
                            )
                            cert = bytes(attributes[0])
                            keyid = bytes(attributes[1])
                            return keyid, cert
                        except PK11.PyKCS11Error:
                            continue
                finally:
                    self.logout()
                return None, None

            def sign(self, keyid, data, mech):
                self.login(token_label, _pin)
                try:
                    privKey = self.session.findObjects(
                        [(PK11.CKA_CLASS, PK11.CKO_PRIVATE_KEY)]
                    )[0]
                    mech_type = getattr(PK11, 'CKM_%s_RSA_PKCS' % mech.upper())
                    sig = self.session.sign(
                        privKey, data, PK11.Mechanism(mech_type, None)
                    )
                    return bytes(sig)
                finally:
                    self.logout()

        # Create signer instance
        signer = TokenSigner(dll_path)

        # Get signer name from certificate
        signer_name = "Digital Signature"
        try:
            keyid, cert_der = signer.certificate()
            if cert_der:
                cert_info = self._parse_certificate(cert_der)
                signer_name = cert_info.get('subject', 'Digital Signature')
                _logger.info(f"Signing with certificate: {signer_name}")
        except Exception as e:
            _logger.warning(f"Could not read certificate name: {e}")

        # Prepare signature dictionary
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
            dct['signature'] = signer_name
            dct['sigbutton'] = True

        # Read input PDF
        with open(input_file, 'rb') as f:
            datau = f.read()

        # Sign the PDF using endesive with proper HSM
        datas = cms.sign(
            datau, dct,
            None, None,
            [],
            'sha256',
            signer,
        )

        # Write signed PDF
        with open(output_file, 'wb') as f:
            f.write(datau)
            f.write(datas)

        self.logger.info(f"PDF signed successfully by {signer_name}: {output_file}")
        return True, f"PDF signed successfully by: {signer_name}"

    def sign_pdf_with_pfx(self, input_file: str, output_file: str,
                          pfx_path: str, pfx_password: str,
                          reason: str = "Digitally Signed",
                          location: str = "India",
                          contact: str = "",
                          visible_signature: bool = True,
                          sig_page: int = 0,
                          sig_rect: Tuple[float, float, float, float] = None) -> Tuple[bool, str]:
        """
        Sign PDF using a PFX/P12 certificate file with endesive (real crypto signature).

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
            from cryptography.hazmat.backends import default_backend
            from cryptography import x509

            # Load the PFX file
            with open(pfx_path, 'rb') as f:
                pfx_data = f.read()

            # Parse the PFX
            password_bytes = pfx_password.encode() if pfx_password else None
            private_key, certificate, additional_certs = pkcs12.load_key_and_certificates(
                pfx_data, password_bytes, default_backend()
            )

            if not certificate or not private_key:
                return False, "No certificate or private key found in PFX file"

            # Get signer name from certificate
            signer_name = "Unknown"
            for attr in certificate.subject:
                if attr.oid == x509.oid.NameOID.COMMON_NAME:
                    signer_name = attr.value
                    break

            # Check certificate validity
            from datetime import datetime as dt, timezone
            now = dt.now(timezone.utc)
            if now < certificate.not_valid_before_utc or now > certificate.not_valid_after_utc:
                return False, (
                    f"Certificate has expired or is not yet valid.\n"
                    f"Valid from: {certificate.not_valid_before_utc}\n"
                    f"Valid until: {certificate.not_valid_after_utc}"
                )

            # Prepare signature dictionary
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
                dct['signature'] = signer_name
                dct['sigbutton'] = True

            # Read input PDF
            with open(input_file, 'rb') as f:
                datau = f.read()

            # Sign with endesive using PFX key and certificate
            from endesive.pdf import cms

            datas = cms.sign(
                datau, dct,
                private_key, certificate,
                additional_certs or [],
                'sha256',
            )

            # Write signed PDF
            with open(output_file, 'wb') as f:
                f.write(datau)
                f.write(datas)

            self.logger.info(f"PDF signed with PFX certificate by {signer_name}: {output_file}")
            return True, f"PDF signed successfully by: {signer_name}"

        except FileNotFoundError:
            return False, f"Certificate file not found: {pfx_path}"
        except ValueError as e:
            if "password" in str(e).lower():
                return False, "Incorrect certificate password"
            return False, f"Invalid certificate file: {str(e)}"
        except ImportError as e:
            return False, f"Required library not available: {str(e)}\nInstall with: pip install endesive"
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
