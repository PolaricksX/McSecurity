"""Encrypted on-disk store of credentials."""
import json
from pathlib import Path

from . import crypto


class Vault:
    def __init__(self, path, master_password: str):
        self.path = Path(path)
        self.entries: dict = {}
        if self.path.exists():
            raw = json.loads(self.path.read_text())
            self._salt = bytes.fromhex(raw["salt"])
            self._key = crypto.derive_key(master_password, self._salt)
            data = crypto.decrypt(self._key, raw["data"].encode())
            self.entries = json.loads(data)
        else:
            self._salt = crypto.new_salt()
            self._key = crypto.derive_key(master_password, self._salt)

    def add(self, site: str, username: str, password: str) -> None:
        self.entries[site] = {"username": username, "password": password}

    def get(self, site: str):
        return self.entries.get(site)

    def delete(self, site: str) -> bool:
        return self.entries.pop(site, None) is not None

    def sites(self):
        return sorted(self.entries)

    def save(self) -> None:
        token = crypto.encrypt(self._key, json.dumps(self.entries).encode())
        payload = {"salt": self._salt.hex(), "data": token.decode()}
        self.path.write_text(json.dumps(payload))
