__afl_maybe_log:
    lahf
    seto al

    mov rdx, qword ptr [rip + __afl_area_ptr]
    test rdx, rdx
    je __afl_setup

__afl_store:
    xor rcx, qword ptr [rip + __afl_prev_loc]
    xor qword ptr [rip + __afl_prev_loc], rcx
    shr qword ptr [rip + __afl_prev_loc], 1

    inc byte ptr [rdx + rcx]

__afl_return:
    add al, 127
    sahf
    ret

__afl_setup:
    cmp byte ptr [rip + __afl_setup_failure], 0
    jne __afl_return

    lea rdx, qword ptr [rip + __afl_global_area_ptr]
    mov rdx, qword ptr [rdx]
    test rdx, rdx
    je __afl_setup_first

    mov qword ptr [rip + __afl_area_ptr], rdx
    jmp __afl_store

__afl_setup_first:
    lea rsp, qword ptr [rsp - 352]

    mov qword ptr [rsp], rax
    mov qword ptr [rsp+8], rcx
    mov qword ptr [rsp+16], rdi
    mov qword ptr [rsp+32], rsi
    mov qword ptr [rsp+40], r8
    mov qword ptr [rsp+48], r9
    mov qword ptr [rsp+56], r10
    mov qword ptr [rsp+64], r11

    movq qword ptr [rsp+96], xmm0
    movq qword ptr [rsp+112], xmm1
    movq qword ptr [rsp+128], xmm2
    movq qword ptr [rsp+144], xmm3
    movq qword ptr [rsp+160], xmm4
    movq qword ptr [rsp+176], xmm5
    movq qword ptr [rsp+192], xmm6
    movq qword ptr [rsp+208], xmm7
    movq qword ptr [rsp+224], xmm8
    movq qword ptr [rsp+240], xmm9
    movq qword ptr [rsp+256], xmm10
    movq qword ptr [rsp+272], xmm11
    movq qword ptr [rsp+288], xmm12
    movq qword ptr [rsp+304], xmm13
    movq qword ptr [rsp+320], xmm14
    movq qword ptr [rsp+336], xmm15

    
    push r12
    mov r12, rsp
    sub rsp, 16
    and rsp, 0xfffffffffffffff0

    lea rdi, qword ptr [rip + AFL_SHM_ENV]
    call {getenv}
    test rax, rax
    je __afl_setup_abort

    mov rdi, rax
    call {atoi}

    xor rdx, rdx # shmat flags
    xor rsi, rsi # requested addr
    mov rdi, rax # SHM ID
    call {shmat}

    cmp rax, -1
    je __afl_setup_abort

    mov rdx, rax
    mov qword ptr [rip + __afl_area_ptr], rax
    lea rdx, qword ptr [rip + __afl_global_area_ptr]
    mov qword ptr [rdx], rax
    mov rdx, rax

__afl_forkserver:
    # forkserver mode!

    push rdx
    push rdx

    mov rdx, 4 # length
    lea rsi, qword ptr [rip + __afl_temp] # data
    mov rdi, {FORKSRV_FD_1} # file desc
    call {write}

    cmp rax, 4
    jne __afl_fork_resume

__afl_fork_wait_loop:
    mov rdx, 4 # length
    lea rsi, qword ptr [rip + __afl_temp] # data
    mov rdi, {FORKSRV_FD} # file desc
    call {read}
    
    cmp rax, 4
    jne __afl_die

    call {fork}
    cmp rax, 0
    jl __afl_die
    je __afl_fork_resume

    mov dword ptr [rip + __afl_fork_pid], eax

    mov rdx, 4 # length
    lea rsi, dword ptr [rip + __afl_fork_pid] # data
    mov rdi, {FORKSRV_FD_1}
    call {write}

    mov rdx, 0 # no flags
    lea rsi, dword ptr [rip + __afl_temp] # status
    mov rdi, qword ptr [rip + __afl_fork_pid] # PID
    call {waitpid}

    cmp rax, 0
    jle __afl_die

    mov rdx, 4 # length
    lea rsi, dword ptr [rip + __afl_temp] # data
    mov rdi, {FORKSRV_FD_1} # file desc
    call {write}

    jmp __afl_fork_wait_loop

__afl_fork_resume:
    mov rdi, {FORKSRV_FD}
    call {close}
    mov rdi, {FORKSRV_FD_1}
    call {close}

    pop rdx
    pop rdx

    mov rsp, r12
    pop r12

    mov rax, qword ptr [rsp]
    mov rcx, qword ptr [rsp+8]
    mov rdi, qword ptr [rsp+16]
    mov rsi, qword ptr [rsp+32]
    mov r8, qword ptr [rsp+40]
    mov r9, qword ptr [rsp+48]
    mov r10, qword ptr [rsp+56]
    mov r11, qword ptr [rsp+64]

    movq xmm0, qword ptr [rsp+96]
    movq xmm1, qword ptr [rsp+112]
    movq xmm2, qword ptr [rsp+128]
    movq xmm3, qword ptr [rsp+144]
    movq xmm4, qword ptr [rsp+160]
    movq xmm5, qword ptr [rsp+176]
    movq xmm6, qword ptr [rsp+192]
    movq xmm7, qword ptr [rsp+208]
    movq xmm8, qword ptr [rsp+224]
    movq xmm9, qword ptr [rsp+240]
    movq xmm10, qword ptr [rsp+256]
    movq xmm11, qword ptr [rsp+272]
    movq xmm12, qword ptr [rsp+288]
    movq xmm13, qword ptr [rsp+304]
    movq xmm14, qword ptr [rsp+320]
    movq xmm15, qword ptr [rsp+336]

    lea rsp, qword ptr [rsp + 352]

    jmp __afl_store

__afl_die:
    xor rax, rax
    call {exit}

__afl_setup_abort:
    inc byte ptr [rip + __afl_setup_failure]

    mov rsp, r12
    pop r12

    mov rax, qword ptr [rsp]
    mov rcx, qword ptr [rsp+8]
    mov rdi, qword ptr [rsp+16]
    mov rsi, qword ptr [rsp+32]
    mov r8, qword ptr [rsp+40]
    mov r9, qword ptr [rsp+48]
    mov r10, qword ptr [rsp+56]
    mov r11, qword ptr [rsp+64]

    movq xmm0, qword ptr [rsp+96]
    movq xmm1, qword ptr [rsp+112]
    movq xmm2, qword ptr [rsp+128]
    movq xmm3, qword ptr [rsp+144]
    movq xmm4, qword ptr [rsp+160]
    movq xmm5, qword ptr [rsp+176]
    movq xmm6, qword ptr [rsp+192]
    movq xmm7, qword ptr [rsp+208]
    movq xmm8, qword ptr [rsp+224]
    movq xmm9, qword ptr [rsp+240]
    movq xmm10, qword ptr [rsp+256]
    movq xmm11, qword ptr [rsp+272]
    movq xmm12, qword ptr [rsp+288]
    movq xmm13, qword ptr [rsp+304]
    movq xmm14, qword ptr [rsp+320]
    movq xmm15, qword ptr [rsp+336]

    lea rsp, qword ptr [rsp + 352]
    jmp __afl_return
    
__afl_area_ptr:
.quad 0x0
__afl_prev_loc:
.quad 0x0
__afl_setup_failure:
.quad 0x0
__afl_global_area_ptr:
.quad 0x0
__afl_fork_pid:
.long 0x0
__afl_temp:
.long 0x0

AFL_SHM_ENV:
.string "__AFL_SHM_ID"
