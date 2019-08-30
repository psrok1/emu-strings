#include "bstrreport.h"
#include "bstr.h"
#include "log.h"

BStrReported* strings = NULL;

void RBStr_send(wchar_t* bstr)
{
    BStrReported* record;

    HASH_FIND(hh, strings, &bstr, BStr_byte_length(bstr), record);
    if(!record) {
        wchar_t* rep_bstr = BStr_copy(bstr);
        record = (BStrReported*)malloc(sizeof *record);
        record->ptr = rep_bstr;
        HASH_ADD(hh, strings, ptr, BStr_byte_length(bstr), record);
        log_send('s', "%ls", bstr);
    }
}