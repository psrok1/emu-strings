import sys
import pefile

"""
@psrok1
MDAC_TYP.EXE doesn't pass unattended installation flag, so EULA prompt is blocking installation
This script overwrites RUNPROGRAM inside MDAC_TYP binary, adding "/q" argument to command line
"""

mdac = pefile.PE(sys.argv[1])

rsrc = mdac.DIRECTORY_ENTRY_RESOURCE.entries
rc_idx = [entry.id for entry in rsrc].index(pefile.RESOURCE_TYPE['RT_RCDATA'])
rc_params = mdac.DIRECTORY_ENTRY_RESOURCE.entries[rc_idx].directory.entries
runarg_idx = [str(e.name) for e in rc_params].index("RUNPROGRAM")
# Title is long enough to safely patch out :P
title_idx = [str(e.name) for e in rc_params].index("TITLE")
runarg_struct = rc_params[runarg_idx].directory.entries[0].data.struct
title_struct = rc_params[title_idx].directory.entries[0].data.struct
# Patching rsrc arguments
new_runarg = '"dasetup.exe" /q\x00\x00'
runarg_struct.OffsetToData = title_struct.OffsetToData
mdac.set_bytes_at_rva(runarg_struct.OffsetToData, new_runarg)
runarg_struct.Size = len(new_runarg)
with open(sys.argv[1], "wb") as f:
    f.write(mdac.write())
