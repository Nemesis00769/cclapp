import os
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
from Crypto.PublicKey import DSA
from Crypto.Random.random import randint
from Crypto.Hash import SHA256
# Diffie-Hellman Key Exchange
PRIME = 23  # Small prime number for demonstration (use a large one in production)
BASE = 5



def get_aes_key_from_secret(secret):
    secret_bytes = str(secret).encode()
    key = SHA256.new(secret_bytes).digest()[:16]  # Use first 16 bytes as AES key
    return key


def generate_private_key():
    """Generates a random private key."""
    return randint(2, PRIME - 2)

def generate_public_key(private_key):
    """Computes public key using base and prime."""
    return (BASE ** private_key) % PRIME

def compute_shared_secret(private_key, received_public_key):
    """Computes the shared secret key."""
    return (received_public_key ** private_key) % PRIME

# AES Encryption/Decryption
import base64

def encrypt_message(message, secret):
    key = get_aes_key_from_secret(secret)
    cipher = AES.new(key, AES.MODE_EAX)
    ciphertext, tag = cipher.encrypt_and_digest(message.encode())

    # Combine nonce + tag + ciphertext
    combined = cipher.nonce + tag + ciphertext
    combined_b64 = base64.b64encode(combined).decode()

    return combined_b64


def decrypt_message(encrypted_combined_b64, secret):
    key = get_aes_key_from_secret(secret)
    combined = base64.b64decode(encrypted_combined_b64)

    # Split back: nonce (16 bytes), tag (16 bytes), rest = ciphertext
    nonce = combined[0:16]
    tag = combined[16:32]
    ciphertext = combined[32:]

    cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)
    plaintext = cipher.decrypt_and_verify(ciphertext, tag)
    return plaintext.decode()

