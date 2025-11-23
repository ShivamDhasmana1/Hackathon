from typing import Dict, Optional
import os, base64, hashlib
from cryptography.fernet import Fernet

key = Fernet.generate_key()
cipher = Fernet(key)

def hash_with_salt(value: Optional[str]) -> Dict[str, Optional[str]]:
    if not value:
        return {"hash": None, "salt": None}
    salt = os.urandom(16)
    h = hashlib.sha256(value.encode() + salt).hexdigest()
    return {
        "hash": h,
        "salt": base64.b64encode(salt).decode()
    }

def hash_kyc_fields(name: Optional[str], dob: Optional[str],
                    id_number: Optional[str], address: Optional[str]):
    return {
        "name": hash_with_salt(name),
        "dob": hash_with_salt(dob),
        "id_number": hash_with_salt(id_number),
        "address": hash_with_salt(address),
    }
