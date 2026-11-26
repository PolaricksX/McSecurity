import contextlib
import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import main
from password_manager.strength import is_strong_password
from password_manager.vault import Vault


class PasswordStrengthTests(unittest.TestCase):
    def test_requirements(self):
        self.assertTrue(is_strong_password("StrongPass1!"))
        for password in ("Short1!", "lowercase123!", "UPPERCASE123!", "NoNumbersHere!", "NoSymbols1234", "NoSymbols123 "):
            with self.subTest(password=password):
                self.assertFalse(is_strong_password(password))

    def test_creation_retries_and_persists_vault(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "vault.json"
            output = io.StringIO()
            with patch.object(main, "VAULT_FILE", str(path)), \
                 patch("main.getpass.getpass", side_effect=["weak", "StrongPass1!"]), \
                 patch("builtins.input", return_value="q"), \
                 contextlib.redirect_stdout(output):
                self.assertEqual(main.main(), 0)
            self.assertIn("too weak", output.getvalue())
            self.assertIn("meets the strength requirements", output.getvalue())
            self.assertEqual(Vault(path, "StrongPass1!").sites(), [])

    def test_existing_weak_master_and_weak_entry_are_accepted(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "vault.json"
            Vault(path, "old").save()
            output = io.StringIO()
            with patch.object(main, "VAULT_FILE", str(path)), \
                 patch("main.getpass.getpass", side_effect=["old", "weak"]), \
                 patch("builtins.input", side_effect=["a", "site", "user", "q"]), \
                 contextlib.redirect_stdout(output):
                self.assertEqual(main.main(), 0)
            self.assertIn("weak; consider changing it", output.getvalue())
            self.assertEqual(Vault(path, "old").get("site")["password"], "weak")

    def test_strong_entry_receives_feedback(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "vault.json"
            Vault(path, "old").save()
            output = io.StringIO()
            with patch.object(main, "VAULT_FILE", str(path)), \
                 patch("main.getpass.getpass", side_effect=["old", "StrongPass1!"]), \
                 patch("builtins.input", side_effect=["a", "site", "user", "q"]), \
                 contextlib.redirect_stdout(output):
                self.assertEqual(main.main(), 0)
            self.assertIn("[Password strength] This password meets", output.getvalue())
            self.assertEqual(Vault(path, "old").get("site")["password"], "StrongPass1!")


if __name__ == "__main__":
    unittest.main()
