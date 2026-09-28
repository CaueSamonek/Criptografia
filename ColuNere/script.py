import os
import subprocess
import time

import matplotlib.pyplot as plt


TESTS_DIR = "tests"
OUTPUTS_DIR = "outputs"
COLUNERE_PROGRAM = "./colunere"
KEY = "chaveSecreta"
AES_KEY = KEY.encode().hex().ljust(64, "0") # 32 bytes padding
AES_IV = "0" * 32
REPETITIONS = 5 # mean of 5
RSA_PRIVATE_KEY = os.path.join(OUTPUTS_DIR, "rsa-private.pem")
RSA_CERTIFICATE = os.path.join(OUTPUTS_DIR, "rsa-certificate.pem")
ALGORITHMS = [
    "ColuNere 4",
    "RSA",
    "AES",
]

# encrypt/decrypt with a cypher in a input file
def run_cipher(algorithm, operation, input_file, output_file, key):
    if algorithm.startswith("ColuNere"):
        columns = algorithm.split()[1]
        command = [
            COLUNERE_PROGRAM,
            "-e" if operation == "encrypt" else "-d",
            "-c", columns,
            "-k", key,
            "-f", input_file,
        ]

        with open(output_file, "wb") as output:
            subprocess.run(command, check=True, stdout=output)
        return

    if algorithm == "AES":
        command = ["openssl", "enc"]
        if operation == "decrypt":
            command.append("-d")

        command += [
            "-aes-256-cbc",
            "-K", key,
            "-iv", AES_IV,
            "-in", input_file,
            "-out", output_file,
        ]

    if algorithm == "RSA":
        if operation == "encrypt":
            command = [
                "openssl", "cms",
                "-encrypt",
                "-binary",
                "-aes-256-cbc",
                "-outform", "DER",
                "-in", input_file,
                "-out", output_file,
                RSA_CERTIFICATE,
            ]
        else:
            command = [
                "openssl", "cms",
                "-decrypt",
                "-binary",
                "-inform", "DER",
                "-in", input_file,
                "-out", output_file,
                "-recip", RSA_CERTIFICATE,
                "-inkey", RSA_PRIVATE_KEY,
                "-passin", "pass:" + key,
            ]

    subprocess.run(command, check=True)


def benchmark(algorithm, input_file):
    output_dir = os.path.join(OUTPUTS_DIR, algorithm)
    os.makedirs(output_dir, exist_ok=True)

    category = os.path.basename(os.path.dirname(input_file))
    filename = category + "_" + os.path.splitext(os.path.basename(input_file))[0]
    encrypted_file = os.path.join(output_dir, filename + ".encrypted")
    decrypted_file = os.path.join(output_dir, filename + ".decrypted")

    encryption_times = []
    decryption_times = []

    for _ in range(REPETITIONS):
        key = KEY
        # padded key
        if algorithm == "AES":
            key = AES_KEY

        # encrypt
        start = time.perf_counter_ns()
        run_cipher(algorithm, "encrypt", input_file, encrypted_file, key)
        encryption_times.append((time.perf_counter_ns() - start) / 1_000_000_000)

        # decrypt
        start = time.perf_counter_ns()
        run_cipher(algorithm, "decrypt", encrypted_file, decrypted_file, key)
        decryption_times.append((time.perf_counter_ns() - start) / 1_000_000_000)

    with open(input_file, "rb") as original:
        with open(decrypted_file, "rb") as decrypted:
            assert original.read() == decrypted.read()

    return {
        "encryption": sum(encryption_times) / REPETITIONS,
        "decryption": sum(decryption_times) / REPETITIONS,
    }

# plots time on size 
def plot_results(results, operation):
    plt.figure(figsize=(18, 8))
    books = list(results)
    algorithms = ALGORITHMS
    positions = list(range(len(books)))
    sizes = [results[book]["size"] for book in books]
    labels = [
        f"{size / 1_000_000_000:g}G" if size >= 1_000_000_000
        else f"{size / 1_000_000:g}M" if size >= 1_000_000
        else f"{size / 1000:g}K"
        for size in sizes
    ]

    for algorithm in algorithms:
        values = [results[book][algorithm][operation] for book in books]
        plt.plot(positions, values, marker="o", label=algorithm)

    plt.xticks(positions, labels, rotation=45, ha="right", fontsize=8)
    plt.xlabel("Tamanho do arquivo")
    plt.ylabel("Tempo (segundos)")
    plt.title(operation.capitalize())
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUTS_DIR, operation + ".png"), dpi=200)
    plt.close()

# read .txt files from TESTS_DIR
def get_test_files():
    books = []
    for directory, _, files in os.walk(TESTS_DIR):
        for filename in files:
            if filename.endswith(".txt"):
                books.append(os.path.join(directory, filename))
    books.sort(key=os.path.getsize)
    return books


def main():
    # generate colunere binary
    subprocess.run(["make"], check=True)
    os.makedirs(OUTPUTS_DIR, exist_ok=True)

    books = get_test_files()

    # create key for RSA
    if not os.path.exists(RSA_PRIVATE_KEY):
        subprocess.run(
            [
                "openssl", "req",
                "-x509",
                "-newkey", "rsa:2048",
                "-keyout", RSA_PRIVATE_KEY,
                "-out", RSA_CERTIFICATE,
                "-passout", "pass:" + KEY,
                "-subj", "/CN=benchmark",
                "-days", "1",
            ],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    results = {}
    for book in books:
        print("Test ", book)
        results[book] = {"size": os.path.getsize(book)}

        for algorithm in ALGORITHMS:
            results[book][algorithm] = benchmark(algorithm, book)

    for book in results:
        print("\n" + os.path.basename(book))
        for algorithm in ALGORITHMS:
            encryption = results[book][algorithm]["encryption"]
            decryption = results[book][algorithm]["decryption"]
            print(f"{algorithm} encrypt: {encryption:.9f} decrypt: {decryption:.9f}")

    plot_results(results, "encryption")
    plot_results(results, "decryption")


if __name__ == "__main__":
    main()
