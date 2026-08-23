#!/usr/bin/env python3

import zlib
import fcntl
import os

USER_FILE = "./data/users.txt"

USERNAME = None

MAX_WORKLOAD = 23

MCS_REQUIRED = 160
MCS_TAKEN = 136

MODULE_WORKLOAD = {
    "CS1231": 4,
    "CS2030": 4,
    "CS2040": 4,
    "CS2100": 4,
    "CS2102": 4,
    "CS2103": 4,
    "CS2220": 4,
    "CS2251": 4,
    "CS3103": 4,
    "CS3210": 4,
    "CS3211": 4,
    "CS3213": 4,
    "CS6767": 6.7,
    "CS3219": 4,
    "CS3223": 4,
    "CS3227": 4,
    "CS3230": 4,
    "CS3231": 4,
    "CS3233": 4,
    "CS3235": 4,
}

FLAG = None

def init():
    global FLAG
    os.makedirs("./data", exist_ok=True)
    open(USER_FILE, "a").close()
    with open("./flag.txt", "r") as f:
        FLAG = f.read()
    assert FLAG, "Flag is empty"


def user_id():
    return sum(ord(char) for char in USERNAME)

def init_user():
    uid = user_id()
    os.makedirs(f"./data/{uid}", exist_ok=True)
    with open(f"./data/{uid}/WORKLOAD.txt", "w") as f:
        f.write("0")
    with open(f"./data/{uid}/MODS.txt", "w") as f:
        pass

def add_mod(mod_code):
    uid = user_id()
    workload = 0
    with open(f"./data/{uid}/WORKLOAD.txt", "r") as f:
        workload = float(f.read() or "0")
    if mod_code not in MODULE_WORKLOAD:
        print("Invalid module code!", flush=True)
        return False
    if workload + MODULE_WORKLOAD[mod_code] > MAX_WORKLOAD:
        print("Workload exceeded!", flush=True)
        return False
    with open(f"./data/{uid}/MODS.txt", "r+") as f:
        fcntl.lockf(f, fcntl.LOCK_EX)
        mods = f.read().splitlines()
        if mod_code in mods:
            print("You already selected this mod!", flush=True)
            return False
        f.write(f"{mod_code}\n")
    with open(f"./data/{uid}/WORKLOAD.txt", "w") as f:
        f.write(str(workload + MODULE_WORKLOAD[mod_code]))
    print("Module added!", flush=True)
    return True


def print_workload():
    workload = 0
    uid = user_id()
    print("Your modules:", flush=True)
    with open(f"./data/{uid}/MODS.txt", "r") as f:
        for idx, mod in enumerate(f.read().splitlines()):
            workload += MODULE_WORKLOAD[mod]
            print(f"{idx+1}. {mod}: {MODULE_WORKLOAD[mod]}MCs", flush=True)
        print("Total:", workload, "MCs", flush=True)
    return workload

def main() -> None:
    global USERNAME
    print("Welcome to CourseRekt!\n", flush=True)
    USERNAME = input("Please enter your username: ")
    success = True
    with open(USER_FILE, "r+") as f:
        fcntl.lockf(f, fcntl.LOCK_EX)
        users = f.read().splitlines()
        if USERNAME in users:
            print("Username is already taken, choose another one!", flush=True)
            success = False
        else:
            print(f"Welcome, {USERNAME}!", flush=True)
            f.write(f"{USERNAME}\n")

    if not success:
        exit(-1)

    init_user()

    while True:
        print("What do you want to do?\n1. Add module\n2. View classes\n3. Apply for graduation\nYour choice: ", flush=True)
        choice = int(input())
        if choice == 1:
            mod_code = input("Enter module code: ")
            if not add_mod(mod_code):
                exit(-1)
        elif choice == 2:
            print_workload()
        elif choice == 3:
            workload = print_workload()
            if workload + MCS_TAKEN >= MCS_REQUIRED:
                print(f"Congratulations on your graduation! Here's the flag: {FLAG}", flush=True)
            else:
                print("Not enough MCs!", flush=True)
                exit(-1)
        else:
            exit(0)



if __name__ == "__main__":
    init()
    main()
