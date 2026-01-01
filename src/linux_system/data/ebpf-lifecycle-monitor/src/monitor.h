#ifndef __MONITOR_H
#define __MONITOR_H

#define TASK_COMM_LEN 16

enum event_type {
    EVENT_PROCESS_EXEC,
    EVENT_PROCESS_EXIT,
    EVENT_OOM_KILL,
};

struct event {
    unsigned long long timestamp;
    int pid;
    int ppid;
    int exit_code;
    enum event_type type;
    char comm[TASK_COMM_LEN];
    char target_comm[TASK_COMM_LEN]; // For OOM
    int target_pid;                  // For OOM
};

#endif
