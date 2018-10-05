#ifndef H_BSTRCHAIN
#define H_BSTRCHAIN

#include <stdlib.h>

typedef struct sVARStr {
    void* dummy1;
    void* dummy2;
    union {
        wchar_t* str;
        struct sVARStr* var;
    } val;
} VARStr, *PVARStr;

extern unsigned int BStr_length(wchar_t* bstr);
extern wchar_t* BStr_new(wchar_t* wc, unsigned int len);
extern wchar_t* BStr_copy(wchar_t* bstr);
extern wchar_t* BStr_free(wchar_t* bstr);

extern void chain_Flush();
extern void chain_AddString(wchar_t* dest, wchar_t* s1, wchar_t* s2);

#endif