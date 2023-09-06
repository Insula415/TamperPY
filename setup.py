import os
import hashlib

def generate_hash():
    with open("main.py", "rb") as file:
        bytes = file.read()
        readable_hash = hashlib.sha256(bytes).hexdigest()
        with open("main.py.sha256", "w") as hash_file:
            hash_file.write(readable_hash)

def generate_linux():
    with open("check_integrity.sh", "w") as file:
        file.write("""#!/bin/bash

sha256sum main.py | awk '{print $1}' > temp.sha256

if diff temp.sha256 main.py.sha256 &>/dev/null; then
    echo "File is not tampered."
    rm temp.sha256
    python main.py
else
    echo "The file main.py has been tampered with!"
    rm temp.sha256
    exit 1
fi
""")
    os.chmod("check_integrity.sh", 0o755)

def generate_windows():
    with open("check_integrity.bat", "w") as file:
        file.write("""@echo off
CertUtil -hashfile main.py SHA256 | find /v "CertUtil" | find /v "main.py" > temp.sha256

fc temp.sha256 main.py.sha256 > nul
if errorlevel 1 (
    echo The file main.py has been tampered with!
    del temp.sha256
    pause
    exit
) else (
    echo File is not tampered.
    del temp.sha256
    python main.py
)
pause
""")

if __name__ == "__main__":
    # check OS name
    generate_hash()
    current_os = os.name
    if current_os == "posix":
        generate_linux()
        print("Generated Linux/Unix files.")
    elif current_os == "nt":
        generate_windows()
        print("Generated Windows files.")
    else:
        print(f"Unsupported OS: {current_os}")
