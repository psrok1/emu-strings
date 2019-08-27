#include "codechain.h"

CodeTracked* codeParsed = NULL;
CodeTracked* codeExecuted = NULL;
void* codeExecutedScr = NULL;
CodeTracked* codeByScrFncObjPtr = NULL;

unsigned int codeSeq = 0;
unsigned int lastOp = 0xFFFFFFFF;

unsigned int CodeTracked_parseStart()
{
    CodeTracked* ct;
    ct = (CodeTracked*)malloc(sizeof *ct);
    ct->codeSeqId = codeSeq;
    ct->containedIn = codeExecuted ? codeExecuted->codeSeqId : 0xFFFFFFFF;
    ct->opTracked = NULL;
    codeParsed = ct;
    return codeSeq++;
}

void CodeTracked_parseAddOp(unsigned int opPos, unsigned int exprStart, unsigned int exprEnd) {
    OpTracked* opt;
    opt = (OpTracked*)malloc(sizeof *opt);
    opt->opPos = opPos;
    opt->exprStart = exprStart;
    opt->exprEnd = exprEnd;
    HASH_ADD_INT(codeParsed->opTracked, opPos, opt);
}

unsigned int CodeTracked_parseFinish(void* ptrScrFncObj)
{
    if(codeParsed == NULL)
    {
        // Function declaration inside currently executed script
        codeParsed = codeExecuted;
    }
    codeParsed->codeScrFncObj = ptrScrFncObj;
    HASH_ADD_INT( codeByScrFncObjPtr, codeScrFncObj, codeParsed);
    int fnId = codeParsed->codeSeqId;
    codeParsed = NULL;
    return fnId;
}

unsigned int CodeTracked_executeStart(void* ptrScrFncObj)
{
    lastOp = 0xFFFFFFFF;
    if(codeExecutedScr != ptrScrFncObj)
    {
        codeExecutedScr = ptrScrFncObj;
        HASH_FIND_INT(codeByScrFncObjPtr, &ptrScrFncObj, codeExecuted);
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
    codepos->codeSeqId = codeParsed->codeSeqId;
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
