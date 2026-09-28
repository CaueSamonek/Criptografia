import os
import subprocess
import time

import matplotlib.pyplot as plt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding


TESTS_DIR = "tests"
OUTPUTS_DIR = "outputs"
COLUNERE_PROGRAM = "./colunere"
KEY = "chaveSecreta"
AES_KEY = KEY.encode().hex().ljust(64, "0") # completa a chave para 32 bytes
AES_IV = "0" * 32
REPETITIONS = 5 # calcula a media de cinco execucoes
RSA_PRIVATE_KEY = os.path.join(OUTPUTS_DIR, "rsa-private-key.pem")
RSA_PUBLIC_KEY = os.path.join(OUTPUTS_DIR, "rsa-public-key.pem")
RSA_INPUT_SIZE = 245
RSA_OUTPUT_SIZE = 256
ALGORITHMS = [
    "ColuNere 4",
    "RSA",
    "AES",
]

# executa uma operacao de cifra sobre um arquivo
def run_cipher(algorithm, operation, input_file, output_file, key):
    if algorithm.startswith("ColuNere"):
        # executa o binario em C com a quantidade escolhida de colunas
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
        # executa o aes da openssl uma vez para o arquivo inteiro
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
        # define a chave e o tamanho dos blocos para cada operacao
        if operation == "encrypt":
            key_file = RSA_PUBLIC_KEY
            input_size = RSA_INPUT_SIZE
        else:
            key_file = RSA_PRIVATE_KEY
            input_size = RSA_OUTPUT_SIZE

        with open(key_file, "rb") as source:
            key_data = source.read()

        if operation == "encrypt":
            rsa_key = serialization.load_pem_public_key(key_data)
        else:
            rsa_key = serialization.load_pem_private_key(key_data, password=None)

        # reutiliza a chave carregada para todos os blocos do arquivo
        with open(input_file, "rb") as source:
            with open(output_file, "wb") as output:
                while block := source.read(input_size):
                    if operation == "encrypt":
                        result = rsa_key.encrypt(block, padding.PKCS1v15())
                    else:
                        result = rsa_key.decrypt(block, padding.PKCS1v15())
                    output.write(result)
        return

    subprocess.run(command, check=True)


def benchmark(algorithm, input_file):
    # separa os resultados por algoritmo e faixa de tamanho
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
        # usa a chave de 32 bytes somente no aes
        if algorithm == "AES":
            key = AES_KEY

        # mede a cifragem incluindo entrada e saida
        start = time.perf_counter_ns()
        run_cipher(algorithm, "encrypt", input_file, encrypted_file, key)
        encryption_times.append((time.perf_counter_ns() - start) / 1_000_000_000)

        # mede a decifragem incluindo entrada e saida
        start = time.perf_counter_ns()
        run_cipher(algorithm, "decrypt", encrypted_file, decrypted_file, key)
        decryption_times.append((time.perf_counter_ns() - start) / 1_000_000_000)

    # confirma que a decifragem recuperou exatamente o arquivo original
    with open(input_file, "rb") as original:
        with open(decrypted_file, "rb") as decrypted:
            assert original.read() == decrypted.read()

    return {
        "encryption": sum(encryption_times) / REPETITIONS,
        "decryption": sum(decryption_times) / REPETITIONS,
    }

def format_size(size):
    if size >= 1_000_000_000:
        return f"{size / 1_000_000_000:g}G"
    if size >= 1_000_000:
        return f"{size / 1_000_000:g}M"
    return f"{size / 1000:g}K"


# gera um grafico com os algoritmos escolhidos
def plot_results(results, operation, algorithms, suffix):
    plt.figure(figsize=(18, 8))
    books = list(results)
    positions = list(range(len(books)))
    sizes = [results[book]["size"] for book in books]
    labels = [format_size(size) for size in sizes]

    for algorithm in algorithms:
        values = [results[book][algorithm][operation] for book in books]
        plt.plot(positions, values, marker="o", label=algorithm)

    plt.xticks(positions, labels, rotation=45, ha="right", fontsize=8)
    plt.xlabel("Tamanho do arquivo")
    plt.ylabel("Tempo médio por execução (segundos)")
    title = "Cifragem" if operation == "encryption" else "Decifragem"
    plt.title(title + " — média de 5 execuções")
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUTS_DIR, operation + "_" + suffix + ".png"), dpi=200)
    plt.close()

# encontra todos os txt e ordena pelo tamanho
def get_test_files():
    books = []
    for directory, _, files in os.walk(TESTS_DIR):
        for filename in files:
            if filename.endswith(".txt"):
                books.append(os.path.join(directory, filename))
    books.sort(key=os.path.getsize)
    return books


def main():
    # compila o colunere antes dos testes
    subprocess.run(["make"], check=True)
    os.makedirs(OUTPUTS_DIR, exist_ok=True)

    books = get_test_files()

    # cria o par rsa somente quando os arquivos pem nao existem
    if not os.path.exists(RSA_PRIVATE_KEY):
        subprocess.run(
            [
                "openssl", "genpkey",
                "-algorithm", "RSA",
                "-pkeyopt", "rsa_keygen_bits:2048",
                "-out", RSA_PRIVATE_KEY,
            ],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    if not os.path.exists(RSA_PUBLIC_KEY):
        subprocess.run(
            [
                "openssl", "pkey",
                "-in", RSA_PRIVATE_KEY,
                "-pubout",
                "-out", RSA_PUBLIC_KEY,
            ],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    results = {}
    for book in books:
        print("Test ", book, flush=True)
        results[book] = {"size": os.path.getsize(book)}

        for algorithm in ALGORITHMS:
            results[book][algorithm] = benchmark(algorithm, book)

    for book in results:
        print("\n" + os.path.basename(book))
        for algorithm in ALGORITHMS:
            encryption = results[book][algorithm]["encryption"]
            decryption = results[book][algorithm]["decryption"]
            print(f"{algorithm} encrypt: {encryption:.9f} decrypt: {decryption:.9f}")

    plot_results(results, "encryption", ALGORITHMS, "all")
    plot_results(results, "encryption", ["ColuNere 4", "AES"], "noRSA")
    plot_results(results, "decryption", ALGORITHMS, "all")
    plot_results(results, "decryption", ["ColuNere 4", "AES"], "noRSA")


if __name__ == "__main__":
    main()
