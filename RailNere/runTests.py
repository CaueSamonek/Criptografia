import os

# a ideia eh ter um arquivo com tudo pra plotar direto,
# ai soh chama plot(metrics) ou um plot() pra cada metrica, enfim
import plot

TEST_FILES_DIR = "tests"
VIGENERE_KEY = "criptografodase" #input("Digite a chave do Vigenere:")
RAIL_FENCE_COL = 4 #int(input("Digite a largura da matriz do Rail Fence:"))

# antes de executar os testes eh bom rodar um 'make'
# Subprocess.run() make ?

for root, subdir, files in os.walk(TEST_FILES_DIR):
    for file in files:
        path = os.path.join(root, file)
        if subdir: # accepts only leaf directories from the test dir
            continue

        # for each test file
        print(path)

        # hardcode as 3 ou fazer algo assim
        #for cipher in ciphers:
            # start = get time stamp ()
            # run encrypt cipher(path, VIGENERE_KEY, RAIL_FENCE_COL)
            # end = get time stamp ()

            # start = get time stamp ()
            # run decrypt cipher(path, VIGENERE_KEY, RAIL_FENCE_COL)
            # end = get time stamp ()

            # log/save cipher metrics

# call plot(metrics)
