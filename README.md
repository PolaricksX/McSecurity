# McSecurity
A simple Python (PyCharm-friendly) password manager.

- `main.py` – CLI entry point
- `password_manager/` – crypto, vault, generator modules
- `tests/` – unit tests (`python -m unittest`)
- `docs/flowchart.md` – program flowchart

Setup: `pip install -r requirements.txt`, then `python main.py`.

When creating a vault, choose a master password with at least 12 characters,
including an uppercase letter, a lowercase letter, a number, and a symbol.
Existing vaults can still be opened with their original master password.
Passwords added to the vault are checked against the same requirements; weak
passwords produce a reminder but can still be saved. This basic check does not
guarantee that a password is secure.
