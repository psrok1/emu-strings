#ifndef H_BSTRREPORT
#define H_BSTRREPORT

#include <stdlib.h>
#include "codepos.h"
#include "uthash/include/uthash.h"

typedef struct sCodePosReported {
    CodePos pos;
    UT_hash_handle hh;
} CodePosReported, *PCodePosReported;

typedef struct sBStrReported {
    wchar_t* ptr;
    CodePosReported* codepos;
    UT_hash_handle hh;
} BStrReported, *PBStrReported;

extern void RBStr_send(wchar_t* bstr, CodePosTracked* source);

#endif