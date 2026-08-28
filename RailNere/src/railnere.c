#include <stdio.h>
#include <unistd.h>

#include "railFence.h" // "rf_" functions
#include "vigenere.h" // "vg_" functions


int main(int argc, char **argv){
    if (argc != 2){
        printf("Uma Flag Deve Ser Especificada: '-e' (encrypt) ou '-d' (decrypt)\n");
        return -1;
    }

    char flag = 0;
    int opt;
    while ((opt = getopt(argc, argv, "ed")) != -1){
        if (opt == 'e' || opt == 'd'){
            flag = opt;
            break;
        }
    }

    if (!flag){
        printf("Uma Flag Deve Ser Especificada: '-e' (encrypt) ou '-d' (decrypt)\n");
        return -1;   
    }

    printf("Opção Escolhida: %c\n", flag);
    return 0;
}
