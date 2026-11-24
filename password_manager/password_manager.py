import json
import os
from cryptography.fernet import Fernet
from pathlib import Path


class PasswordManager:
    """A simple password manager with encryption."""
    
    def __init__(self, master_password, storage_file="passwords.json", key_file="encryption.key"):
        self.storage_file = storage_file
        self.key_file = key_file
        self.master_password = master_password
        self.cipher = None
        self._setup_encryption()
        self.passwords = self._load_passwords()
    
    def _setup_encryption(self):
        """Setup encryption key or load existing one."""
        if os.path.exists(self.key_file):
            with open(self.key_file, 'rb') as f:
                key = f.read()
        else:
            key = Fernet.generate_key()
            with open(self.key_file, 'wb') as f:
                f.write(key)
        
        self.cipher = Fernet(key)
    
    def _load_passwords(self):
        """Load passwords from storage file."""
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r') as f:
                    encrypted_data = json.load(f)
                return encrypted_data
            except (json.JSONDecodeError, IOError):
                return {}
        return {}
    
    def _save_passwords(self):
        """Save passwords to storage file."""
        with open(self.storage_file, 'w') as f:
            json.dump(self.passwords, f, indent=2)
    
    def add_password(self, service, username, password):
        """Add or update a password entry."""
        encrypted_password = self.cipher.encrypt(password.encode()).decode()
        self.passwords[service] = {
            "username": username,
            "password": encrypted_password
        }
        self._save_passwords()
        return True
    
    def get_password(self, service):
        """Retrieve a password for a service."""
        if service not in self.passwords:
            return None, None
        
        entry = self.passwords[service]
        try:
            decrypted_password = self.cipher.decrypt(entry["password"].encode()).decode()
            return entry["username"], decrypted_password
        except Exception as e:
            return None, f"Error decrypting password: {str(e)}"
    
    def delete_password(self, service):
        """Delete a password entry."""
        if service in self.passwords:
            del self.passwords[service]
            self._save_passwords()
            return True
        return False
    
    def get_all_services(self):
        """Get list of all stored services."""
        return list(self.passwords.keys())
    
    def service_exists(self, service):
        """Check if a service entry exists."""
        return service in self.passwords
