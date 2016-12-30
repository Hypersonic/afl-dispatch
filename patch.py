from random import randint
from sys import argv

from dispatch import *
from dispatch.constructs import Function

from afl_instrumentation import AFL_TRAMPOLINE, AFL_MAIN_INSTRUMENTATION, INSTR_FUNCTIONS


"""
VERY, VERY PoC SCRIPT TO PATCH IN AFL SUPPORT TO x64 LINUX BINARIES

PROBABLY DONT USE THIS FOR ANYTHING SERIOUS.

Currently broken:
    - We can't reasonably add entries to the got.plt, and AFL requires the following functions:
        getenv, atoi, waitpid, shmat, write, read, fork, close, _exit

        We can (and do) inject these:
            shmat, write, read, fork, close, _exit, atoi, waitpid

        We still need to implement:
            getenv

    - grsec/PaX systems can't run because of W^X, and we inject data into the same page as code. This can probably be fixed, but you should have control of the systems you're fuzzing on, so it's not a huge issue right now.


    - We can't safely instrument leaf functions in general, because the optimizer can choose to not actually expand a stack frame, and when we turn it into a non-leaf during instrumentation that breaks code.

    - We can't instrument quite as many BBs as regular AFL can, because we're limited by safety constraints (is this block safe to instrument, are these instructions safe to move elsewhere), so we can lose a fair amount of coverage info.
        I think this can be pushed back a bunch to the point where we get good coverage, but the PoC doesn't really attempt to push that bound, in favor of safety & simplicity.
        The biggest impact on this is BBs with lots of small instructions and stack-examining instructions... Perhaps some basic rewriting could let us instrument them safely...

        So far, however, it looks like we instrument enough to generate good coverage. That's good!
"""


def banner(s):
    dshs = '-'*(len(s) + 2)
    print '+' + dshs + '+'
    print '| ' + s + ' |'
    print '+' + dshs + '+'


def has_all_required_fns(ex):
    """
    Check that we have all the required functions.
    Returns (has_all, missing)
    """
    functions = {x.name.split('@')[0] for a,x in ex.functions.iteritems()}
    has_fn = lambda name: name in functions
    needed_fns = ['getenv', 'atoi', 'shmat', 'write', 'read', 'fork', 'waitpid', 'close', 'exit']
    return all(has_fn(x) for x in needed_fns), [x for x in needed_fns if not has_fn(x)]


def is_patchable_fn(fn):
    """
    Is this even a function we can patch?
    Some functions (GOT entries, for instance) aren't worthwhile to patch.
    """
    return fn.type == Function.NORMAL_FUNC # just ignore extern functions


def find_patch_addr(bb):
    """
    Find a vaddr in `BasicBlock` bb that we feel comfortable starting a patch at

    Return (start_address, size)

    Throws ValueError if no suitable vaddr could be found
    """
    MIN_PATCH_SIZE = 5 # sizeof(call 0xdeadbeef) on x64
    curr_patch_start = None
    curr_patch_size = 0


    def is_usable_for_patching(ins):
        """
        Tell us if an `Instruction` is movable during a patch
        """
        return not ins.references_ip() and \
               not ins.references_sp() and \
               not ins.is_jump() and \
               not ins.is_call() and \
               not ins.references_seg_reg() # TODO: don't require checking the seg_reg, this is waiting on a Keystone assembly bug

    # we can't safely hook basic blocks that are a CFG leaf because
    # the optimizer may choose to not generate an actual stack frame for it.
    # Therefore, we skip any BB that contains no calls
    #
    # TODO: determine if the BB actually uses locals and if not we can still instrument
    has_calls = False
    for ins in bb.instructions:
        if ins.is_call():
            has_calls = True
    if not has_calls:
        raise ValueError('Cannot safely hook leaf BBs, skip this')


    for ins in bb.instructions:
        if is_usable_for_patching(ins):
            #print ins, 'is usable for patching'
            # if we don't have a patch start, start here!
            if curr_patch_start is None:
                curr_patch_start = ins.address
            curr_patch_size += ins.size
        else: # reset our patch
            curr_patch_start = None
            curr_patch_size = 0
        # Stop looking if we've found one
        if curr_patch_size >= MIN_PATCH_SIZE:
            break

    if curr_patch_start is None or curr_patch_size < MIN_PATCH_SIZE:
        raise ValueError('No viable hook location found in bb')
    return curr_patch_start, curr_patch_size


