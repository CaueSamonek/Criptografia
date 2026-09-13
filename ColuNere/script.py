import os
import time
import matplotlib.pyplot as plt

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes

import subprocess

BOOKS_DIR = "books"
NUM_BOOKS = 4
REPETITIONS = 10
COLUNERE_PROGRAM = "./colunere"
CT_COLS = 4
PRINT_LENGTH = 100
OUTPUTS_DIR = "outputs"

def benchmark_colunere(input_file, encrypted_output, decrypted_output, key):
    average_enc = 0
    average_dec = 0
    encrypted = ""
    decrypted = ""
    for _ in range(REPETITIONS):

        start = time.perf_counter()

        encrypted = colunere_encrypt(input_file, key)

        enc_time = time.perf_counter() - start

        with open(encrypted_output, "w", encoding="utf-8") as f:
            f.write(encrypted)
        start = time.perf_counter()

        decrypted = colunere_decrypt(encrypted_output, key)

        dec_time = time.perf_counter() - start

        average_enc += enc_time
        average_dec += dec_time

    with open(decrypted_output, "w", encoding="utf-8") as f:
        f.write(decrypted)
    average_enc /= REPETITIONS
    average_dec /= REPETITIONS

    return average_enc, average_dec


def colunere_encrypt(input_file, key):
    result = subprocess.run(
        [
            COLUNERE_PROGRAM,
            "-e",
            "-c", str(CT_COLS),
            "-k", key,
            "-f", input_file
        ],
        check=True,
        capture_output=True,
        text=True
    )
    return result.stdout

    

def colunere_decrypt(input_file, key):
    result = subprocess.run(
        [
            COLUNERE_PROGRAM,
            "-d",
            "-c", str(CT_COLS),
            "-k", key,
            "-f", input_file
        ],
        check=True,
        capture_output=True,
        text=True
    )

    return result.stdout



# AES

def benchmark_aes(data, encrypted_output, decrypted_output, key):
    average_enc = 0
    average_dec = 0
    encrypted = b""
    decrypted = b"" 
    for _ in range(REPETITIONS):

        start = time.perf_counter()

        encrypted = aes_encrypt(data, key)

        enc_time = time.perf_counter() - start

        start = time.perf_counter()

        decrypted = aes_decrypt(encrypted, key)

        dec_time = time.perf_counter() - start
        average_enc += enc_time
        average_dec += dec_time

    with open(encrypted_output, "wb") as f:
        f.write(encrypted) 

    with open(decrypted_output, "wb") as f:
        f.write(decrypted) 
    average_enc /= REPETITIONS
    average_dec /= REPETITIONS

    return average_enc, average_dec

def aes_encrypt(data, key):
    iv = os.urandom(16)

    cipher = Cipher(
        algorithms.AES(key),
        modes.CBC(iv)
    )

    encryptor = cipher.encryptor()

    padding_size = 16 - (len(data) % 16)
    padded = data + bytes([padding_size]) * padding_size

    encrypted = encryptor.update(padded) + encryptor.finalize()

    return iv + encrypted


def aes_decrypt(data, key):
    iv = data[:16]
    ciphertext = data[16:]

    cipher = Cipher(
        algorithms.AES(key),
        modes.CBC(iv)
    )

    decryptor = cipher.decryptor()

    padded = decryptor.update(ciphertext) + decryptor.finalize()

    padding_size = padded[-1]

    return padded[:-padding_size]


# RSA

def benchmark_rsa(data, encrypted_output, decrypted_output, public_key, private_key):
    average_enc = 0
    average_dec = 0
    encrypted = b""
    decrypted = b"" 
    for _ in range(REPETITIONS):

        start = time.perf_counter()

        encrypted = rsa_encrypt(data, public_key)

        enc_time = time.perf_counter() - start
    
        start = time.perf_counter()

        decrypted = rsa_decrypt(encrypted, private_key)

        dec_time = time.perf_counter() - start
            
        average_enc += enc_time
        average_dec += dec_time

    with open(encrypted_output, "wb") as f:
        f.write(encrypted) 
    with open(decrypted_output, "wb") as f:
        f.write(decrypted) 
    average_enc /= REPETITIONS
    average_dec /= REPETITIONS

    return average_enc, average_dec

