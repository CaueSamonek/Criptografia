#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

#include "columnarTransposition.h" // "ct_" functions
#include "vigenere.h"              // "vg_" functions

int main(int argc, char **argv){
    char flag = 0;
    int ct_cols = 0;
    char* vg_key = NULL;
    char* txt_file = NULL;
    int opt;

    while ((opt = getopt(argc, argv, "edc:k:f:")) != -1){
        switch (opt){
            case 'e':
            case 'd':
                flag = opt;
                break;

            case 'c':
                ct_cols = atoi(optarg);
                break;

            case 'k':
                vg_key = optarg;
                break;

            case 'f':
                txt_file = optarg;
                break;

            default:
                printf("Uso: %s -e|-d -c <cols> -k <key> -f <file>\n", argv[0]);
                return -1;
        }
    }

    if (!flag){
        printf("Uma Flag Deve Ser Especificada: '-e' (encrypt) ou '-d' (decrypt)\n");
        return -1;
    }

    if (!ct_cols || ct_cols <= 0){
        printf("O Número de Colunas Deve Ser Positivo e Especificado com '-c'.\n");
        return -1;
    }

    if (!vg_key){
        printf("A Chave Vigenere Deve Ser Especificada com '-k'.\n");
        return -1;
    }

    if (!txt_file){
        printf("Um Arquivo Deve Ser Especificado com '-f'.\n");
        return -1;
    }

    printf("Opção Escolhida: %c\n", flag);
    printf("Chave Escolhida: %s\n", vg_key);
    printf("Número de Colunas: %d\n", ct_cols);
    
    char* out1 = vg_encrypt(ct_encrypt(txt_file, ct_cols), vg_key);
    printf("Texto Criptografado:\n%s\n", out1);

    char* out2 = ct_decrypt(vg_decrypt(out1, vg_key), ct_cols);
    printf("Texto Descriptografado:\n%s\n", out2);

    return 0;
}
