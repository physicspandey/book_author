from dotenv import load_dotenv
from sqlalchemy.orm import Mapper
from sqlalchemy.orm.mapper import configure_mappers
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from sqlalchemy import event
from datetime import datetime
from enum import Enum
import hashlib
import base64
import hmac
import os

load_dotenv()

SECRET_KEY = os.getenv("ENCRYPTION_SECRET")


if isinstance(SECRET_KEY, str):
   SECRET_KEY = base64.b64decode(SECRET_KEY.encode())


def encrypt_aes_gcm(plaintext, key: bytes):
   """
   AES-256-GCM Encryption (for Strong Security & Compliance)

   This method encrypts data using AES-256-GCM, which ensures both confidentiality and integrity.
   It generates a unique IV for each encryption, making it highly secure but non-deterministic.

   Since each encryption produces a different result, this method cannot be used for searchable encryption.
   """
   # Convert int/float values to string before encryption
   if not isinstance(plaintext, str):
       plaintext = str(plaintext)

   # Generate a unique 12-byte IV for each encryption (ensures randomness)
   iv = os.urandom(12)

   ## Initialize AES-256-GCM cipher
   cipher = Cipher(algorithms.AES(key), modes.GCM(iv), backend=default_backend())

   # Create an encryptor instance
   encryptor = cipher.encryptor()

   # Encrypt the plaintext
   ciphertext = encryptor.update(plaintext.encode()) + encryptor.finalize()

   # Encode IV, tag, and ciphertext in Base64
   return base64.b64encode(iv + encryptor.tag + ciphertext).decode()


def decrypt_aes_gcm(encrypted_text: str, key: bytes):
   """
   AES-256-GCM Decryption (Restores Original Data)

   This method decrypts data that was encrypted using AES-256-GCM.
   It verifies data integrity using the authentication tag before decryption.

   The same key used for encryption must be used for decryption.
   """
   # Decode the Base64-encoded encrypted data
   encrypted_data = base64.b64decode(encrypted_text)

   # Extract IV, tag, and ciphertext
   iv, tag, ciphertext = encrypted_data[:12], encrypted_data[12:28], encrypted_data[28:]

   # Initialize AES-256-GCM cipher
   cipher = Cipher(algorithms.AES(key), modes.GCM(iv, tag), backend=default_backend())

   # Create a decryptor instance
   decryptor = cipher.decryptor()

   # Decrypt and return the original plaintext
   return decryptor.update(ciphertext) + decryptor.finalize()


def hash_for_search(value) -> str:
   """
   Generates a secure, deterministic hash using HMAC-SHA256 for searchable fields.

   This allows exact-match searches on sensitive data without revealing the original value.
   Not suitable for cryptographic security, but safe for indexing & lookup.
   """
   value_str = str(value)
   return hmac.new(SECRET_KEY, value_str.encode(), hashlib.sha256).hexdigest()

#_____________________________________ EncryptedMixin Class _________________________________________________

class EncryptedMixin:
   """
   Mixin to automatically encrypt/decrypt specified fields in a SQLAlchemy model.
   Supports searchable encryption via HMAC hashing.
   """
   __encrypted_fields__ = {}
   __searchable_fields__ = []

   @classmethod
   def encrypt_sensitive_fields(cls, mapper: Mapper, connection, target):
       """Encrypts specified fields before saving to the database."""
       for field, field_type in cls.__encrypted_fields__.items():

           # Retrieve the current field value
           value = getattr(target, field)

           # Prevent double encryption , Check if value is not already encrypted
           if value is not None and not isinstance(value, bytes):

               # Convert Enum to string before encryption
               if isinstance(value, Enum):
                   value = value.value

               # Convert datetime to ISO format string before encryption
               elif isinstance(value, datetime):
                   value = value.isoformat()

               # Encrypt value using AES-GCM
               encrypted_value = encrypt_aes_gcm(value, SECRET_KEY).encode("utf-8")

               # Store the encrypted value in the object
               setattr(target, field, encrypted_value)

               # Store HMAC hash for searchable fields
               if field in cls.__searchable_fields__:
                   setattr(target, f"{field}_hash", hash_for_search(value))

   @classmethod
   def decrypt_sensitive_fields(cls, target, context):
       """Decrypts specified fields when retrieving from the database."""
       for field, field_type in cls.__encrypted_fields__.items():

           # Retrieve the encrypted value from the object
           value = getattr(target, field)

           # Ensure value exists and is stored as bytes
           if value and isinstance(value, bytes):
               decrypted_value = decrypt_aes_gcm(value.decode("utf-8"), SECRET_KEY).decode()

               # Convert decrypted value back to its original data type
               if field_type == int:
                   decrypted_value = int(decrypted_value)
               elif field_type == float:
                   decrypted_value = float(decrypted_value)
               elif field_type == datetime:
                   decrypted_value = datetime.fromisoformat(decrypted_value)
               elif isinstance(field_type, type) and issubclass(field_type, Enum):
                   decrypted_value = field_type(decrypted_value)

               # Store the decrypted value back in the object
               setattr(target, field, decrypted_value)

   @classmethod
   def register_encryption_events(cls):
       """Attach encryption event listeners to all models using EncryptedMixin."""

       # Ensure SQLAlchemy models are fully configured before attaching events
       configure_mappers()

       # Iterate through all models that inherit from EncryptedMixin
       for subclass in cls.__subclasses__():

           # Encrypt data before inserting
           event.listen(subclass, "before_insert", subclass.encrypt_sensitive_fields)

           # Encrypt data before updating
           event.listen(subclass, "before_update", subclass.encrypt_sensitive_fields)

           # Decrypt data when loading from DB
           event.listen(subclass, "load", subclass.decrypt_sensitive_fields)
