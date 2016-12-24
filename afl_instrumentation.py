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
INSTR_GETENV = """
ret
"""
INSTR_ATOI = """
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
        }
