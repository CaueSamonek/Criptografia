#include <stdlib.h>
#include <string.h>

#include "vigenere.h"

// desloca somente letras e preserva os outros caracteres
char* vg_apply(char* txt, char* key, int dir){
    int len = strlen(txt);
    int key_len = strlen(key);

    if (!key_len)
        return NULL;

    char* out = malloc(len + 1);
    if (!out)
        return NULL;

    int k = 0;

    for (int i = 0; i < len; i++){
        char c = txt[i];

        if ((c >= 'A' && c <= 'Z') || (c >= 'a' && c <= 'z')){
            int base = (c >= 'a') ? 'a' : 'A';
            unsigned char key_char = (unsigned char)key[k];
            int shift;

            // converte o byte da chave em um deslocamento de 0 a 25
            if ((key_char >= 'A' && key_char <= 'Z') ||
                (key_char >= 'a' && key_char <= 'z'))
                shift = (key_char | 32) - 'a';
            else
                shift = key_char % 26;

            // matriz de vigenere feita como linha+coluna=valor
            out[i] = base + (c - base + dir * shift + 26) % 26;
            if (++k == key_len)
                k = 0;
        }
        else
            out[i] = c;
    }

    out[len] = '\0';
    return out;
}

char* vg_encrypt(char* txt, char* key){
    return vg_apply(txt, key, 1);
}

char* vg_decrypt(char* txt, char* key){
    return vg_apply(txt, key, -1);
}
