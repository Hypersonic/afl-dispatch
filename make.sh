#!/bin/sh

#gcc -fno-stack-protector vuln.c -o vuln
gcc -fno-stack-protector -std=c99 test.c -o test

python patch.py 'test' 'test-ins'
chmod +x 'test-ins'
