from src.crypto import gen_key, decrypt_server_info
from config import register_url, register_email
import uuid
import requests
import json
import os

def firstrun():
    # Generate unique ID and keys
    uid = str(uuid.uuid4())
    key = gen_key()

    with open("config.py","a") as outfile:
        outfile.write("\n\n")
        outfile.write("################# Setup variables #################\n")
        outfile.write("# If you change these you will have to re-register\n")
        outfile.write("uid = '{}'\n".format(uid))
        outfile.write("key = '{}'\n".format(key))
        outfile.write("###################################################\n")

    reg_info = json.dumps({
        "uid": uid,
        "key": key,
        "email": register_email
    })
    print(reg_info)

    # try:
    enc_response = requests.post(register_url, json=reg_info).text
    print("\nenc", enc_response)
    response = decrypt_server_info(enc_response, key)
    print("\nres", response)

    if response == uid:
        print("Registration successfull, follow email link to complete")
        with open("initialized.dat","w") as of: of.write("true")
    #     else:
    #         print("Somthing went wrong. Try again later with new config file")
    # except:
    #     print("Somthing went wrong. Try again later with new config file")
