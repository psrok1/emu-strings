#include <stdio.h>
#include <string.h>
#include "log.h"
#include "bstrchain.h"
#include "bstr.h"
#include "bstrreport.h"

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
    
    if(!bstr)
        return;

    HASH_FIND_INT(strings, &bstr, s);
    if (s == NULL || (s->flags & TRACKED_ENABLED))
        RBStr_send(bstr);
    
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
            RBStr_send(s->ptr);
        free(s);
    }

    HASH_ITER(hh, consts, cs, cstmp) {
        HASH_DEL(consts, cs);
        if(cs->flags & TRACKED_ENABLED)
            RBStr_send(cs->cstr);
        BStr_free(cs->cstr);
        free(cs);
    }
}
