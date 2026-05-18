import json
import os
import base64
import argparse
import getpass
import time

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

VAULT_FILE = "vault.json"
MAX_ATTEMPTS = 3


# Generate encryption key
def derive_key(password, salt):

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=480000,
    )

    return kdf.derive(password.encode())


# Encrypt data
def encrypt_data(key, data):

    aesgcm = AESGCM(key)

    nonce = os.urandom(12)

    plaintext = json.dumps(data).encode()

    ciphertext = aesgcm.encrypt(
        nonce,
        plaintext,
        None
    )

    return {
        "nonce": base64.b64encode(nonce).decode(),
        "ciphertext": base64.b64encode(ciphertext).decode()
    }


# Decrypt data
def decrypt_data(key, encrypted_data):

    aesgcm = AESGCM(key)

    nonce = base64.b64decode(
        encrypted_data["nonce"]
    )

    ciphertext = base64.b64decode(
        encrypted_data["ciphertext"]
    )

    plaintext = aesgcm.decrypt(
        nonce,
        ciphertext,
        None
    )

    return json.loads(plaintext.decode())


# Initialize vault
def initialize_vault(master_password):

    salt = os.urandom(16)

    password_check = {
        "message": "Password Verified"
    }

    key = derive_key(master_password, salt)

    encrypted_check = encrypt_data(
        key,
        password_check
    )

    vault = {
        "salt": base64.b64encode(salt).decode(),
        "password_check": encrypted_check,
        "entries": {}
    }

    save_vault(vault)

    return vault, key


# Save vault safely
def save_vault(vault):

    temp_file = VAULT_FILE + ".tmp"

    with open(temp_file, "w") as file:
        json.dump(vault, file, indent=4)

    os.replace(temp_file, VAULT_FILE)


# Load vault
def load_vault(master_password):

    if not os.path.exists(VAULT_FILE):

        print("No vault found. Creating new vault...")
        return initialize_vault(master_password)

    with open(VAULT_FILE, "r") as file:
        vault = json.load(file)

    salt = base64.b64decode(vault["salt"])

    key = derive_key(master_password, salt)

    try:

        decrypt_data(
            key,
            vault["password_check"]
        )

    except Exception:

        raise ValueError(
            "Incorrect master password!"
        )

    return vault, key


# Add entry
def add_entry(master_password):

    vault, key = load_vault(master_password)

    website = input("Website: ").strip()

    username = input("Username: ").strip()

    password = getpass.getpass(
        "Password: "
    )

    entry = {
        "username": username,
        "password": password
    }

    encrypted_entry = encrypt_data(
        key,
        entry
    )

    vault["entries"][website] = encrypted_entry

    save_vault(vault)

    print("\nPassword saved successfully!")


# Get entry
def get_entry(master_password):

    vault, key = load_vault(master_password)

    website = input(
        "Website: "
    ).strip()

    if website not in vault["entries"]:

        print("No entry found.")
        return

    encrypted_entry = vault["entries"][website]

    try:

        entry = decrypt_data(
            key,
            encrypted_entry
        )

        print("\nSaved Credentials")
        print("-------------------")
        print(f"Username: {entry['username']}")
        print(f"Password: {entry['password']}")

    except Exception:

        print(
            "Decryption failed! Data may be corrupted."
        )


# List websites
def list_entries(master_password):

    vault, key = load_vault(master_password)

    print("\nStored Websites")
    print("-------------------")

    if not vault["entries"]:
        print("No saved entries.")
        return

    for website in vault["entries"]:
        print(website)


# Delete entry
def delete_entry(master_password):

    vault, key = load_vault(master_password)

    website = input(
        "Website to delete: "
    ).strip()

    if website in vault["entries"]:

        del vault["entries"][website]

        save_vault(vault)

        print("Entry deleted.")

    else:
        print("Website not found.")


# Login protection
attempts = 0

while attempts < MAX_ATTEMPTS:

    try:

        master_password = getpass.getpass(
            "Master Password: "
        )

        parser = argparse.ArgumentParser(
            description="Secure Password Manager"
        )

        subparsers = parser.add_subparsers(
            dest="command"
        )

        subparsers.add_parser("add")
        subparsers.add_parser("get")
        subparsers.add_parser("list")
        subparsers.add_parser("delete")

        args = parser.parse_args()

        if args.command == "add":
            add_entry(master_password)

        elif args.command == "get":
            get_entry(master_password)

        elif args.command == "list":
            list_entries(master_password)

        elif args.command == "delete":
            delete_entry(master_password)

        else:
            parser.print_help()

        break

    except ValueError as error:

        attempts += 1

        print(f"\n{error}")
        print(
            f"Attempts remaining: {MAX_ATTEMPTS - attempts}"
        )

        time.sleep(1)

if attempts == MAX_ATTEMPTS:

    print(
        "\nToo many failed attempts. Vault locked."
    )