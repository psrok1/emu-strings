#include <windows.h>
#include <wincrypt.h>
#include <stdarg.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>

#define MAX_CHUNK_LEN 1024

unsigned int L_MAGIC = 0xf00ca11;

void log_init() {
    HCRYPTPROV hProv;

    CryptAcquireContext(&hProv, 0, 0,
                        PROV_RSA_FULL,
                        CRYPT_VERIFYCONTEXT | CRYPT_SILENT);
    CryptGenRandom(hProv, sizeof(L_MAGIC), (BYTE*)&L_MAGIC);
    CryptReleaseContext(hProv, 0);
}

void log_send_raw(const char* data, unsigned int length)
{
    char buffer[MAX_CHUNK_LEN*2], preflen = 0;
    preflen = snprintf(buffer, MAX_CHUNK_LEN*2, "\n*$wdrop%08X:%u:", L_MAGIC, length);
    memcpy(buffer + preflen, data, length);
    write(1, buffer, preflen + length);
}

void log_send(char type, const char* fmt, ...)
{
    va_list args;
    size_t buf_size, encoded_size;
    char* buffer, *pbuf;
    char* encoded;

    va_start(args, fmt);

    buf_size = vsnprintf(NULL, 0, fmt, args);
    pbuf = buffer = malloc(buf_size + 1);
    vsnprintf(buffer + 1, buf_size, fmt, args);

    while(buf_size > MAX_CHUNK_LEN)
    {
        *buffer = 'p';
        log_send_raw(buffer, MAX_CHUNK_LEN + 1);
        buf_size -= MAX_CHUNK_LEN;
        pbuf += MAX_CHUNK_LEN;
        memcpy(buffer + 1, pbuf, min(buf_size, MAX_CHUNK_LEN));
    }
    *buffer = type;

    log_send_raw(buffer, buf_size + 1);
    free(buffer);
    va_end(args);
}