#include <windows.h>
#include <stdio.h>
#include <stdlib.h>
#include "log.h"
#include "bstrchain.h"

#ifndef __stdcall
#define __stdcall __attribute__((stdcall))
#endif

#ifndef __thiscall
#define __thiscall __attribute__((thiscall))
#endif

#ifndef __regcall
#define __regcall __stdcall __attribute__((regparm(3)))
#endif

typedef struct {
    void* dummy1;
    void* dummy2;
    wchar_t* code;
    wchar_t* line;
    wchar_t* token_start;
    wchar_t* token_end;
} Scanner, *PScanner;

/*** 
 * JSCRIPT.DLL 
 ***/

typedef int __stdcall (*fn_ConcatStrs)(PVARStr dest, PVARStr s1, PVARStr s2);

int __stdcall hook_ConcatStrs(fn_ConcatStrs original, PVARStr dest, PVARStr s1, PVARStr s2)
{
    int retval = original(dest, s1, s2);
    chain_AddString(dest->val.var->val.str, s1->val.str, s2->val.str);
    return retval;
}

/*** 
 * VBSCRIPT.DLL 
 ***/

typedef PVARStr __stdcall (*fn_rtConcatBStr)(wchar_t *s1, wchar_t* s2);

PVARStr __stdcall hook_rtConcatBStr(fn_rtConcatBStr original, wchar_t* s1, wchar_t* s2)
{
    PVARStr retval = original(s1, s2);
    chain_AddString(retval->val.str, s1, s2);
    return retval;
}

/*** 
 * JSCRIPT.DLL 
 * VBSCRIPT.DLL
 ***/

typedef int __thiscall (*fn_Scanner_ScanStringConstant)(PScanner this, unsigned int chStr);

int __thiscall hook_ScanStringConstant(PScanner this, 
                                       fn_Scanner_ScanStringConstant original, 
                                       unsigned int chStr)
{
    int len, retval = original(this, chStr);
    len = this->token_end - this->token_start - 2;
    wchar_t* token = BStr_new(this->token_start+1, len);
    log_send("string", "%u:0:%ls",len,token);
    BStr_free(token);
    return retval;
}

/*** 
 * CSCRIPT.EXE
 ***/

int __stdcall hook_IgnoreQuit(void* original, void* this, int exitCode)
{
    log_send("notice", "WScript.Quit called with exit code %u - ignored", exitCode);
    return 1;
}

/*** 
 * CSCRIPT.EXE
 ***/

typedef int __stdcall (*fn_CHostObj_Sleep)(void* this, unsigned msSleep);

int __stdcall hook_IgnoreSleep(fn_CHostObj_Sleep original, void* this, unsigned msSleep) 
{
    if (msSleep >= 2000)
    {
        log_send("notice", "WScript.Sleep called with %u ms - waiting only 500ms", msSleep);
        msSleep = 500;
    }
    return original(this, msSleep);
}

/*** 
 * JSCRIPT.DLL
 ***/

typedef int __thiscall (*fn_jscript_Parser_ParseSource)(void* this, void* execBody, void* oleScript, wchar_t* a3,
                                        void *a4, void *a5, 
                                        void *a6, void *a7, 
                                        void *a8, void *a9);

int __thiscall hook_jscript_ParseSource(void* this, fn_jscript_Parser_ParseSource original,
                               void* execBody, void* oleScript, wchar_t *code,
                               void *a4,
                               void *a5,
                               void *a6,
                               void *a7, 
                               void *a8, 
                               void *a9)
{
    log_send("snippet", "%ls", code);
    return original(this, execBody, oleScript, code, a4, a5, a6, a7, a8, a9);
}

/*** 
 * VBSCRIPT.DLL
 ***/

typedef int __thiscall (*fn_vbscript_Parser_ParseSource)(void* this, void* execBody, void* oleScript, wchar_t* a3,
                                        void *a4, void *a5, 
                                        void *a6, void *a7, 
                                        void *a8, void *a9, void* a10);

int __thiscall hook_vbscript_ParseSource(void* this, fn_vbscript_Parser_ParseSource original,
                               void* execBody, void* oleScript, wchar_t *code,
                               void *a4,
                               void *a5,
                               void *a6,
                               void *a7, 
                               void *a8, 
                               void *a9,
                               void *a10)
{
    log_send("snippet", "%ls", code);
    return original(this, execBody, oleScript, code, a4, a5, a6, a7, a8, a9, a10);
}

/*** 
 * Entrypoint
 ***/

BOOL WINAPI DllMain(
    HINSTANCE hinstDLL,  // handle to DLL module
    DWORD fdwReason,     // reason for calling function
    LPVOID lpReserved )  // reserved
{
    if(fdwReason == DLL_PROCESS_ATTACH)
    {
        log_init();
        log_send("init", "Hello");
    } 
    else if (fdwReason == DLL_PROCESS_DETACH)
    {
        chain_Flush();
    }
    
    return TRUE;  // Successful DLL_PROCESS_ATTACH.
}