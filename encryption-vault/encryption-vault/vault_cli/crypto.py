"""
Provides key derivation and AES-GCM encryption/decryption utils.
"""

# standard lib imports
from Crypto.Cipher import AES                     # AES CYPHER
from Crypto.Protocol.KDF import PBKDF2            # Pass-based key derivation
from Crypto.Random import get_random_bytes        # Secure random bytes generator

# config const
SALT_BYTES = 16          # or 12 for GCM recommendation
KDF_ITERATIONS = 100_000
KEY_LEANGTH = 32


def derive_key(password: str, salt: bytes = None) -> (bytes, bytes):
    """
    Derive a symetric key from a password using PBKDF2.

    Args:
        password (str): User-supplied master password.
        salt (bytes, optional): If provided, reuse this salt; otherwise generate a new one.

    Returns:
        (key, salt): Tuple where key is the derived key and salt is the random salt.
    """

    # Generate a new salt if not provided
    if salt is None:
        salt = get_random_bytes(SALT_BYTES)

    # Derive the key using PBKDF2 (HMAC-SHA1)
    key = PBKDF2(password, salt, dkLen=KEY_LEANGTH, count=KDF_ITERATIONS)

    # Return both key and salt (store salt for future use)
    return key, salt

def encrypt_bytes(plaintext: bytes, key: bytes) -> bytes:
    """
    Encrypt bytes using AES-GCM for confidentiality and authenticity.

    Args:
        plaintext (bytes): data to be encrypted.
        key (bytes): 256-bit symmetric key.

    Returns:
        bytes: Concatenation of nonce + tag + ciphertext.
    """
    # 1. Create a new AES-GCM cipher object with fresh nonce
    cipher = AES.new(key, AES.MODE_GCM)

    # 2. Encrypt the plaintext and compute the auth tag
    ciphertext, tag = cipher.encrypt_and_digest(plaintext)

    # 3. Concatenate nonce, tag and ciphertext
    return cipher.nonce + tag + ciphertext

def decrypt_bytes(payload: bytes, key: bytes) -> bytes:
    """
    Decrypt data produced by encrypt_bytes, verifying its authenticity.

    Args:
        payload (bytes): Combined nonce +tag +ciphertext.
        key (bytes): 256-bit symmetric key.

    Returns:
        bytes: The original plaintext if authentication succeeds.

    Raises:
        ValueError: if the authentication tag does not match.
    """

    # 1. Extract nonce, tag, and chipertext
    nonce = payload[:SALT_BYTES]
    tag = payload[SALT_BYTES:SALT_BYTES*2]
    ciphertext = payload[SALT_BYTES*2:]

    # 2. Reconstruct cipher and verify
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    plaintext = cipher.decrypt_and_verify(ciphertext, tag)

    # 3. Return the decrypted plaintext
    return plaintext
