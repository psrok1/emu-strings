#include <stdio.h>
#include <string.h>
#include "log.h"
#include "bstrchain.h"

wchar_t* BStrPtr_to_BStr(void* ptr) {
    return (wchar_t*)(((char*)ptr) + 4);
}

void* BStr_to_BStrPtr(wchar_t* bstr) {
    return ((char*)bstr) - 4;
}


unsigned int BStr_length(wchar_t* bstr)
{
    return *((unsigned int*)BStr_to_BStrPtr(bstr))/2;
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


wchar_t* chain_last_dest = NULL;
wchar_t* chain_first = NULL, *chain_second = NULL;

void chain_FreeBuffers()
{
    if(chain_first)
    {
        BStr_free(chain_first);
        chain_first = NULL;
    }
    if(chain_second)
    {
        BStr_free(chain_second);
        chain_second = NULL;
    }
}

void chain_Flush() {
    if(chain_first && chain_second)
    {
        chain_last_dest = NULL;
        log_send("string", "%u:%u:%ls%ls", BStr_length(chain_first), BStr_length(chain_second), chain_first, chain_second);
    }
    chain_FreeBuffers();
}

void chain_AddString(wchar_t* dest, wchar_t* s1, wchar_t* s2)
{
    if(chain_last_dest && chain_last_dest != s1)
    {
        chain_Flush();
    }
    chain_FreeBuffers();
    chain_first = BStr_copy(s1);
    chain_second = BStr_copy(s2);
    chain_last_dest = dest;
    // For long strings concatenation we'll get better results if we report them immediately
    if(BStr_length(chain_first) >= 3 && BStr_length(chain_second) >= 3)
    {
        chain_Flush();
    }
}
