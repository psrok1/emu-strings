#ifndef H_BSTRCHAIN
#define H_BSTRCHAIN

#include <stdlib.h>
#include "uthash/include/uthash.h"

typedef struct sVARStr {
    unsigned int type;
    void* dummy2;
    union {
        wchar_t* str;
        struct sVARStr* var;
    } val;
} VARStr, *PVARStr;

#define TRACKED_ENABLED 1
#define TRACKED_CONST   2

typedef struct sBStrTracked {
    wchar_t* ptr;
    unsigned int flags;
    UT_hash_handle hh;
} BStrTracked, *PBStrTracked;

typedef struct sConstBStrTracked {
    unsigned int chash;
    wchar_t* cstr;
    unsigned int flags;
    UT_hash_handle hh;
} ConstBStrTracked, *PConstBStrTracked;

extern unsigned int BStr_length(wchar_t* bstr);
extern wchar_t* BStr_new(wchar_t* wc, unsigned int len);
extern wchar_t* BStr_copy(wchar_t* bstr);
extern wchar_t* BStr_free(wchar_t* bstr);
extern unsigned int CBStr_hash(wchar_t* bstr);

extern void TBStr_scanned_const(wchar_t* bstr);
extern void TBStr_add_from_var(wchar_t* bstr);
extern void TBStr_add_from_const(wchar_t* cbstr);
extern void TBStr_disable(wchar_t* bstr);
extern void TBStr_clear(wchar_t* bstr);
extern void TBStr_dumpall();

#endif