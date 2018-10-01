#include <stdio.h>

#ifndef __stdcall
#define __stdcall __attribute__((stdcall))
#endif

int __stdcall hook_IgnoreQuit(void* original, int exitCode)
{
    printf("Tried to WScript.Quit()");
    return 0;
}