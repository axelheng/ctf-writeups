// gcc ./chall.c -o chall
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <signal.h>
#include <unistd.h>
#include <fcntl.h>

#define MAX_STRAWS 0x10
#define DATA_SIZE 0x40

void setup() {
    setbuf(stdin, 0);
	setbuf(stdout, 0);
}

struct straw {
    struct straw* next_ptr;
    char data[DATA_SIZE];
};

int num_straws = 1;
struct straw* init_straw;

// can you find a way to trigger this function?
void win(int sig) {
    int flag_fd = open("flag.txt", O_RDONLY);
    if (flag_fd == -1) {
        printf("Error reading flag.");
        exit(1);
    }
    char buf[0x30];
    read(flag_fd, buf, 0x30);
    write(1, buf, 0x30);
    exit(1);
}

void print_menu() {
    printf("=====================\n");
    printf("n00bcak's straw store\n");
    printf("How many straws would n00bcak store if n00bcak could store straws?\n");
    printf("=====================\n");
    printf("1. Create straw\n");
    printf("2. Edit straw\n");
    printf("3. Read straw\n");
    printf("> ");
}

void create_straw() {
    if (num_straws == MAX_STRAWS) {
        printf("[X] Too many straws! n00bcak can't store this many straws :(\n");
        return;
    }
    num_straws++;
    struct straw* last_straw = init_straw;
    while (last_straw->next_ptr != NULL) {
        last_straw = last_straw->next_ptr;
    }
    struct straw* new_straw = malloc(sizeof(struct straw));
    last_straw->next_ptr = new_straw;
    new_straw->next_ptr = NULL;
    strcpy(new_straw->data, "n00bcak's new straw");
    printf("[+] New straw created!\n");
}

void edit_straw(int straw_id) {
    struct straw* cur_straw = init_straw;
    for (int i = 0; i < straw_id; i++) {
        cur_straw = cur_straw->next_ptr;
    }
    printf("Enter new straw data: ");
    scanf("%72s", cur_straw->data);
    printf("[+] Straw edited!\n");
}

void read_straw(int straw_id) {
    struct straw* cur_straw = init_straw;
    for (int i = 0; i < straw_id; i++) {
        cur_straw = cur_straw->next_ptr;
    }
    printf("[+] Straw data: \n");
    write(1, cur_straw->data, 0x40);
}

int main() {
    setup();
    signal(SIGSEGV, win);
    init_straw = malloc(sizeof(struct straw));
    init_straw->next_ptr = NULL;
    strcpy(init_straw->data, "n00bcak's first straw");
    while (1) {
        print_menu();
        int choice;
        scanf("%i", &choice);
        if (choice < 1 || choice > 3) {
            printf("[X] Invalid option!\n");
            continue;
        }
        if (choice == 1) {
            create_straw();
            continue;
        }
        int straw_id;
        printf("Enter straw id: ");
        scanf("%i", &straw_id);
        if (straw_id >= num_straws || straw_id < 0) {
            printf("[X] Invalid straw id!\n");
            continue;
        }
        if (choice == 2) {
            edit_straw(straw_id);
        } else {
            read_straw(straw_id);
        }
    }
    return 0;
}
