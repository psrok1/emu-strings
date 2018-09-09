	.text
	.intel_syntax noprefix
	.file	"monitor.c"
                                        # Start of file scope inline assembly
	.globl	HookSleep
HookSleep:
	pop	eax
	xchg	dword ptr [esp], eax
	push	eax


                                        # End of file scope inline assembly
	.globl	WinMain                 # -- Begin function WinMain
	.p2align	4, 0x90
	.type	WinMain,@function
WinMain:                                # @WinMain
# %bb.0:
	push	ebp
	mov	ebp, esp
	push	eax
	mov	eax, dword ptr [ebp - 4]
	add	esp, 4
	pop	ebp
	ret
.Lfunc_end0:
	.size	WinMain, .Lfunc_end0-WinMain
                                        # -- End function

	.ident	"clang version 6.0.0-1ubuntu2 (tags/RELEASE_600/final)"
	.section	".note.GNU-stack","",@progbits
