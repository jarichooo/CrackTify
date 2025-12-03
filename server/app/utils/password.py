import hashlib
import os

def hash_password(password: str):
    salt = os.urandom(16)
    hashed = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100000)
    return salt.hex() + ":" + hashed.hex()

def verify_password(password: str, stored: str):
    salt, stored_hash = stored.split(":")
    salt = bytes.fromhex(salt)
    hashed = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100000)
    return hashed.hex() == stored_hash
