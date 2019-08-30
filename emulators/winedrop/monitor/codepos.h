#ifndef H_CODEPOS
#define H_CODEPOS

#include <stdlib.h>
#include "uthash/include/uthash.h"


typedef struct sCodePos {
    unsigned int codeSeqId;
    unsigned int exprStart;
    unsigned int exprEnd;
} CodePos, *PCodePos;


#endif