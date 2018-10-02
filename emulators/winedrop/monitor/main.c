#include <stdio.h>
#include <stdlib.h>

#ifndef __stdcall
#define __stdcall __attribute__((stdcall))
#endif

#ifndef __thiscall
#define __thiscall __attribute__((thiscall))
#endif

int __stdcall hook_IgnoreQuit(void* original, void* this, int exitCode)
{
    printf("Tried to WScript.Quit()\n");
    return 1;
}

typedef int __stdcall (*fn_CHostObj_Sleep)(void* this, unsigned msSleep);

int __stdcall hook_IgnoreSleep(fn_CHostObj_Sleep original, void* this, unsigned msSleep) 
{
    if (msSleep >= 2000)
    {
        printf("Ignored sleep %d ms, waiting 500ms!\n");
        msSleep = 500;
    }
    return original(this, msSleep);
}

typedef int __thiscall (*fn_ParseSource)(void* this, void* execBody, void* oleScript, wchar_t* a3,
                                        void *a4, void *a5, 
                                        void *a6, void *a7, 
                                        void *a8, void *a9);

int __thiscall hook_ParseSource(void* this, fn_ParseSource original,
                               void* execBody, void* oleScript, wchar_t *code,
                               void *a4,
                               void *a5,
                               void *a6,
                               void *a7, 
                               void *a8, 
                               void *a9)
{
    printf("=== Code start\n");
    printf("%ls\n", code);
    printf("=== Code end\n");
    return original(this, execBody, oleScript, code, a4, a5, a6, a7, a8, a9);
}