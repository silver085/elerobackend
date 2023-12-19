from pyeasyencrypt.pyeasyencrypt import encrypt_string, decrypt_string

ENC_SALT = "TestSalt"


def encrypt(clear_message, salt):
    return encrypt_string(clear_string=clear_message, password=salt)


def decrypt(hashed_pass, salt):
    return decrypt_string(encrypted_string=hashed_pass, password=salt)
