#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>


void instr_reqs() {
    char *ptr;
    ptr = getenv("A");
    waitpid(1);
}


#define BLOCK() do { \
    k++; \
    if (n == k) { \
        a = b; \
        b = c; \
        c = d; \
        d = k; \
        printf("ok, n == %d\n", k); \
    } \
} while(0)

void lol(int n) {
    int k = 0;
    int a,b,c,d;
    a = b = c = d = 0;
    BLOCK();
    BLOCK();
    BLOCK();
    BLOCK();
    BLOCK();
    BLOCK();
    BLOCK();
    BLOCK();
    BLOCK();
    BLOCK();
    BLOCK();
    BLOCK();
    BLOCK();
    BLOCK();
    BLOCK();
    BLOCK();
    BLOCK();
    BLOCK();
    BLOCK();
    BLOCK();
    BLOCK();
    BLOCK();
    BLOCK();
    BLOCK();
    BLOCK();
    BLOCK();
    BLOCK();
    BLOCK();
    BLOCK();
    BLOCK();
    BLOCK();
    BLOCK();
    BLOCK();
    BLOCK();
    BLOCK();
    BLOCK();
    BLOCK();
    BLOCK();
    BLOCK();
    BLOCK();
    BLOCK();
    BLOCK();
    BLOCK();
    BLOCK();
    BLOCK();
    BLOCK();
    BLOCK();
    BLOCK();
    BLOCK();
    BLOCK();
    BLOCK();
    BLOCK();
    BLOCK();
    BLOCK();
    BLOCK();
    BLOCK();
    BLOCK();
    BLOCK();
    BLOCK();
    BLOCK();
    BLOCK();
    BLOCK();
    BLOCK();
    BLOCK();
    BLOCK();
    BLOCK();
    BLOCK();
    BLOCK();
    BLOCK();
    BLOCK();
    BLOCK();
    BLOCK();
    BLOCK();
    BLOCK();
    BLOCK();
    BLOCK();
    BLOCK();
    BLOCK();
    BLOCK();
    BLOCK();
    BLOCK();
    BLOCK();
    BLOCK();
    BLOCK();
    BLOCK();
    BLOCK();
    BLOCK();
    BLOCK();
    BLOCK();
    BLOCK();
    BLOCK();
    BLOCK();
    BLOCK();
    BLOCK();
    BLOCK();
    BLOCK();
    BLOCK();
    BLOCK();
    BLOCK();
    BLOCK();
    BLOCK();
    BLOCK();
    BLOCK();
    BLOCK();
    BLOCK();
    BLOCK();
    BLOCK();
    BLOCK();
}

void fizzbuzz() {
    for (int i = 0; i < 1000; i++) {
        int did_print = 0;
        if (i % 5 == 0) {
            printf("Fizz");
            did_print = 1;
        }
        if (i % 3 == 0) {
            printf("Buzz");
            did_print = 1;
        }
        if (!did_print) {
            printf("%d", i);
        }
        printf("\n");
    }
}

void hexprint(char c) {
    printf("%02x", c);
}

void hexenc(char *buf, size_t len) {
    for (int i = 0; i < len; i++) {
        if (strncmp(buf+i, "AAAA", 4) == 0) {
            printf("Are you trying to hack me!?!?!\n");
        }
        hexprint(buf[i]);
    }
    printf("\n");
}

int main() {
    fizzbuzz();
    lol(24);
    printf("Hi and welcome to the tester\n");
    char buf[100];
    if (read(0, buf, sizeof(buf)) < sizeof(buf)) {
        printf(">_> ENTER THE RIGHT AMOUNT.\n");
        exit(1);
    }
    hexenc(buf, sizeof(buf));
}
