import struct
from pefile import PE

from yaml import load
from pdblib.read_syms import read_symbols

p32 = lambda d: struct.pack("<I", d & 0xFFFFFFFF)

"""
@psrok1
Instrumentation of WSH components using winedrop.dll and kind of magic
"""

class WSHInstrumentation(object):
    def __init__(self, libpath):
        self.libpath = libpath
        self.pe = PE(libpath)
        
        last_section = self.pe.sections[-1]
        # In case of uninitialized data at the end of section
        # Not needed now, so not implemented
        assert last_section.Misc_VirtualSize <= last_section.SizeOfRawData
        self.last_section = last_section
        # Set RWX
        self.last_section.IMAGE_SCN_MEM_WRITE = True
        self.last_section.IMAGE_SCN_MEM_EXECUTE = True
        # Move from mmap to str
        self.pe.__data__ = self.pe.__data__.read(self.pe.__data__.size())

    def next_rva(self):
        section = self.last_section
        return section.VirtualAddress + section.SizeOfRawData

    def append(self, data):
        section = self.last_section
        rva = self.next_rva()
        section.SizeOfRawData += len(data)
        section.Misc_VirtualSize = section.SizeOfRawData
        self.pe.__data__ += data
        return rva

    def align(self, alignment, padchar='\x00'):
        va = self.next_rva()
        pad = (alignment-va%alignment)
        self.append(pad*padchar)

    def rebuild_imports(self, routines):
        # Build string list
        rva_winedrop_dll = self.append("winedrop.dll\x00")
        rva_routine_str = []
        for r in routines:
            # hint (0) + name + terminator
            rva_routine_str.append(self.append('\x00\x00'+r+'\x00'))
        # 0x10 alignment
        self.align(16)
        # Build OriginalThunkList
        rva_oft = self.next_rva()
        for r in rva_routine_str:
            self.append(p32(r))
        self.append(p32(0))
        # 0x10 alignment
        self.align(16)
        # Build ThunkList
        rva_ft = self.next_rva()
        rva_iat = []
        for r in rva_routine_str:
            rva_iat.append(self.append(p32(r)))
        self.append(p32(0))
        # 0x10 alignment
        self.align(16)
        # Copy import table entries
        offs_imports = self.pe.get_offset_from_rva(self.pe.OPTIONAL_HEADER.DATA_DIRECTORY[1].VirtualAddress)
        rva_imports = self.next_rva()
        while True:
            entry = self.pe.__data__[offs_imports:offs_imports+20]
            if entry[:4] == "\x00\x00\x00\x00":
                break
            offs_imports += 20
            self.append(entry)
        # Add winedrop.dll entry
        self.append(
            struct.pack("<IIIII", 
                        rva_oft,                # OriginalFirstThunk
                        0,                      # Timestamp
                        0,                      # ForwarderChain
                        rva_winedrop_dll,       # Name
                        rva_ft))                # FirstThunk
        # Add import table delimiter entry
        self.append("\x00"*20)
        # End of import pseudo-section
        self.align(0x200)
        # Fix data directory and finish!
        self.pe.OPTIONAL_HEADER.DATA_DIRECTORY[1].VirtualAddress = rva_imports
        self.pe.OPTIONAL_HEADER.DATA_DIRECTORY[1].Size += 20
        # Return IAT entries for each imported routine
        return rva_iat
    
    def add_trampolines(self, iat):
        """
        Assume that we're hooking function with signature "int __stdcall fn(a,b,c)".
        After CALL to trampoline, stack looks like:
            fn_ptr
            callee_ptr
            a
            b
            c
        We will swap last two elements:
            callee_ptr
            fn_ptr
            a
            b
            c
        So now we're effectively calling "int __stdcall hook_fn(orig_ptr, a, b, c)" with callee_ptr as return address.
        """
        tramp_code = ''.join([
            "\x58",             # pop eax
            "\x87\x04\x24",     # xchg [esp], eax
            "\x50",             # push eax
            "\xe9"              # jmp ...
        ])
        tramp_size = len(tramp_code)+4
        tramp_rva = []
        for va in iat:
            tramp_rva.append(self.append(tramp_code+p32((va-(self.next_rva()+tramp_size)))))
            self.align(16, '\xcc')
        self.align(0x200)
        return tramp_rva

    def hook_patch(self, patch_va, tramp_va):
        patch_offs = self.pe.get_offset_from_rva(patch_va)
        # Is it "hookable" function prologue?
        assert self.pe.__data__[patch_offs-5:patch_offs+2] == "\x90\x90\x90\x90\x90\x8B\xFF"
        # Apply hook patch (jmp backwards, call to tramp_va)
        data = bytearray(self.pe.__data__)
        data[patch_offs-5:patch_offs+2] = "\xe8{}\xeb\xf9".format(p32(tramp_va - patch_va))
        self.pe.__data__ = str(data)

    def write(self, fname):
        self.pe.write(fname)
