"""Command-line entry point (see docs/flowchart.md)."""
import getpass
import sys
from pathlib import Path

from password_manager.generator import generate_password
from password_manager.password_strength import REQUIREMENTS, is_strong_password
from password_manager.vault import Vault

VAULT_FILE = "vault.json"
MENU = "[a]dd  [g]et  [d]elete  [l]ist  [n]ew password  [q]uit > "


def main() -> int:
    new_vault = not Path(VAULT_FILE).exists()
    while True:
        master = getpass.getpass("Master password: ")
        if not new_vault or is_strong_password(master):
            break
        print(f"Weak master password. {REQUIREMENTS}")
    if new_vault:
        print("Master password meets strength requirements.")
    try:
        vault = Vault(VAULT_FILE, master)
        if new_vault:
            vault.save()
    except ValueError as exc:
        print(exc)
        return 1
    while True:
        choice = input(MENU).strip().lower()
        if choice == "a":
            site = input("Site: ")
            user = input("Username: ")
            pw = getpass.getpass("Password (blank to generate): ") or generate_password()
            if is_strong_password(pw):
                print("Password meets strength requirements.")
            else:
                print(f"Weak password; changing it is optional. {REQUIREMENTS}")
            vault.add(site, user, pw)
            vault.save()
        elif choice == "g":
            entry = vault.get(input("Site: "))
            print(entry if entry else "Not found")
        elif choice == "d":
            print("Deleted" if vault.delete(input("Site: ")) else "Not found")
            vault.save()
        elif choice == "l":
            print("\n".join(vault.sites()) or "(empty)")
        elif choice == "n":
            print(generate_password())
        elif choice == "q":
            return 0


if __name__ == "__main__":
    sys.exit(main())
