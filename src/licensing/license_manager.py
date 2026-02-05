"""
License Manager - Hardware-bound subscription licensing
"""

import hashlib
import uuid
import platform
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict
import requests
from cryptography.fernet import Fernet
from src.utilities.logger import get_logger


class LicenseManager:
    """Manage application licensing and validation"""

    def __init__(self, db_path: str = "data/license.db"):
        self.logger = get_logger()
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
        self._encryption_key = self._get_or_create_key()

    def _init_database(self):
        """Initialize license database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS licenses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    license_key TEXT UNIQUE NOT NULL,
                    hardware_id TEXT NOT NULL,
                    activation_date TEXT NOT NULL,
                    expiry_date TEXT NOT NULL,
                    last_validated TEXT,
                    status TEXT DEFAULT 'active',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS validation_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    license_key TEXT NOT NULL,
                    validation_time TEXT NOT NULL,
                    validation_result TEXT NOT NULL,
                    message TEXT
                )
            ''')

            conn.commit()
            conn.close()

        except Exception as e:
            self.logger.error(f"Error initializing license database: {e}")

    def _get_or_create_key(self) -> bytes:
        """Get or create encryption key"""
        key_file = self.db_path.parent / ".key"

        if key_file.exists():
            with open(key_file, 'rb') as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            with open(key_file, 'wb') as f:
                f.write(key)
            return key

    def get_hardware_id(self) -> str:
        """
        Generate hardware ID based on machine characteristics

        Returns:
            Hardware ID string
        """
        try:
            # Collect hardware information
            machine_id = str(uuid.getnode())  # MAC address
            processor = platform.processor()
            system = platform.system()
            machine = platform.machine()

            # Combine and hash
            hw_string = f"{machine_id}-{processor}-{system}-{machine}"
            hw_hash = hashlib.sha256(hw_string.encode()).hexdigest()

            return hw_hash[:32]  # First 32 characters

        except Exception as e:
            self.logger.error(f"Error generating hardware ID: {e}")
            # Fallback to UUID
            return str(uuid.uuid4())[:32]

    def activate_license(self, license_key: str, online: bool = True) -> Dict:
        """
        Activate license key

        Args:
            license_key: License key from user
            online: Whether to validate online

        Returns:
            Dictionary with activation result
        """
        try:
            hardware_id = self.get_hardware_id()

            # Validate with server if online
            if online:
                validation_result = self._validate_with_server(license_key, hardware_id)

                if not validation_result['valid']:
                    return {
                        'success': False,
                        'message': validation_result.get('message', 'Invalid license key')
                    }

                expiry_date = validation_result.get('expiry_date')
            else:
                # Offline activation - basic validation
                if not self._validate_key_format(license_key):
                    return {
                        'success': False,
                        'message': 'Invalid license key format'
                    }

                # Default 1 year expiry for offline activation
                expiry_date = (datetime.now() + timedelta(days=365)).isoformat()

            # Store license
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                INSERT OR REPLACE INTO licenses
                (license_key, hardware_id, activation_date, expiry_date, last_validated, status)
                VALUES (?, ?, ?, ?, ?, 'active')
            ''', (
                self._encrypt(license_key),
                hardware_id,
                datetime.now().isoformat(),
                expiry_date,
                datetime.now().isoformat()
            ))

            conn.commit()
            conn.close()

            self._log_validation(license_key, 'SUCCESS', 'License activated')

            return {
                'success': True,
                'message': 'License activated successfully',
                'expiry_date': expiry_date
            }

        except Exception as e:
            self.logger.error(f"Error activating license: {e}")
            return {
                'success': False,
                'message': f'Activation error: {str(e)}'
            }

    def validate_license(self, force_online: bool = False) -> Dict:
        """
        Validate current license

        Args:
            force_online: Force online validation

        Returns:
            Dictionary with validation result
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Get active license
            cursor.execute('''
                SELECT license_key, hardware_id, expiry_date, last_validated, status
                FROM licenses
                WHERE status = 'active'
                ORDER BY activation_date DESC
                LIMIT 1
            ''')

            result = cursor.fetchone()
            conn.close()

            if not result:
                return {
                    'valid': False,
                    'message': 'No active license found',
                    'requires_activation': True
                }

            enc_license_key, hardware_id, expiry_date, last_validated, status = result
            license_key = self._decrypt(enc_license_key)

            # Check hardware ID
            current_hw_id = self.get_hardware_id()
            if hardware_id != current_hw_id:
                self._log_validation(license_key, 'FAILED', 'Hardware ID mismatch')
                return {
                    'valid': False,
                    'message': 'License not valid for this machine',
                    'requires_activation': True
                }

            # Check expiry
            expiry_dt = datetime.fromisoformat(expiry_date)
            if datetime.now() > expiry_dt:
                self._deactivate_license(license_key)
                return {
                    'valid': False,
                    'message': 'License expired',
                    'expired': True,
                    'expiry_date': expiry_date
                }

            # Check if revalidation needed
            last_val_dt = datetime.fromisoformat(last_validated) if last_validated else None
            needs_revalidation = (
                force_online or
                not last_val_dt or
                (datetime.now() - last_val_dt) > timedelta(hours=24)
            )

            if needs_revalidation:
                online_result = self._validate_with_server(license_key, hardware_id)

                if online_result['valid']:
                    self._update_validation_time(license_key)
                    self._log_validation(license_key, 'SUCCESS', 'Online validation successful')
                else:
                    # Check grace period
                    grace_period_days = 7
                    grace_end = last_val_dt + timedelta(days=grace_period_days) if last_val_dt else datetime.now()

                    if datetime.now() > grace_end:
                        return {
                            'valid': False,
                            'message': 'License validation failed and grace period expired',
                            'requires_activation': True
                        }

                    # Still in grace period
                    days_remaining = (grace_end - datetime.now()).days
                    return {
                        'valid': True,
                        'message': f'Grace period: {days_remaining} days remaining',
                        'grace_mode': True,
                        'days_remaining': days_remaining
                    }

            return {
                'valid': True,
                'message': 'License valid',
                'expiry_date': expiry_date,
                'days_until_expiry': (expiry_dt - datetime.now()).days
            }

        except Exception as e:
            self.logger.error(f"Error validating license: {e}")
            return {
                'valid': False,
                'message': f'Validation error: {str(e)}'
            }

    def _validate_with_server(self, license_key: str, hardware_id: str) -> Dict:
        """
        Validate license with remote server

        Args:
            license_key: License key
            hardware_id: Hardware ID

        Returns:
            Validation result
        """
        try:
            # In production, this would connect to actual licensing server
            # For now, return mock validation

            # Example server validation
            # response = requests.post(
            #     "https://licensing.nexpro.com/validate",
            #     json={
            #         'license_key': license_key,
            #         'hardware_id': hardware_id,
            #         'product': 'NexPro PDF'
            #     },
            #     timeout=10
            # )
            #
            # if response.status_code == 200:
            #     return response.json()

            # Mock validation for development
            if self._validate_key_format(license_key):
                return {
                    'valid': True,
                    'message': 'License valid',
                    'expiry_date': (datetime.now() + timedelta(days=365)).isoformat()
                }
            else:
                return {
                    'valid': False,
                    'message': 'Invalid license key'
                }

        except requests.RequestException as e:
            self.logger.error(f"Server validation failed: {e}")
            return {
                'valid': False,
                'message': 'Unable to connect to licensing server'
            }
        except Exception as e:
            self.logger.error(f"Error in server validation: {e}")
            return {
                'valid': False,
                'message': str(e)
            }

    def _validate_key_format(self, license_key: str) -> bool:
        """Validate license key format"""
        # Example format: XXXX-XXXX-XXXX-XXXX
        parts = license_key.split('-')
        return len(parts) == 4 and all(len(p) == 4 for p in parts)

    def _deactivate_license(self, license_key: str):
        """Deactivate license"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                UPDATE licenses
                SET status = 'expired'
                WHERE license_key = ?
            ''', (self._encrypt(license_key),))

            conn.commit()
            conn.close()

            self._log_validation(license_key, 'DEACTIVATED', 'License deactivated')

        except Exception as e:
            self.logger.error(f"Error deactivating license: {e}")

    def _update_validation_time(self, license_key: str):
        """Update last validation time"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                UPDATE licenses
                SET last_validated = ?
                WHERE license_key = ?
            ''', (datetime.now().isoformat(), self._encrypt(license_key)))

            conn.commit()
            conn.close()

        except Exception as e:
            self.logger.error(f"Error updating validation time: {e}")

    def _log_validation(self, license_key: str, result: str, message: str):
        """Log validation attempt"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO validation_log
                (license_key, validation_time, validation_result, message)
                VALUES (?, ?, ?, ?)
            ''', (
                self._encrypt(license_key),
                datetime.now().isoformat(),
                result,
                message
            ))

            conn.commit()
            conn.close()

        except Exception as e:
            self.logger.error(f"Error logging validation: {e}")

    def _encrypt(self, data: str) -> str:
        """Encrypt sensitive data"""
        try:
            f = Fernet(self._encryption_key)
            return f.encrypt(data.encode()).decode()
        except:
            return data

    def _decrypt(self, data: str) -> str:
        """Decrypt sensitive data"""
        try:
            f = Fernet(self._encryption_key)
            return f.decrypt(data.encode()).decode()
        except:
            return data

    def get_license_info(self) -> Optional[Dict]:
        """Get current license information"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                SELECT activation_date, expiry_date, status
                FROM licenses
                WHERE status = 'active'
                ORDER BY activation_date DESC
                LIMIT 1
            ''')

            result = cursor.fetchone()
            conn.close()

            if result:
                activation_date, expiry_date, status = result
                return {
                    'activation_date': activation_date,
                    'expiry_date': expiry_date,
                    'status': status,
                    'hardware_id': self.get_hardware_id()
                }

            return None

        except Exception as e:
            self.logger.error(f"Error getting license info: {e}")
            return None
