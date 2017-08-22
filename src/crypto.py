from cryptography.fernet import Fernet
import json

def gen_key():
    return Fernet.generate_key().decode()
