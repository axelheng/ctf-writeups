# CTF Writeups

Collection of Fun and Interesting Challenges! I have learnt quite alotfrom these

## Challenges

### CourseRekt

CourseRekt uses colliding username IDs and has a race condition in its workload validation. Six concurrent users can share one account directory and bypass the 23-MC limit.

- [Challenge files and writeup](dist-courserekt/)

### n00bcak's Last Straw

This challenge uses a buffer overflow to corrupt a linked-list pointer and trigger the registered `SIGSEGV` handler.

- [Challenge files and writeup](n00bcaks-last-straw/)

### GreyLogin

GreyLogin stores the complete login form in the session, allowing an attacker to add `role=admin` and access the administrator dashboard.

- [Live challenge](http://challs.nusgreyhats.org:36171)
- [Challenge files and writeup](NUS-Greyhats-CTF/dist-greylogin/)
