#ifndef COLUMNAR_TRANSPOSITION_H
#define COLUMNAR_TRANSPOSITION_H

#define CT_BLOCK 32
#define CT_PAD 'X'

// Adiciona padding pro tamanho ser multiplo de cols
char* ct_addPadding(const char* txt, int cols);

// realiza transposicao de texto
char* ct_transpose(const char* txt, int rows, int cols);

// Escreve em linhas e le em colunas
char* ct_encrypt(const char* txt, int cols);

// Escreve em colunas e le em linhas
char* ct_decrypt(const char* txt, int cols);

#endif // COLUMNAR_TRANSPOSITION_H
