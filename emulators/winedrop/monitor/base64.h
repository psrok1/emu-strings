#ifndef H_BASE64
#define H_BASE64

#include <inttypes.h>

extern int base64encode(const void* data_buf, size_t dataLength, char* result, size_t resultSize);

#endif