def add__afl_maybe_log(ex, functions):
    """
    Add the __afl_maybe_log function, the main function that the hook code calls into

    Returns the address of __afl_maybe_log
    """
    instr = AFL_MAIN_INSTRUMENTATION.format(
            getenv = functions['getenv'],
            atoi = functions['atoi'],
            shmat = functions['shmat'],
            write = functions['write'],
            read = functions['read'],
            fork = functions['fork'],
            waitpid = functions['waitpid'],
            close = functions['close'],
            exit = functions['exit'],

            FORKSRV_FD = 198,
            FORKSRV_FD_1 = 199,
            )
    ex.prepare_for_injection()
    asm = ex.assemble(instr, vaddr=ex.next_injection_vaddr)
    vaddr = ex.inject(asm)
    return vaddr

def add_missing_functions(ex, missing):
    """
    Add any missing functions named in the list `missing`.

    If we cannot find an injectable function from the missing list, we'll raise a ValueError

    Returns a dict of {fn_name: addr}
    """
    inserted_locs = {}
    for fn in missing:
        if fn in INSTR_FUNCTIONS:
            print 'Inserting {}'.format(fn)
            ex.prepare_for_injection()
            instr = INSTR_FUNCTIONS[fn]
            asm = ex.assemble(instr, vaddr=ex.next_injection_vaddr)
            vaddr = ex.inject(asm)
            inserted_locs[fn] = vaddr
        else:
            raise ValueError('No such available function: ' + fn)
    return inserted_locs


def main():
    if len(argv) != 3:
        print 'Usage: patch.py <input> <output>'
        return


    INPUT_FILE = argv[1]
    OUTPUT_FILE = argv[2]

    banner('LOADING FILE: ' + INPUT_FILE)

    ex = read_executable(INPUT_FILE)
    ex.analyze()
    ex.prepare_for_injection()

    functions = {x.name.split('@')[0]: x.address for x in ex.functions.itervalues()}

    print 'Loaded!'

    banner('CHECKING PREREQS')
    has_all, missing = has_all_required_fns(ex)
    inserted_reqs = None
    # insert our new reqs
    if not has_all:
        insertable = [fn for fn in missing if fn in INSTR_FUNCTIONS]
        inserted_reqs = add_missing_functions(ex, insertable)
        for fn, addr in inserted_reqs.iteritems():
            missing.remove(fn)
        has_all = not bool(missing)
        functions.update(inserted_reqs) # Add to our functions list
    if not has_all:
        print 'Missing the following functions:'
        for fn in missing:
            print fn
        code_to_insert = """
void instr_reqs() {
    char *ptr;
    int i;
    ptr = getenv("A");
}
        """
        print 'If you have access to the original source, adding the following function will allow us to work for now:'
        print code_to_insert
        return

    banner('INJECTION MAIN INSTRUMENTATION')
    __afl_maybe_log = add__afl_maybe_log(ex, functions)
    print 'Added __afl_maybe_log @ ', hex(__afl_maybe_log)

    banner('FINDING PATCHABLE BASIC BLOCKS')

    patchable_addrs = set()
    n_bbs, n_patchable = 0, 0
    for fn in ex.iter_functions():
        if not is_patchable_fn(fn):
            print 'Not patching', fn
            continue
        for bb in fn.bbs:
            n_bbs += 1
            try:
                patch_addr,size = find_patch_addr(bb)
                #print hex(patch_addr), size
                patchable_addrs.add(patch_addr)
                n_patchable += 1
            except ValueError: # no patch found
                pass
                #print 'No patch addr for bb at', hex(bb.address)

    print '{} / {} BBs are patchable'.format(n_patchable, n_bbs)

    banner('HOOKING BASIC BLOCKS')

    for i,addr in enumerate(patchable_addrs):
        #bb = ex.bb_containing_vaddr(addr)
        #ins = [x for x in bb.instructions if x.address == addr][0]
        print '({} / {}) Hooking {}'.format(i, n_patchable, hex(addr))
        hook_id = randint(0, 0xffff)
        ex.hook(addr, AFL_TRAMPOLINE.format(
            hook_id = hook_id,
            __afl_maybe_log = __afl_maybe_log,
            ))

    banner('GENERATING OUTPUT: ' + OUTPUT_FILE)
    ex.save(OUTPUT_FILE)


if __name__ == '__main__':
    main()
