#include "columnarTransposition.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// Adiciona padding pro tamanho ser multiplo de cols
char* ct_addPadding(const char* txt, int cols){
    int len = strlen(txt);
    int rows = (len + cols - 1) / cols;
    int size = rows * cols;

    char* out = malloc(size + 1);

    memcpy(out, txt, len);
    memset(out + len, CT_PAD, size - len);

    out[size] = '\0';
    return out;
}

char* ct_transpose(const char* txt, int rows, int cols){
    int len = rows * cols;
    char* out = malloc(len + 1);

    for (int rb = 0; rb < rows; rb += CT_BLOCK)
        for (int cb = 0; cb < cols; cb += CT_BLOCK)
            for (int r = rb; r < rb + CT_BLOCK && r < rows; r++)
                for (int c = cb; c < cb + CT_BLOCK && c < cols; c++)
                    out[c * rows + r] = txt[r * cols + c];

    out[len] = '\0';
    return out;
}

// Escreve em linhas e le em colunas
char* ct_encrypt(const char* txt, int cols){
    char* in = ct_addPadding(txt, cols);

    int rows = strlen(in) / cols;
    char* out = ct_transpose(in, rows, cols);
    free(in);

    return out;
}

// Escreve em colunas e le em linhas
char* ct_decrypt(const char* txt, int cols){
    int len = strlen(txt);
    int rows = len / cols;
    char* out = ct_transpose(txt, cols, rows);

    // Remove padding
    while (len > 0 && out[len - 1] == CT_PAD)
        len--;

    out[len] = '\0';
    return out;
}
