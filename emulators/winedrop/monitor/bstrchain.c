#include <stdio.h>
#include <string.h>
#include "log.h"
#include "bstrchain.h"

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

BStrTracked* strings = NULL;
ConstBStrTracked* consts = NULL;

void TBStr_scanned_const(wchar_t* bstr)
{
    /* Should be copied via BStr_new */
    ConstBStrTracked *s;

    unsigned int hash = BStr_hash(bstr);

    HASH_FIND_INT(consts, &hash, s);
    if (s == NULL)
    {
        s = (ConstBStrTracked*)malloc(sizeof *s);
        s->chash = hash;
        s->cstr = bstr;
        s->flags = TRACKED_ENABLED;
        HASH_ADD_INT( consts, chash, s );
    }
}

void TBStr_add(wchar_t* bstr, unsigned int flags)
{
    /* Handling dynamic or unbound strings */
    BStrTracked * s;

    if(BStr_length(bstr) <= 3)
        return;


    HASH_FIND_INT(strings, &bstr, s);
    if (s == NULL) 
    {
        s = (BStrTracked*)malloc(sizeof *s);
        s->ptr = bstr;
        s->flags = flags;
        HASH_ADD_INT( strings, ptr, s );
    }
}

void TBStr_add_from_var(wchar_t* bstr)
{
    TBStr_add(bstr, TRACKED_ENABLED);
}


void TBStr_add_from_const(wchar_t* cbstr)
{
    /**
     * CBStr format:
     * [4-byte hash][4-byte length][wide string]
     *                             ^
     *                              --- BStr pointer
     */
    TBStr_add(cbstr, TRACKED_ENABLED | TRACKED_CONST);
}

void TBStr_disable(wchar_t* bstr)
{
    BStrTracked *s;
    ConstBStrTracked *cs;

    HASH_FIND_INT(strings, &bstr, s);
    if (s != NULL)
    {
        if(!(s->flags & TRACKED_ENABLED))
            return;
        s->flags &= ~TRACKED_ENABLED;
        if(s->flags & TRACKED_CONST)
        {
            unsigned int hash;
            hash = CBStr_hash(bstr);
            HASH_FIND_INT(consts, &hash, cs);
            if (cs != NULL)
            {
                cs->flags &= ~TRACKED_ENABLED;
            }
        }
    }
}

void TBStr_clear(wchar_t* bstr)
{
    BStrTracked *s;
    ConstBStrTracked *cs;
    
    HASH_FIND_INT(strings, &bstr, s);
    if (s == NULL || (s->flags & TRACKED_ENABLED))
        log_send('s', "%ls", bstr);
    
    if (s != NULL)
    {
        if(s->flags & TRACKED_CONST)
        {
            unsigned int hash;
            hash = CBStr_hash(bstr);
            HASH_FIND_INT(consts, &hash, cs);
            if (cs != NULL)
            {
                BStr_free(cs->cstr);
                HASH_DEL(consts, cs);
                free(cs);
            }
        }
        HASH_DEL(strings, s);
        free(s);
    }
}

void TBStr_dumpall()
{
    BStrTracked *s, *stmp;
    ConstBStrTracked *cs, *cstmp;

    HASH_ITER(hh, strings, s, stmp) {
        HASH_DEL(strings, s);
        if((s->flags & TRACKED_ENABLED) && !(s->flags & TRACKED_CONST))
            log_send('s', "%ls", s->ptr);
        free(s);
    }

    HASH_ITER(hh, consts, cs, cstmp) {
        HASH_DEL(consts, cs);
        if(cs->flags & TRACKED_ENABLED)
            log_send('s', "%ls", cs->cstr);
        BStr_free(cs->cstr);
        free(cs);
    }
}
