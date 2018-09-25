#!/bin/bash

export WINETRICKS_LIB=1
source ../patches/winetricks

### Install WSH57
w_call wsh57

### Install MDAC28, but apply mdac_unattended_fix.py first

load_mdac28()
{
    # https://www.microsoft.com/en-us/download/details.aspx?id=5793
    w_download https://download.microsoft.com/download/4/a/a/4aafff19-9d21-4d35-ae81-02c48dcbbbff/MDAC_TYP.EXE 157ebae46932cb9047b58aa849ac1885e8cbd2f218810cb83e57613b49c679d6
    w_try python mdac_unattended_fix.py "$W_CACHE"/"$W_PACKAGE"/MDAC_TYP.EXE
    load_native_mdac
    w_set_winver nt40
    w_try_cd "$W_CACHE"/"$W_PACKAGE"
    w_try "$WINE" mdac_typ.exe ${W_OPT_UNATTENDED:+ /q /C:"setup $W_UNATTENDED_SLASH_QNT"}
    w_unset_winver
}

w_call mdac28

WINESYSTEM32="$WINEPREFIX/drive_c/windows/system32"

w_try python pdblib/dl_syms.py "$WINESYSTEM32/jscript.dll"
w_try python pdblib/dl_syms.py "$WINESYSTEM32/vbscript.dll"
w_try python pdblib/dl_syms.py "$WINESYSTEM32/cscript.exe"
