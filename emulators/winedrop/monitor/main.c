#include <windows.h>
#include <stdio.h>
#include <stdlib.h>
#include "log.h"

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

typedef struct {
    void* dummy1;
    void* dummy2;
    wchar_t* str;
} VARStr, *PVARStr;

int VARStr_length(PVARStr var)
{
    return ((unsigned int*)var->str)[-1];
}

wchar_t* wnewstrcpy(wchar_t* src, int len)
{
    wchar_t* wc = malloc((len+1)*2);
    memcpy(wc, src, len*2);
    wc[len] = L'\x00';
    return wc;
}

typedef int __stdcall (*fn_ConcatStrs)(PVARStr dest, PVARStr s1, PVARStr s2);

int __stdcall hook_ConcatStrs(fn_ConcatStrs original, PVARStr dest, PVARStr s1, PVARStr s2)
{
    int retval = original(dest, s1, s2);
    wchar_t* first = wnewstrcpy(s1->str, VARStr_length(s1));
    wchar_t* second = wnewstrcpy(s2->str, VARStr_length(s2));
    log_send("string", "%u:%u:%ls%ls", VARStr_length(s1), VARStr_length(s2), first, second);
    free(first);
    free(second);
    return retval;
}

typedef int __thiscall (*fn_Scanner_ScanStringConstant)(PScanner this, unsigned int chStr);

int __thiscall hook_ScanStringConstant(PScanner this, 
                                       fn_Scanner_ScanStringConstant original, 
                                       unsigned int chStr)
{
    int len, retval = original(this, chStr);
    len = this->token_end - this->token_start - 2;
    wchar_t* token = wnewstrcpy(this->token_start+1, len);
    log_send("string", "%u:0:%ls",len,token);
    free(token);
    return retval;
}

int __stdcall hook_IgnoreQuit(void* original, void* this, int exitCode)
{
    log_send("notice", "WScript.Quit called with exit code %u - ignored", exitCode);
    return 1;
}

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

typedef int __thiscall (*fn_Parser_ParseSource)(void* this, void* execBody, void* oleScript, wchar_t* a3,
                                        void *a4, void *a5, 
                                        void *a6, void *a7, 
                                        void *a8, void *a9);

int __thiscall hook_ParseSource(void* this, fn_Parser_ParseSource original,
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
    return TRUE;  // Successful DLL_PROCESS_ATTACH.
}