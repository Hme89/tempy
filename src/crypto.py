import string
import secrets
import json, zlib

def gen_key(length=32):
    selection = string.ascii_letters + "!?#%&()[]+-_.:,;=<>@" + string.digits
    rand =''.join(secrets.choice( selection ) for i in range(length))
    return rand


def compress(data_dict):
    return zlib.compress( json.dumps(data_dict).encode() )