def rsa_encrypt(data, public_key):
    key_size = public_key.key_size // 8

    max_chunk_size = key_size - 2 * hashes.SHA256().digest_size - 2

    encrypted_chunks = []

    for i in range(0, len(data), max_chunk_size):
        chunk = data[i:i + max_chunk_size]

        encrypted_chunk = public_key.encrypt(
            chunk,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        encrypted_chunks.append(encrypted_chunk)

    return b"".join(encrypted_chunks)


def rsa_decrypt(data, private_key):
    key_size = private_key.key_size // 8

    decrypted_chunks = []

    for i in range(0, len(data), key_size):
        chunk = data[i:i + key_size]

        decrypted_chunk = private_key.decrypt(
            chunk,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        decrypted_chunks.append(decrypted_chunk)

    return b"".join(decrypted_chunks)


def benchmark_algorithm(name, filepath, data, keys):
    print(f"\nBenchmarking {name}...")
    average_enc = 0
    average_dec = 0
    
    output_directory = prepare_output_directory(name)
    filename = os.path.basename(filepath)
    filename_without_extension = os.path.splitext(filename)[0]

    encrypted_output = os.path.join(
        output_directory,
        f"{filename_without_extension}.encrypted"
    )
    
    decrypted_output = os.path.join(
        output_directory,
        f"{filename_without_extension}.decrypted"
    )

    if name == "AES":
        average_enc, average_dec = benchmark_aes(data, encrypted_output, decrypted_output, keys["aes"])

    elif name == "RSA":
        average_enc, average_dec  = benchmark_rsa(data, encrypted_output, decrypted_output, keys["rsa_public"], keys["rsa_private"])

    elif name == "Colunere":
         average_enc, average_dec = benchmark_colunere(filepath, encrypted_output, decrypted_output, keys["colunere"]
        )
    return average_enc, average_dec


def plot_results(results, operation):
    books = list(results.keys())
    algorithms = ["AES", "RSA", "Colunere"]

    x = range(len(books))
    width = 0.25

    plt.figure(figsize=(12, 6))

    for i, algorithm in enumerate(algorithms):
        values = [
            results[book][algorithm]
            for book in books
        ]

        positions = [
            j + (i - 1) * width
            for j in x
        ]

        plt.bar(
            positions,
            values,
            width=width,
            label=algorithm
        )

    plt.xticks(
        list(x),
        books,
        rotation=15
    )

    plt.xlabel("Text file")
    plt.ylabel("Time (seconds)")

    title = (
        "Encryption Performance"
        if operation == "encrypt"
        else "Decryption Performance"
    )

    plt.title(title)

    plt.legend()
    plt.grid(axis="y", alpha=0.3)

    plt.tight_layout()

    filename = (
        "encryption_performance.png"
        if operation == "encrypt"
        else "decryption_performance.png"
    )

    plt.savefig(filename, dpi=300)
    plt.show()


def prepare_output_directory(algorithm):
    directory = os.path.join(OUTPUTS_DIR, algorithm)
    os.makedirs(directory, exist_ok=True)
    return directory

def main():

    subprocess.run(
        ["make"],
        check=True
    )

    files = [
        os.path.join(BOOKS_DIR, filename)
        for filename in os.listdir(BOOKS_DIR)
        if filename.lower().endswith(".txt")
    ]

    files.sort()

    if len(files) != NUM_BOOKS:
        raise RuntimeError(
            f"Expected exactly {NUM_BOOKS} .txt files in "
            f"'{BOOKS_DIR}/', found {len(files)}."
        )

    print("Files:")
    for file in files:
        size = os.path.getsize(file)

        print(
            f"  {os.path.basename(file)} "
            f"({size / 1024:.2f} KB)"
        )

    print("\nGenerating keys...")

    aes_key = os.urandom(32)

    colunere_key = "SECRETKEY"

    rsa_private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )

    rsa_public_key = rsa_private_key.public_key()

    keys = {
        "aes": aes_key,
        "colunere": colunere_key,
        "rsa_private": rsa_private_key,
        "rsa_public": rsa_public_key
    }

    encryption_results = {}
    decryption_results = {}

    for filepath in files:

        filename = os.path.basename(filepath)

        print(f"\nFILE: {filename}")

        with open(filepath, "rb") as f:
            data = f.read()

        encryption_results[filename] = {}
        decryption_results[filename] = {}

        for algorithm in ["AES", "RSA", "Colunere"]:
                
            encryption_time, decryption_time = benchmark_algorithm(
                algorithm,
                filepath,
                data,
                keys
            )

            encryption_results[filename][algorithm] = encryption_time
            decryption_results[filename][algorithm] = decryption_time

    print("\nENCRYPTION RESULTS")

    for filename in encryption_results:
        print(f"\n{filename}")

        for algorithm in encryption_results[filename]:
            print(
                f"  {algorithm:8s}: "
                f"{encryption_results[filename][algorithm]:.6f} s"
            )

    print("\nDECRYPTION RESULTS")

    for filename in decryption_results:
        print(f"\n{filename}")

        for algorithm in decryption_results[filename]:
            print(
                f"  {algorithm:8s}: "
                f"{decryption_results[filename][algorithm]:.6f} s"
            )

    plot_results(
        encryption_results,
        "encrypt"
    )

    plot_results(
        decryption_results,
        "decrypt"
    )


if __name__ == "__main__":
    main()