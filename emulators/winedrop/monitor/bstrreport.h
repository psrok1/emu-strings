#ifndef H_BSTRREPORT
#define H_BSTRREPORT

#include <stdlib.h>
#include "uthash/include/uthash.h"


typedef struct sBStrReported {
    wchar_t* ptr;
    UT_hash_handle hh;
} BStrReported, *PBStrReported;

extern void RBStr_send(wchar_t* bstr);

#endif