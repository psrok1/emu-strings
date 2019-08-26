import os
import struct

from pefile import PE
from yaml import load
from capstone import Cs, CS_ARCH_X86, CS_MODE_32

from pdblib.dl_syms import download_pdb_by_pe
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
            iat_va = self.append(p32(r))
            print("IAT winedrop.dll@{} => {}+0x{:x}".format(r, self.libpath, iat_va))
            rva_iat.append(iat_va)
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
        # Fix SizeOfImage
        size_of_image = self.last_section.VirtualAddress + self.last_section.SizeOfRawData
        self.pe.OPTIONAL_HEADER.SizeOfImage = size_of_image + (4096 - size_of_image % 4096)
        # Return IAT entries for each imported routine
        return {routines[idx]: r_iat for idx, r_iat in enumerate(rva_iat)}

    def hook_hotpatchable_prologue(self, patch_va, hook_iat_va):
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
            fn_ptr+2
            a
            b
            c
        So now we're effectively calling "int __stdcall hook_fn(orig_ptr, a, b, c)" with callee_ptr as return address.
        """
        tramp_code = [
            "\x58"  # pop eax
            "\x83\xc0\x02"  # add eax, 2
            "\x87\x04\x24"  # xchg [esp], eax
            "\x50"  # push eax
            "\xe8\x00\x00\x00\x00"  # call $+5
            ,
            "\x58"  # pop eax
            "\xff\xa0"  # jmp [eax+<rip_rel_iat>]
        ]
        patch_offs = self.pe.get_offset_from_rva(patch_va)
        # Is it "hookable" function prologue?
        assert self.pe.__data__[patch_offs-5:patch_offs+2] == "\x90\x90\x90\x90\x90\x8B\xFF"
        rip_rel_iat = hook_iat_va - (self.next_rva() + len(tramp_code[0]))
        tramp_va = self.append(tramp_code[0] + tramp_code[1] + p32(rip_rel_iat))
        self.align(16, '\xcc')
        # Apply hook patch (jmp backwards, call to tramp_va)
        self.pe.set_bytes_at_offset(patch_offs - 5, "\xe8{}\xeb\xf9".format(p32(tramp_va - patch_va)))
        return tramp_va

    def hook_inline(self, patch_va, hook_iat_va, expected=None):
        """
        Hooking middle of function
        """
        tramp_code = [
            "\x9c" # pushf
            "\x60" # pusha
            "\xe8\x00\x00\x00\x00"  # call $+5
            ,
            "\x58" # pop eax
            "\xff\x90" # call [eax+<rip_rel_iat>]
            ,
            "\x61" # popa
            "\x9d" # popf
            ,
            "\xc3" # ret
        ]
        patch_offs = self.pe.get_offset_from_rva(patch_va)
        # Is it "hookable" function prologue?
        if expected is not None:
            expected = expected.decode("hex")
            if self.pe.__data__[patch_offs:patch_offs + len(expected)] != expected:
                raise AssertionError("Expected {}, found {}".format(
                    expected.encode("hex"),
                    self.pe.__data__[patch_offs:patch_offs + len(expected)].encode("hex")))

        rip_rel_iat = hook_iat_va - (self.next_rva() + len(tramp_code[0]))
        tramp_va = self.append(tramp_code[0] + tramp_code[1] + p32(rip_rel_iat))
        self.append(tramp_code[2])

        patched_code_size = 0
        for _, instr_size, _, _ in Cs(CS_ARCH_X86, CS_MODE_32).disasm_lite(
                self.pe.__data__[patch_offs:patch_offs + 16], 16):
            patched_code_size += instr_size
            if patched_code_size >= 5:
                break

        patched_code = self.pe.__data__[patch_offs:patch_offs + patched_code_size]
        self.pe.set_bytes_at_offset(patch_offs, ("\xe8" + p32(tramp_va - patch_va - 5)).ljust(patched_code_size, '\x90'))
        self.append(patched_code)
        self.append(tramp_code[3])
        self.align(16, '\xcc')
        return tramp_va

    def write(self, fname):
        self.align(0x200)
        self.pe.write(fname)

if __name__ == "__main__":
    for libname, libroutines in load(open("monitor.yml")).iteritems():
        pdbpath = os.path.splitext(libname)[0]+".pdb"
        libpath = os.path.join(os.getenv("WINESYSTEM32", './'), libname)
        if not os.path.isfile(pdbpath):
            download_pdb_by_pe(os.path.join(os.getenv("WINESYSTEM32", './'), libname))
        syms = {sym[0]: sym[1] for sym in read_symbols(pdbpath)}

        libwsh = WSHInstrumentation(libpath)

        monroutines = list(set(
            hookdef if isinstance(hookdef, str) else hookdef["hook"]
            for routine, hookdef in libroutines.iteritems()))
        iatroutines = libwsh.rebuild_imports(monroutines)

        for routine, hookdef in libroutines.iteritems():
            if isinstance(hookdef, str):
                print("{} ({libname}+0x{:x}) => winedrop.dll@{} ({libname}+0x{:x})".format(
                    routine,
                    syms[routine],
                    hookdef,
                    libwsh.hook_hotpatchable_prologue(syms[routine], iatroutines[hookdef]),
                    libname=libname
                ))
            else:
                hook_routine = hookdef["hook"]
                hook_offset = hookdef["offset"]
                hook_expected = hookdef.get("expected")
                print("{}+{:x} ({libname}+0x{:x}) => winedrop.dll@{} ({libname}+0x{:x})".format(
                    routine,
                    hook_offset,
                    syms[routine] + hook_offset,
                    hook_routine,
                    libwsh.hook_inline(syms[routine] + hook_offset, iatroutines[hook_routine], expected=hook_expected),
                    libname=libname
                ))
        libwsh.write(libpath)
        print "[+] Applied patches on {}".format(libpath)
