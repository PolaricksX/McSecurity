import contextlib
import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

import main
from password_manager import password_manager_ui
from password_manager.password_strength import is_strong_password
from password_manager.vault import Vault


class PasswordStrengthTests(unittest.TestCase):
    def test_requirements(self):
        self.assertTrue(is_strong_password("Abcdefghij1!"))
        for password in (
            "Abcdefghi1!",
            "abcdefghij1!",
            "ABCDEFGHIJ1!",
            "Abcdefghijk!",
            "Abcdefghij1 ",
        ):
            with self.subTest(password=password):
                self.assertFalse(is_strong_password(password))

    def test_cli_reprompts_and_saves_weak_entry(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "vault.json"
            output = io.StringIO()
            with (
                patch.object(main, "VAULT_FILE", str(path)),
                patch("getpass.getpass", side_effect=["weak", "Abcdefghij1!", "weak"]),
                patch("builtins.input", side_effect=["a", "site", "user", "q"]),
                contextlib.redirect_stdout(output),
            ):
                self.assertEqual(main.main(), 0)
            self.assertEqual(Vault(path, "Abcdefghij1!").get("site")["password"], "weak")
            self.assertIn("Weak master password", output.getvalue())
            self.assertIn("Master password meets strength requirements", output.getvalue())
            self.assertIn("changing it is optional", output.getvalue())

    def test_cli_creates_vault_and_allows_legacy_master_password(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "vault.json"
            with (
                patch.object(main, "VAULT_FILE", str(path)),
                patch("getpass.getpass", return_value="Abcdefghij1!"),
                patch("builtins.input", return_value="q"),
            ):
                self.assertEqual(main.main(), 0)
            self.assertTrue(path.exists())
            legacy = Path(directory) / "legacy.json"
            Vault(legacy, "weak").save()
            with (
                patch.object(main, "VAULT_FILE", str(legacy)),
                patch("getpass.getpass", return_value="weak") as password_prompt,
                patch("builtins.input", return_value="q"),
            ):
                self.assertEqual(main.main(), 0)
            password_prompt.assert_called_once()

    def test_cli_reports_generated_password_as_strong(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "vault.json"
            output = io.StringIO()
            with (
                patch.object(main, "VAULT_FILE", str(path)),
                patch("getpass.getpass", side_effect=["Abcdefghij1!", ""]),
                patch("builtins.input", side_effect=["a", "site", "user", "q"]),
                contextlib.redirect_stdout(output),
            ):
                self.assertEqual(main.main(), 0)
            self.assertTrue(is_strong_password(Vault(path, "Abcdefghij1!").get("site")["password"]))
            self.assertIn("Password meets strength requirements", output.getvalue())

    def test_gui_enforces_strength_only_for_new_accounts(self):
        ui = password_manager_ui.PasswordManagerUI.__new__(password_manager_ui.PasswordManagerUI)
        ui.master_password_var = MagicMock()
        ui.master_password_var.get.return_value = "weak"
        ui.show_main_screen = MagicMock()
        with (
            patch.object(password_manager_ui.os.path, "exists", return_value=False) as exists,
            patch.object(password_manager_ui.messagebox, "showwarning") as warning,
            patch.object(password_manager_ui.messagebox, "showinfo") as info,
            patch.object(password_manager_ui, "PasswordManager") as manager,
        ):
            ui.login()
            warning.assert_called_once()
            manager.assert_not_called()
            ui.master_password_var.get.return_value = "Abcdefghij1!"
            ui.login()
            info.assert_called_once()
            manager.assert_called_once_with("Abcdefghij1!")
            manager.reset_mock()
            exists.return_value = True
            ui.master_password_var.get.return_value = "weak"
            ui.login()
            manager.assert_called_once_with("weak")

    def test_gui_reports_strength_and_stores_password(self):
        for password, expected in (("weak", "Weak password"), ("Abcdefghij1!", "meets strength")):
            with self.subTest(password=password):
                ui = password_manager_ui.PasswordManagerUI.__new__(password_manager_ui.PasswordManagerUI)
                ui.root = MagicMock()
                ui.pm = MagicMock()
                ui.pm.service_exists.return_value = False
                ui.refresh_services_list = MagicMock()
                ui.status_var = MagicMock()
                values = [MagicMock(), MagicMock(), MagicMock()]
                for variable, value in zip(values, ("site", "user", password)):
                    variable.get.return_value = value
                with (
                    patch.object(password_manager_ui.tk, "Toplevel"),
                    patch.object(password_manager_ui.tk, "StringVar", side_effect=values),
                    patch.object(password_manager_ui.ttk, "Frame"),
                    patch.object(password_manager_ui.ttk, "Label"),
                    patch.object(password_manager_ui.ttk, "Entry"),
                    patch.object(password_manager_ui.ttk, "Button") as button,
                    patch.object(password_manager_ui.messagebox, "showinfo") as info,
                ):
                    ui.show_add_password_dialog()
                    button.call_args_list[0].kwargs["command"]()
                ui.pm.add_password.assert_called_once_with("site", "user", password)
                self.assertIn(expected, info.call_args_list[0].args[1])


if __name__ == "__main__":
    unittest.main()
