#include "bstr.h"

/**
 * BStr format:
 * [4-byte length][wide string]
 * ^              ^ BStr
 * \---BStrPtr
 */

wchar_t* BStrPtr_to_BStr(void* ptr) {
    return (wchar_t*)(((char*)ptr) + 4);
}

void* BStr_to_BStrPtr(wchar_t* bstr) {
    return ((char*)bstr) - 4;
}

unsigned int BStr_byte_length(wchar_t* bstr)
{
    return *((unsigned int*)BStr_to_BStrPtr(bstr));
}

unsigned int BStr_length(wchar_t* bstr)
{
    return BStr_byte_length(bstr) >> 1;
}

wchar_t* BStr_new(wchar_t* wc, unsigned int len)
{
    void* obj = malloc((len+1)*2 + 4);
    *((unsigned int*)obj) = len*2;
    wchar_t* nwc = BStrPtr_to_BStr(obj);
    memcpy(nwc, wc, len*2);
    nwc[len] = L'\x00';
    return nwc;
}

wchar_t* BStr_copy(wchar_t* bstr)
{
    return BStr_new(bstr, BStr_length(bstr));
}

wchar_t* BStr_free(wchar_t* bstr)
{
    free(BStr_to_BStrPtr(bstr));
}

unsigned int BStr_hash(wchar_t* bstr)
{
    /* From jscript@CaseInsensitiveComputeHashCch */
    unsigned int length = BStr_length(bstr);
    unsigned int result = 0;
    wchar_t* ptr = bstr;
    wchar_t ch;
    while(length > 0)
    {
        ch = *(ptr++);
        length -= 1;
        if ((ch - 65) <= 25)
            ch += 32;
        result = ch + 17 * result;
    }
    return result;
}

unsigned int CBStr_hash(wchar_t* bstr)
{
    return *(unsigned int*)(((char*)bstr) - 8);
}
