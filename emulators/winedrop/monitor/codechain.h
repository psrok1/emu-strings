#ifndef H_CODECHAIN
#define H_CODECHAIN

#include <stdlib.h>
#include "uthash/include/uthash.h"

typedef struct sOpTracked {
    unsigned int opPos;
    unsigned int exprStart;
    unsigned int exprEnd;
    UT_hash_handle hh;
} OpTracked, *POpTracked;

typedef struct sCodeTracked {
    void* codeCScriptBody;
    unsigned int codeSeqId;
    unsigned int containedIn;
    POpTracked opTracked;
    UT_hash_handle hh;
} CodeTracked, *PCodeTracked;

typedef struct sCodePosTracked {
    unsigned int codeSeqId;
    unsigned int exprStart;
    unsigned int exprEnd;
    struct sCodePosTracked* next;
} CodePosTracked, *PCodePosTracked;


extern unsigned int CodeTracked_compileStart();
extern void CodeTracked_compileAddOp(unsigned int opPos, unsigned int exprStart, unsigned int exprEnd);
extern unsigned int CodeTracked_compileFinish(void* ptrCScriptBody);
extern unsigned int CodeTracked_executeStart(void* ptrCScriptBody);
extern void CodeTracked_executeOp(unsigned int opPos);
extern CodePosTracked* CodeTracked_getCodePosForConst(unsigned int exprStart, unsigned int exprEnd);
extern CodePosTracked* CodeTracked_getCodePosByLastOp();

#endif