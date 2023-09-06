import os
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Hash import SHA256
import textwrap

def get_key():
    password = input("Enter your passphrase: ").encode('utf-8')
    salt = get_random_bytes(16)
    key = PBKDF2(password, salt, dkLen=32)
    return key, salt

def encrypt(input_file, encrypted_file):
    key, salt = get_key()
    
    with open(input_file, 'r') as file:
        data = file.read().encode('utf-8')
    
    cipher = AES.new(key, AES.MODE_CBC)
    ciphertext = cipher.encrypt(pad(data, AES.block_size))
    
    with open(encrypted_file, 'wb') as file:
        file_contents = salt + cipher.iv + ciphertext
        file_hash = SHA256.new(file_contents).digest()
        file.write(file_contents + file_hash)

MAX_ATTEMPTS = 3

def decrypt(encrypted_file, decrypted_file):
    attempt_count = 0
    while attempt_count < MAX_ATTEMPTS:
        with open(encrypted_file, 'rb') as file:
            file_contents = file.read()
            stored_hash = file_contents[-32:]
            salt_iv_ciphertext = file_contents[:-32]

        computed_hash = SHA256.new(salt_iv_ciphertext).digest()
        if computed_hash != stored_hash:
            os.remove(encrypted_file)
            print(f"The file {encrypted_file} appears to be tampered with and has been deleted for security reasons.")
            return
        
        password = input("Enter your passphrase: ").encode('utf-8')
        salt = salt_iv_ciphertext[:16]
        key = PBKDF2(password, salt, dkLen=32)
        iv = salt_iv_ciphertext[16:32]
        ciphertext = salt_iv_ciphertext[32:]

        cipher = AES.new(key, AES.MODE_CBC, iv=iv)
        try:
            plaintext = unpad(cipher.decrypt(ciphertext), AES.block_size)
            with open(decrypted_file, 'w') as file:
                file.write(plaintext.decode('utf-8'))
            print(f"Decryption complete. Decrypted file saved as {decrypted_file}.")
            break
        except ValueError:
            attempt_count += 1
            print(f"Incorrect passphrase. {MAX_ATTEMPTS - attempt_count} attempts remaining.")

    if attempt_count == MAX_ATTEMPTS:
        os.remove(encrypted_file)
        print(f"Maximum passphrase attempts reached. {encrypted_file} has been deleted for security reasons.")

def main():
    running = True
    while running:
        try: 
            action = int(input(textwrap.dedent(
                """
                1. Encrypt
                2. Decrypt

                """
            )))
        except:
            print("Something went wrong...")
            
        if action == 1:
            input_file = input("Enter the name of the file you want to encrypt (e.g., passwords.txt): ")
            encrypted_file = input("Enter the name for the encrypted output file: ")
            encrypt(input_file, encrypted_file)
            print(f"Encryption complete. Encrypted file saved as {encrypted_file}.")
            running = False
        
        elif action == 2:
            encrypted_file = input("Enter the name of the encrypted file: ")
            decrypted_file = input("Enter the name for the decrypted output file: ")
            decrypt(encrypted_file, decrypted_file)
            running = False

        else:
            print("Invalid action. Please choose '1' or '2'.")
            running = True

if __name__ == "__main__":
    main()
