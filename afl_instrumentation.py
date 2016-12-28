#TODO: AT&T -> Intel on all asm snippets

# this is what we actually want to hook with
# note that the random value for the BB must be inserted
AFL_TRAMPOLINE = """
  lea rsp, qword ptr [rsp-0x98]
  mov qword ptr [rsp], rdx
  mov qword ptr [rsp+8], rcx
  mov qword ptr [rsp+16], rax
  mov rcx, {hook_id}
  call {__afl_maybe_log}
  mov rax, qword ptr [rsp+16]
  mov rcx, qword ptr [rsp+8]
  mov rdx, qword ptr [rsp]
  lea rsp, qword ptr [rsp+0x98]
  ret
"""

# main payload
with open('afl_maybe_log.s') as f:
    AFL_MAIN_INSTRUMENTATION = f.read()



# functions required for instrumenting

# these ones are easy, just syscall wrappers
INSTR_SHMAT = """
mov rax, 30
syscall
ret
"""
INSTR_WRITE = """
mov rax, 1
syscall
ret
"""
INSTR_READ = """
mov rax, 0
syscall
ret
"""
INSTR_FORK = """
mov rax, 57
syscall
ret
"""
INSTR_CLOSE = """
mov rax, 3
syscall
ret
"""
INSTR_EXIT = """
mov rax, 60
syscall
ret
"""

# these are less easy...

# Trivial implementation plucked out of GCC:
# int atoi(char *s) {
#   int acc = 0;
#   while (*s) {
#       acc *= 10;
#       acc += *s - '0';
#       s++;
#   }
# }
INSTR_ATOI = """
    push   rbp
    mov    rbp,rsp
    mov    qword ptr [rbp-0x18],rdi
    mov    dword ptr [rbp-0x4],0x0
    jmp    atoi_end
atoi_loop:
    mov    edx,dword ptr [rbp-0x4]
    mov    eax,edx
    shl    eax,0x2
    add    eax,edx
    add    eax,eax
    mov    dword ptr [rbp-0x4],eax
    mov    rax,qword ptr [rbp-0x18]
    movzx  eax,byte ptr [rax]
    movsx  eax,al
    sub    eax,0x30
    add    dword ptr [rbp-0x4],eax
    add    qword ptr [rbp-0x18],0x1
atoi_end:
    mov    rax,qword ptr [rbp-0x18]
    movzx  eax,byte ptr [rax]
    test   al,al
    jne    atoi_loop
    mov    eax,dword ptr [rbp-0x4]
    pop    rbp
    ret
"""

INSTR_GETENV = """
ret
"""
INSTR_WAITPID = """
ret
"""

# export a dictionary
INSTR_FUNCTIONS = {
        'shmat': INSTR_SHMAT,
        'write': INSTR_WRITE,
        'read': INSTR_READ,
        'fork': INSTR_FORK,
        'close': INSTR_CLOSE,
        'exit': INSTR_EXIT,
        'atoi': INSTR_ATOI,
        }
