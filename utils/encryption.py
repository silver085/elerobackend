import hashlib
ENC_SALT = b'TestSalt'


def encrypt(clear_message, salt):
    hash_object = hashlib.sha256()
    hash_object.update(salt + clear_message.encode())
    hash_password = hash_object.hexdigest()
    return hash_password


