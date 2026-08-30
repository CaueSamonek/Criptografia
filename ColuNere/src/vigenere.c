#include <stdlib.h>
#include <string.h>

#include "vigenere.h"

// Aplica o deslocamento Vigenere: dir = 1 encrypt, dir = -1 decrypt
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
            int shift = (key[k] | 32) - 'a';

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
