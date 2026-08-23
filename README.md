# CTF Writeups

Collection of challenge files and writeups.

## Challenges

### CourseRekt

CourseRekt uses colliding username IDs and has a race condition in its workload validation. Six concurrent users can share one account directory and bypass the 23-MC limit.

- [Challenge files and writeup](dist-courserekt/)

### n00bcak's Last Straw

This challenge uses a buffer overflow to corrupt a linked-list pointer and trigger the registered `SIGSEGV` handler.

- [Challenge files and writeup](n00bcaks-last-straw/)
