#include "codechain.h"
#include "bstrreport.h"
#include "bstr.h"
#include "log.h"

BStrReported* rstrings = NULL;

void RBStr_send(wchar_t* bstr, CodePosTracked* source)
{
    BStrReported* record;
    int string_reported = 0;

    HASH_FIND(hh, rstrings, bstr, BStr_byte_length(bstr), record);
    if(!record) {
        wchar_t* rep_bstr = BStr_copy(bstr);
        record = (BStrReported*)malloc(sizeof *record);
        record->ptr = rep_bstr;
        record->codepos = NULL;
        HASH_ADD_KEYPTR(hh, rstrings, record->ptr, BStr_byte_length(bstr), record);
        log_send('s', "%ls", bstr);
        string_reported = 1;
    }

    if(source)
    {
        CodePosTracked* el;
        for(el = source; el != NULL; el = el->hh.next) {
            CodePosReported* rep_pos;
            HASH_FIND(hh, record->codepos, &el->pos, sizeof(CodePos), rep_pos);
            if(!rep_pos) {
                if(!string_reported)
                {
                    string_reported = 1;
                    log_send('s', "%ls", bstr);
                }
                log_send('e', "%d:%d:%d", el->pos.codeSeqId, el->pos.exprStart, el->pos.exprEnd);
                rep_pos = (CodePosReported*)malloc(sizeof* rep_pos);
                rep_pos->pos.codeSeqId = el->pos.codeSeqId;
                rep_pos->pos.exprStart = el->pos.exprStart;
                rep_pos->pos.exprEnd = el->pos.exprEnd;
                HASH_ADD(hh, record->codepos, pos, sizeof(CodePos), rep_pos);
            }
        }
    }
}