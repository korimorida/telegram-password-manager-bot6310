from cryptography.fernet import Fernet

with open("secret.key", "rb") as f:
    KEY = f.read()

fernet = Fernet(KEY)

def encrypt_password(password: str) -> str:
    return fernet.encrypt(password.encode()).decode()

def decrypt_password(token: str) -> str:
    return fernet.decrypt(token.encode()).decode()