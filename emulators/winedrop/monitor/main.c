#include <windows.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include "log.h"
#include "bstr.h"
#include "bstrchain.h"
#include "bench.h"

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
    TBStr_add_from_var(dest->val.var->val.str);
    TBStr_disable(s1->val.str);
    TBStr_disable(s2->val.str);
    return retval;
}

/*** 
 * VBSCRIPT.DLL
 * rtConcatBStr is used by VbsVarAdd and VbsVarConcat
 ***/

typedef PVARStr __stdcall (*fn_rtConcatBStr)(wchar_t *s1, wchar_t* s2);

PVARStr __stdcall hook_rtConcatBStr(fn_rtConcatBStr original, wchar_t* s1, wchar_t* s2)
{
    PVARStr retval = original(s1, s2);
    TBStr_add_from_var(retval->val.str);
    TBStr_disable(s1);
    TBStr_disable(s2);
    return retval;
}

/*** 
 * JSCRIPT.DLL 
 ***/

typedef void __thiscall (*fn_VarClear)(PVARStr var);

void __thiscall hook_VarClear(PVARStr var, fn_VarClear original)
{
    if((var->type & 0xFFFF) == 8 || (var->type & 0xFFFF) == 74)
    {
        TBStr_clear(var->val.str);
    }
    original(var);
}

typedef void __thiscall (*fn_VarSetConstBstr)(PVARStr var, wchar_t *str, void *dummy);

void __thiscall hook_VarSetConstBstr(PVARStr var, fn_VarSetConstBstr original, wchar_t *str, void *dummy)
{
    original(var, str, dummy);
    TBStr_add_from_const(str);
}

// ?FInterrupt@CSession@@QAEHXZ

void triggerHalt_VBScript(void* session) {
    *((unsigned int*)(((char*)session)+0x44)) = 1;
    *((unsigned int*)(((char*)session)+0x40)) = 0;
    *((unsigned int*)(((char*)session)+0x4)) = 0;
}

void triggerHalt_JScript(void* session) {
    *((unsigned int*)(((char*)session)+0x248)) = 1;
    *((unsigned int*)(((char*)session)+0x244)) = 0;
    *((unsigned int*)(((char*)session)+0x4)) = 0;
}

unsigned int softTimeout = 45;

typedef int __thiscall (*fn_SessionFInterrupt)(void* session);

int __thiscall hook_SessionFInterrupt_JScript(void* session, fn_SessionFInterrupt original)
{
    if(timeElapsed() > softTimeout)
    {
        log_send('n', "Enforcing shutdown after %d seconds", softTimeout);
        triggerHalt_JScript(session);
    }
    return original(session);
}

int __thiscall hook_SessionFInterrupt_VBScript(void* session, fn_SessionFInterrupt original)
{
    int result;
    if(timeElapsed() > softTimeout)
    {
        log_send('n', "Enforcing shutdown after %d seconds", softTimeout);
        triggerHalt_VBScript(session);
    }
    return original(session);
}

int __cdecl hook_CScriptRuntimeRun_BOS_JScript(unsigned int edi,
                                               unsigned int esi,
                                               unsigned int ebp,
                                               unsigned int esp,
                                               unsigned int ebx,
                                               unsigned int edx,
                                               unsigned int ecx,
                                               unsigned int eax)
{
    log_send('n', "BOS (%d, %d)", eax, esi);
}

int __cdecl hook_ParserGenPCode_JScript(char* parserPtr,
                                        unsigned int opcode,
                                        unsigned int ebp,
                                        unsigned int esp,
                                        unsigned int ebx,
                                        unsigned int edx,
                                        unsigned int ecx,
                                        unsigned int eax)
{
    unsigned int opOffset, codeStart, codeEnd;
    unsigned int *parseNode;
    if(opcode == 0x4F) // a+b
    {
        opOffset = *(unsigned int*)(parserPtr + 0xB4);
        parseNode = *(unsigned int*)(ebp+16);
        if(*parseNode > 0x80)
            parseNode = *(unsigned int*)(ebp+12);
        codeStart = parseNode[2];
        codeEnd = parseNode[3];
        log_send('n', "Concat found (op %d) - chars %d..%d", opOffset, codeStart, codeEnd);
    }
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
    if(len > 3)
    {
        wchar_t* token = BStr_new(this->token_start+1, len);
        TBStr_scanned_const(token);
    }
    return retval;
}

/*** 
 * CSCRIPT.EXE
 ***/

int __stdcall hook_IgnoreQuit(void* original, void* this, int exitCode)
{
    log_send('n', "WScript.Quit called with exit code %u - ignored", exitCode);
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
        log_send('n', "WScript.Sleep called with %u ms - waiting only 500ms", msSleep);
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
    log_send('c', "%ls", code);
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
    log_send('c', "%ls", code);
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
    char timeoutBuf[32];
    if(fdwReason == DLL_PROCESS_ATTACH)
    {
        log_init();
        log_send('n', "Monitor started");
        if(GetEnvironmentVariable("TIMEOUT", timeoutBuf, 31))
        {
            softTimeout = atoi(timeoutBuf);
            log_send('n', "Soft timeout set to %d", softTimeout);
        }
    } else if(fdwReason == DLL_PROCESS_DETACH)
    {
        log_send('n', "Graceful shutdown");
        TBStr_dumpall();
    }
    
    return TRUE;  // Successful DLL_PROCESS_ATTACH.
}