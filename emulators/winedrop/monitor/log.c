#include <windows.h>
#include <wincrypt.h>
#include <stdarg.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include "base64.h"

unsigned int L_MAGIC = 0xf00ca11;

void log_init() {
    HCRYPTPROV hProv;

    CryptAcquireContext(&hProv, 0, 0,
                        PROV_RSA_FULL,
                        CRYPT_VERIFYCONTEXT | CRYPT_SILENT);
    CryptGenRandom(hProv, sizeof(L_MAGIC), (BYTE*)&L_MAGIC);
    CryptReleaseContext(hProv, 0);
}

void log_send(const char* channel, const char* fmt, ...)
{
    va_list args;
    size_t buf_size, encoded_size;
    char* buffer;
    char* encoded;

    va_start(args, fmt);

    buf_size = vsnprintf(NULL, 0, fmt, args);
    buffer = malloc(buf_size);
    vsnprintf(buffer, buf_size, fmt, args);

    encoded_size = buf_size*4/3 + 16;
    encoded = malloc(encoded_size);
    base64encode(buffer, buf_size, encoded, encoded_size);

    printf("*$winedrop%08X:%s:%s$*", L_MAGIC, channel, encoded);
    free(encoded);
    free(buffer);
    va_end(args);
}