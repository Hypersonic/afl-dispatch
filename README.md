AFL-Dispatch
------------

AFL Instrumentation on binaries via binary patching!


Requires [Dispatch](https://github.com/isislab/dispatch) to work.

Once you have that it _should_ be a simple matter of:

`python patch.py <input_binary> <output_binary>`


However, there are a few major caveats right now:

1. We need a handful of libc functions for AFL's instrumentation to work. Right now, we patch in a handful of them, but a few are more complicated and need to be implemented. They are:
    - `getenv`

2. This only works on x86\_64 Linux ELFs right now, but the switch to other platforms and architectures is mostly a matter of having instrumentation available for the platforms. 

