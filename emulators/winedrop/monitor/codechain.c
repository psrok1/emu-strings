#include "codechain.h"

CodeTracked* codeCompiled = NULL;
CodeTracked* codeExecuted = NULL;
void* codeExecutedBody = NULL;
CodeTracked* codeByCScriptBodyPtr = NULL;

unsigned int codeSeq = 0;
unsigned int lastOp = 0xFFFFFFFF;

unsigned int CodeTracked_compileStart()
{
    CodeTracked* ct;
    ct = (CodeTracked*)malloc(sizeof *ct);
    ct->codeSeqId = codeSeq;
    ct->containedIn = codeExecuted ? codeExecuted->codeSeqId : 0xFFFFFFFF;
    ct->opTracked = NULL;
    codeCompiled = ct;
    return codeSeq++;
}

void CodeTracked_compileAddOp(unsigned int opPos, unsigned int exprStart, unsigned int exprEnd) {
    OpTracked* opt;
    opt = (OpTracked*)malloc(sizeof *opt);
    opt->opPos = opPos;
    opt->exprStart = exprStart;
    opt->exprEnd = exprEnd;
    HASH_ADD_INT(codeCompiled->opTracked, opPos, opt);
}

unsigned int CodeTracked_compileFinish(void* ptrCScriptBody)
{
    codeCompiled->codeCScriptBody = ptrCScriptBody;
    HASH_ADD_INT( codeByCScriptBodyPtr, codeCScriptBody, codeCompiled);
    int fnId = codeCompiled->codeSeqId;
    codeCompiled = NULL;
    return fnId;
}

unsigned int CodeTracked_executeStart(void* ptrCScriptBody)
{
    lastOp = 0xFFFFFFFF;
    if(codeExecutedBody != ptrCScriptBody)
    {
        codeExecutedBody = ptrCScriptBody;
        HASH_FIND_INT(codeByCScriptBodyPtr, &ptrCScriptBody, codeExecuted);
    }
    return codeExecuted->codeSeqId;
}

void CodeTracked_executeOp(unsigned int opPos)
{
    lastOp = opPos;
}

CodePosTracked* CodeTracked_getCodePosForConst(unsigned int exprStart, unsigned int exprEnd) {
    CodePosTracked* codepos;
    codepos = (CodePosTracked*)malloc(sizeof *codepos);
    codepos->codeSeqId = codeCompiled->codeSeqId;
    codepos->exprStart = exprStart;
    codepos->exprEnd = exprEnd;
    return codepos;
}

CodePosTracked* CodeTracked_getCodePosByLastOp() {
    OpTracked* opt;
    CodePosTracked* codepos;
    HASH_FIND_INT( codeExecuted->opTracked, &lastOp, opt);
    if(opt)
    {
        codepos = (CodePosTracked*)malloc(sizeof *codepos);
        codepos->codeSeqId = codeExecuted->codeSeqId;
        codepos->exprStart = opt->exprStart;
        codepos->exprEnd = opt->exprEnd;
    } else
    {
        codepos = NULL;
    }
    lastOp = 0xFFFFFFFF;
    return codepos;
}

int CodeTracked_cmpCodePos(CodePosTracked *a, CodePosTracked *b) {
    return  !(a->codeSeqId == b->codeSeqId &&
              a->exprStart == b->exprStart &&
              a->exprEnd == b->exprEnd);
}