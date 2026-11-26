# McSecurity
A simple Python (PyCharm-friendly) password manager.

- `main.py` – CLI entry point
- `password_manager/` – crypto, vault, generator modules
- `tests/` – unit tests (`python -m unittest`)
- `docs/flowchart.md` – program flowchart

Setup: `pip install -r requirements.txt`, then `python main.py`.

New master passwords must have at least 12 characters and include an uppercase
letter, a lowercase letter, a number, and a non-whitespace symbol. Existing
vaults can still be opened with their original master password. Passwords saved
in the manager use the same strength check, but weak passwords are allowed
after a reminder.

The separate GUI (`python -m password_manager.password_manager_ui`) uses its own
storage and currently does not authenticate the master password. Do not rely on
it to protect access to stored passwords.
