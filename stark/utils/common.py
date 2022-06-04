import hashlib

SALT = "fafmaofda".encode()

def gen_md5(pwd):
    hashlib_obj = hashlib.md5(SALT)
    hashlib_obj.update(pwd.encode())

    return hashlib_obj.hexdigest()