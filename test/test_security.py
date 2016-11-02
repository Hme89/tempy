from src.security.passlib_setup import pwd_context
from src.security.userlib import UserData
import os


def test_hash_bcrypt():
    pass1 = "testpassword"
    pass2 = "test2Password"

    hash1 = pwd_context.encrypt(pass1)
    hash2 = pwd_context.encrypt(pass2)

    assert pwd_context.verify(pass1, hash1)
    assert pwd_context.verify(pass2, hash2)
    assert not pwd_context.verify(pass1, hash2)
    assert not pwd_context.verify(pass2, hash1)

def test_stored_hash():
    pass1 = "12kJuk&%123648.,_-wsk"
    outfile = open("hashtest.txt","w")
    outfile.write(pwd_context.encrypt(pass1))
    outfile.close()

    infile = open("hashtest.txt","r")
    try:
        assert pwd_context.verify(pass1,infile.readline())
    finally:
        infile.close()
        os.remove("hashtest.txt")
