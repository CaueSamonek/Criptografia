#ifndef VIGENERE_H
#define VIGENERE_H

// Aplica o deslocamento Vigenere: dir = 1 encrypt, dir = -1 decrypt
char* vg_apply(char* txt, char* key, int dir);

// wrappers
char* vg_encrypt(char* txt, char* key);
char* vg_decrypt(char* txt, char* key);

#endif // VIGENERE_H
