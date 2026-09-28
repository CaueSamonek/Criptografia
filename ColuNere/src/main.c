#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

#include "columnarTransposition.h"
#include "vigenere.h"

// le todo o arquivo para a memoria
static char *read_file(const char *path) {
    FILE *file = fopen(path, "rb");
    if (!file) return NULL;

    fseek(file, 0, SEEK_END);
    long size = ftell(file);
    rewind(file);

    char *text = malloc(size + 1);
    if (!text) {
        fclose(file);
        return NULL;
    }

    fread(text, 1, size, file);
    fclose(file);
    text[size] = '\0';
    return text;
}

int main(int argc, char **argv) {
    char operation = 0;
    int columns = 0;
    char *key = NULL;
    char *filename = NULL;
    int option;

    // le a operacao, as colunas, a chave e o arquivo
    while ((option = getopt(argc, argv, "edc:k:f:")) != -1) {
        switch (option) {
        case 'e':
        case 'd':
            operation = option;
            break;
        case 'c':
            columns = atoi(optarg);
            break;
        case 'k':
            key = optarg;
            break;
        case 'f':
            filename = optarg;
            break;
        default:
            return 1;
        }
    }

    if (!operation || columns <= 0 || !key || !filename) {
        fprintf(stderr, "Uso: %s -e|-d -c <colunas> -k <chave> -f <arquivo>\n", argv[0]);
        return 1;
    }

    char *input = read_file(filename);
    if (!input) {
        fprintf(stderr, "Nao foi possivel ler %s\n", filename);
        return 1;
    }

    char *intermediate;
    char *output;

    // aplica as duas cifras na ordem correta
    if (operation == 'e') {
        intermediate = ct_encrypt(input, columns);
        output = vg_encrypt(intermediate, key);
    } else {
        intermediate = vg_decrypt(input, key);
        output = ct_decrypt(intermediate, columns);
    }

    // envia o resultado para a saida padrao
    printf("%s", output);
    free(input);
    free(intermediate);
    free(output);
    return 0;
}
