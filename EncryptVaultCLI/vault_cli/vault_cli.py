#!/usr/bin/env python3
"""
Command-line interface (CLI) for the encrypted file vault.
Uses Click for user-friendly commands and prompts.
"""
import os
import sys
import click

# Import our crypto helpers from the local crypto module
from vault_cli.crypto import derive_key, encrypt_bytes, decrypt_bytes

# Where we store the salt and encrypted payloads
VAULT_DIR = os.path.expanduser("~/.vault_cli")
SALT_PATH = os.path.join(VAULT_DIR, "salt.bin")


@click.group()
def cli():
    """Encrypted File Vault CLI."""
    pass


@cli.command()
@click.option(
    "--password",
    prompt="Create a new master password",
    hide_input=True,
    confirmation_prompt=True,
    help="Set your master password",
)
def init(password):
    """Initialize the vault directory and master-key salt."""
    os.makedirs(VAULT_DIR, exist_ok=True)
    _, salt = derive_key(password)
    with open(SALT_PATH, "wb") as f:
        f.write(salt)
    click.echo(f"Initialized vault at {VAULT_DIR}")


@cli.command()
@click.argument("filepath", type=click.Path(exists=True))
@click.option(
    "--password", prompt="Enter your master password", hide_input=True, help="Your master password")


def put(filepath, password):
    """Encrypt and store a file in the vault."""
    if not os.path.exists(SALT_PATH):
        click.echo("Error: vault not initialized. Run `vault_cli init` first.")
        sys.exit(1)

    # Load salt & derive key
    with open(SALT_PATH, "rb") as f:
        salt = f.read()
    key, _ = derive_key(password, salt)

    # Read plaintext
    with open(filepath, "rb") as f:
        plaintext = f.read()

    # Encrypt and write out
    payload = encrypt_bytes(plaintext, key)
    filename = os.path.basename(filepath)
    dest = os.path.join(VAULT_DIR, filename + ".enc")
    with open(dest, "wb") as f:
        f.write(payload)

    click.echo(f"Stored {filename} in vault.")


@cli.command(name="get")
@click.argument("filename")
@click.option(
    "--out",
    "-o",
    type=click.Path(),
    default=".",
    help="Directory to write the decrypted file into",
)
@click.option(
    "--password", prompt=True, hide_input=True, help="Your master password"
)
def get_file(filename, out, password):
    """Retrieve and decrypt a file from the vault."""
    if not os.path.exists(SALT_PATH):
        click.echo("Error: vault not initialized. Run `vault_cli init` first.")
        sys.exit(1)

    # Load salt & derive key
    with open(SALT_PATH, "rb") as f:
        salt = f.read()
    key, _ = derive_key(password, salt)

    # Locate encrypted file
    enc_path = os.path.join(VAULT_DIR, filename + ".enc")
    if not os.path.exists(enc_path):
        click.echo(f"Error: `{filename}` not found in vault.")
        sys.exit(1)

    # Decrypt
    with open(enc_path, "rb") as f:
        payload = f.read()
    try:
        plaintext = decrypt_bytes(payload, key)
    except ValueError:
        click.echo("Error: failed to decrypt. Wrong password or corrupted file.")
        sys.exit(1)

    # Write output
    os.makedirs(out, exist_ok=True)
    out_path = os.path.join(out, filename)
    with open(out_path, "wb") as f:
        f.write(plaintext)

    click.echo(f"Retrieved {filename} to {out}/")


@cli.command(name="list")
def list_files():
    """List all files stored in the vault."""
    if not os.path.isdir(VAULT_DIR):
        click.echo("Error: vault not initialized. Run `vault_cli init` first.")
        sys.exit(1)

    entries = [f[:-4] for f in os.listdir(VAULT_DIR) if f.endswith(".enc")]
    if not entries:
        click.echo("Vault is empty.")
    else:
        click.echo("Files in vault:")
        for name in entries:
            click.echo(f"  - {name}")


if __name__ == "__main__":
    cli()
