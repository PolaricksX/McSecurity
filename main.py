"""Command-line entry point (see docs/flowchart.md)."""
import getpass
import sys
from pathlib import Path

from password_manager.generator import generate_password
from password_manager.strength import REQUIREMENTS, is_strong_password
from password_manager.vault import Vault

VAULT_FILE = "vault.json"
MENU = "[a]dd  [g]et  [d]elete  [l]ist  [n]ew password  [q]uit > "


def main() -> int:
    creating_vault = not Path(VAULT_FILE).exists()
    if creating_vault:
        while True:
            master = getpass.getpass("Choose a master password: ")
            if is_strong_password(master):
                print("Master password meets the strength requirements.")
                break
            print(f"Master password is too weak. Use {REQUIREMENTS}. Please try again.")
    else:
        master = getpass.getpass("Master password: ")
    try:
        vault = Vault(VAULT_FILE, master)
    except ValueError as exc:
        print(exc)
        return 1
    if creating_vault:
        vault.save()
    while True:
        choice = input(MENU).strip().lower()
        if choice == "a":
            site = input("Site: ")
            user = input("Username: ")
            pw = getpass.getpass("Password (blank to generate): ") or generate_password()
            if is_strong_password(pw):
                print("[Password strength] This password meets the strength requirements.")
            else:
                print(f"[Password strength] This password is weak; consider changing it. Use {REQUIREMENTS}.")
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
