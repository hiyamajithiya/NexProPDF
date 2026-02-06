"""
License Manager for NexPro PDF
Manages trial period and subscription validation
"""

import os
import json
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from cryptography.fernet import Fernet
import base64


class LicenseManager:
    """Manages application licensing and trial period"""

    TRIAL_DAYS = 180  # 6 months trial period
    LICENSE_FILE = "nexpro_license.dat"

    def __init__(self):
        # Get app data directory
        if os.name == 'nt':  # Windows
            app_data = os.path.join(os.environ.get('APPDATA', ''), 'NexProPDF')
        else:  # macOS/Linux
            app_data = os.path.join(os.path.expanduser('~'), '.nexpropdf')

        os.makedirs(app_data, exist_ok=True)
        self.license_path = os.path.join(app_data, self.LICENSE_FILE)
        self.cipher_key = self._generate_machine_key()

    def _generate_machine_key(self):
        """Generate encryption key based on machine"""
        # Use machine-specific information
        machine_id = os.environ.get('COMPUTERNAME', '') + os.environ.get('USERNAME', '')
        key_material = hashlib.sha256(machine_id.encode()).digest()
        return base64.urlsafe_b64encode(key_material)

    def _encrypt_data(self, data: dict) -> bytes:
        """Encrypt license data"""
        cipher = Fernet(self.cipher_key)
        json_data = json.dumps(data)
        return cipher.encrypt(json_data.encode())

    def _decrypt_data(self, encrypted_data: bytes) -> dict:
        """Decrypt license data"""
        try:
            cipher = Fernet(self.cipher_key)
            decrypted = cipher.decrypt(encrypted_data)
            return json.loads(decrypted.decode())
        except:
            return None

    def initialize_trial(self):
        """Initialize trial period on first run"""
        if not os.path.exists(self.license_path):
            license_data = {
                'install_date': datetime.now().isoformat(),
                'type': 'trial',
                'status': 'active'
            }
            encrypted = self._encrypt_data(license_data)
            with open(self.license_path, 'wb') as f:
                f.write(encrypted)
            return True
        return False

    def get_license_info(self) -> dict:
        """Get current license information"""
        if not os.path.exists(self.license_path):
            self.initialize_trial()

        try:
            with open(self.license_path, 'rb') as f:
                encrypted = f.read()
            return self._decrypt_data(encrypted)
        except:
            return None

    def check_license_validity(self) -> tuple:
        """
        Check if license is valid
        Returns: (is_valid: bool, days_remaining: int, message: str)
        """
        license_info = self.get_license_info()

        if not license_info:
            return False, 0, "License file corrupted. Please contact support."

        # Check if subscription is active
        if license_info.get('type') == 'subscription':
            expiry_date = datetime.fromisoformat(license_info.get('expiry_date'))
            if datetime.now() > expiry_date:
                return False, 0, "Your subscription has expired. Please renew."

            days_remaining = (expiry_date - datetime.now()).days
            return True, days_remaining, f"Subscription valid. {days_remaining} days remaining."

        # Check trial period
        install_date = datetime.fromisoformat(license_info.get('install_date'))
        expiry_date = install_date + timedelta(days=self.TRIAL_DAYS)
        days_remaining = (expiry_date - datetime.now()).days

        if days_remaining <= 0:
            return False, 0, "Your 180-day trial has expired. Please purchase a subscription."

        if days_remaining <= 30:
            return True, days_remaining, f"Trial expires in {days_remaining} days. Consider purchasing now."

        return True, days_remaining, f"Trial active. {days_remaining} days remaining."

    def activate_subscription(self, license_key: str) -> tuple:
        """
        Activate subscription with license key
        Returns: (success: bool, message: str)
        """
        # Validate license key format (example: NEXPRO-XXXXX-XXXXX-XXXXX-XXXXX)
        if not license_key or not license_key.startswith('NEXPRO-'):
            return False, "Invalid license key format."

        # In a real implementation, you would validate this with a server
        # For now, we'll do basic validation
        parts = license_key.split('-')
        if len(parts) != 5 or parts[0] != 'NEXPRO':
            return False, "Invalid license key."

        # Check if it's a valid key (in real app, check with activation server)
        if self._validate_license_key(license_key):
            # Activate for 1 year
            license_data = {
                'install_date': datetime.now().isoformat(),
                'type': 'subscription',
                'status': 'active',
                'license_key': license_key,
                'expiry_date': (datetime.now() + timedelta(days=365)).isoformat()
            }

            encrypted = self._encrypt_data(license_data)
            with open(self.license_path, 'wb') as f:
                f.write(encrypted)

            return True, "Subscription activated successfully! Valid for 1 year."
        else:
            return False, "Invalid or already used license key."

    def _validate_license_key(self, license_key: str) -> bool:
        """
        Validate license key
        In production, this would call an activation server
        """
        # Simple checksum validation for demo
        parts = license_key.split('-')
        if len(parts) != 5:
            return False

        # Check if key format is correct
        try:
            # In real implementation: verify with activation server
            # For demo: accept keys where all segments are 5 alphanumeric chars
            for i in range(1, 5):
                if len(parts[i]) != 5 or not parts[i].isalnum():
                    return False
            return True
        except:
            return False

    def generate_trial_key(self) -> str:
        """Generate a trial extension key (for support purposes)"""
        import random
        import string

        segments = []
        for _ in range(4):
            segment = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
            segments.append(segment)

        return f"NEXPRO-{'-'.join(segments)}"

    def get_contact_info(self) -> dict:
        """Get contact information for purchasing subscription"""
        return {
            'email': 'support@himanshumajithiya.com',
            'phone': '+91-XXXXXXXXXX',
            'website': 'www.himanshumajithiya.com',
            'whatsapp': '+91-XXXXXXXXXX'
        }
