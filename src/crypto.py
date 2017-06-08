from cryptography.fernet import Fernet
import json


# Decrypt server info
def decrypt_server_info(json_data, key):
    f = Fernet(key)
    info = f.decrypt(json_data.encode())
    return json.loads(info)

def gen_key():
    return Fernet.generate_key().decode()
