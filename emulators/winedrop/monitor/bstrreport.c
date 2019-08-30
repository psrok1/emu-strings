#include "bstrreport.h"
#include "bstr.h"
#include "log.h"

BStrReported* rstrings = NULL;

void RBStr_send(wchar_t* bstr)
{
    BStrReported* record;

    HASH_FIND(hh, rstrings, bstr, BStr_byte_length(bstr), record);
    if(!record) {
        wchar_t* rep_bstr = BStr_copy(bstr);
        record = (BStrReported*)malloc(sizeof *record);
        record->ptr = rep_bstr;
        HASH_ADD_KEYPTR(hh, rstrings, record->ptr, BStr_byte_length(bstr), record);
        log_send('n', "%ls", bstr);
        log_send('s', "%ls", bstr);
    }
}