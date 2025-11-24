練習參考答案
=====================================================

.. toctree::
      :hidden:
      :maxdepth: 4

課後練習
-------------------------------

編程題
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. `*` 分別編寫基於UNIX System V IPC的管道、共享內存、信號量和消息隊列的Linux應用程序，實現進程間的數據交換。

    管道

    .. code-block:: c
        :linenos:

        #include <unistd.h>
        #include <stdio.h>
        #include <stdlib.h>
        #include <string.h>
        
        int main(void) {
          int pipefd[2];
          // pipe syscall creates a pipe with two ends
          // pipefd[0] is the read end
          // pipefd[1] is the write end
          // ref: https://man7.org/linux/man-pages/man2/pipe.2.html
          if (pipe(pipefd) == -1) {
            perror("failed to create pipe");
            exit(EXIT_FAILURE);
          }
        
          int pid = fork();
          if (pid == -1) {
            perror("failed to fork");
            exit(EXIT_FAILURE);
          }
        
          if (pid == 0) {
            // child process reads from the pipe
            close(pipefd[1]); // close the write end
            // read a byte at a time
            char buf;
            while (read(pipefd[0], &buf, 1) > 0) {
              printf("%s", &buf);
            }
            close(pipefd[0]); // close the read end
          } else {
            // parent process writes to the pipe
            close(pipefd[0]); // close the read end
            // parent writes
            char* msg = "hello from pipe\n";
            write(pipefd[1], msg, strlen(msg)); // omitting error handling
            close(pipefd[1]); // close the write end
          }
        
          return EXIT_SUCCESS;
        }

    共享內存

    .. code-block:: c
        :linenos:

        #include <unistd.h>
        #include <stdio.h>
        #include <stdlib.h>
        #include <string.h>
        #include <sys/shm.h>
        
        int main(void) {
          // create a new anonymous shared memory segment of page size, with a permission of 0600
          // ref: https://man7.org/linux/man-pages/man2/shmget.2.html
          int shmid = shmget(IPC_PRIVATE, sysconf(_SC_PAGESIZE), IPC_CREAT | 0600);
          if (shmid == -1) {
            perror("failed to create shared memory");
            exit(EXIT_FAILURE);
          }
        
          int pid = fork();
          if (pid == -1) {
            perror("failed to fork");
            exit(EXIT_FAILURE);
          }
        
          if (pid == 0) {
            // attach the shared memory into child process's address space
            char* shm = shmat(shmid, NULL, 0);
            while (!shm[0]) {
              // wait until the parent signals that the data is ready
              // WARNING: this is not the correct way to synchronize processes
              // on SMP systems due to memory orders, but this implementation
              // is chosen here specifically for ease of understanding
            }
            printf("%s", shm + 1);
          } else {
            // attach the shared memory into parent process's address space
            char* shm = shmat(shmid, NULL, 0);
            // copy message into shared memory
            strcpy(shm + 1, "hello from shared memory\n");
            // signal that the data is ready
            shm[0] = 1;
          }
        
          return EXIT_SUCCESS;
        }

    信號量

    .. code-block:: c
        :linenos:

        #include <unistd.h>
        #include <stdio.h>
        #include <stdlib.h>
        #include <string.h>
        #include <sys/sem.h>
        
        int main(void) {
          // create a new anonymous semaphore set, with permission 0600
          // ref: https://man7.org/linux/man-pages/man2/semget.2.html
          int semid = semget(IPC_PRIVATE, 1, IPC_CREAT | 0600);
          if (semid == -1) {
            perror("failed to create semaphore");
            exit(EXIT_FAILURE);
          }
        
          struct sembuf sops[1];
          sops[0].sem_num = 0; // operate on semaphore 0
          sops[0].sem_op  = 1; // increase the semaphore's value by 1
          sops[0].sem_flg = 0;
          if (semop(semid, sops, 1) == -1) {
            perror("failed to increase semaphore");
            exit(EXIT_FAILURE);
          }
        
          int pid = fork();
          if (pid == -1) {
            perror("failed to fork");
            exit(EXIT_FAILURE);
          }
        
          if (pid == 0) {
            printf("hello from child, waiting for parent to release semaphore\n");
            struct sembuf sops[1];
            sops[0].sem_num = 0; // operate on semaphore 0
            sops[0].sem_op  = 0; // wait for the semaphore to become 0
            sops[0].sem_flg = 0;
            if (semop(semid, sops, 1) == -1) {
              perror("failed to wait on semaphore");
              exit(EXIT_FAILURE);
            }
            printf("hello from semaphore\n");
          } else {
            printf("hello from parent, waiting three seconds before release semaphore\n");
            // sleep for three second
            sleep(3);
            struct sembuf sops[1];
            sops[0].sem_num = 0; // operate on semaphore 0
            sops[0].sem_op  = -1; // decrease the semaphore's value by 1
            sops[0].sem_flg = 0;
            if (semop(semid, sops, 1) == -1) {
              perror("failed to decrease semaphore");
              exit(EXIT_FAILURE);
            }
          }
        
          return EXIT_SUCCESS;
        }

    消息隊列

    .. code-block:: c
        :linenos:

        #include <unistd.h>
        #include <stdio.h>
        #include <stdlib.h>
        #include <string.h>
        #include <sys/msg.h>
        
        struct msgbuf {
          long mtype;
          char mtext[1];
        };
        
        int main(void) {
          // create a new anonymous message queue, with a permission of 0600
          // ref: https://man7.org/linux/man-pages/man2/msgget.2.html
          int msgid = msgget(IPC_PRIVATE, IPC_CREAT | 0600);
          if (msgid == -1) {
            perror("failed to create message queue");
            exit(EXIT_FAILURE);
          }
        
          int pid = fork();
          if (pid == -1) {
            perror("failed to fork");
            exit(EXIT_FAILURE);
          }
        
          if (pid == 0) {
            // child process receives message
            struct msgbuf buf;
            while (msgrcv(msgid, &buf, sizeof(buf.mtext), 1, 0) != -1) {
              printf("%c", buf.mtext[0]);
            }
          } else {
            // parent process sends message
            char* msg = "hello from message queue\n";
            struct msgbuf buf;
            buf.mtype = 1;
            for (int i = 0; i < strlen(msg); i ++) {
              buf.mtext[0] = msg[i];
              msgsnd(msgid, &buf, sizeof(buf.mtext), 0);
            }
            struct msqid_ds info;
            while (msgctl(msgid, IPC_STAT, &info), info.msg_qnum > 0) {
              // wait for the message queue to be fully consumed
            }
            // close message queue
            msgctl(msgid, IPC_RMID, NULL);
          }
        
          return EXIT_SUCCESS;
        }

2. `**` 分別編寫基於UNIX的signal機制的Linux應用程序，實現進程間異步通知。

    .. code-block:: c
        :linenos:

        #include <unistd.h>
        #include <stdio.h>
        #include <stdlib.h>
        #include <signal.h>
        
        static void sighandler(int sig) {
          printf("received signal %d, exiting\n", sig);
          exit(EXIT_SUCCESS);
        }
        
        int main(void) {
          struct sigaction sa;
          sa.sa_handler = sighandler;
          sa.sa_flags = 0;
          sigemptyset(&sa.sa_mask);
          // register function sighandler as signal handler for SIGUSR1
          if (sigaction(SIGUSR1, &sa, NULL) != 0) {
            perror("failed to register signal handler");
            exit(EXIT_FAILURE);
          }
        
          int pid = fork();
          if (pid == -1) {
            perror("failed to fork");
            exit(EXIT_FAILURE);
          }
        
          if (pid == 0) {
            while (1) {
              // loop and wait for signal
            }
          } else {
            // send SIGUSR1 to child process
            kill(pid, SIGUSR1);
          }
        
          return EXIT_SUCCESS;
        }

3. `**` 參考rCore Tutorial 中的shell應用程序，在Linux環境下，編寫一個簡單的shell應用程序，通過管道相關的系統調用，能夠支持管道功能。

    .. code-block:: c
        :linenos:

        #include <stdio.h>
        #include <stdlib.h>
        #include <string.h>
        #include <sys/wait.h>
        #include <unistd.h>
        
        int parse(char* line, char** argv) {
          size_t len;
          // read a line from stdin
          if (getline(&line, &len, stdin) == -1)
            return -1;
          // remove trailing newline
          line[strlen(line) - 1] = '\0';
          // split line into tokens
          int i = 0;
          char* token = strtok(line, " ");
          while (token != NULL) {
            argv[i] = token;
            token = strtok(NULL, " ");
            i++;
          }
          return 0;
        }
        
        int concat(char** argv1, char** argv2) {
            // create pipe
            int pipefd[2];
            if (pipe(pipefd) == -1)
              return -1;
        
            // run the first command
            int pid1 = fork();
            if (pid1 == -1)
              return -1;
            if (pid1 == 0) {
              dup2(pipefd[1], STDOUT_FILENO);
              close(pipefd[0]);
              close(pipefd[1]);
              execvp(argv1[0], argv1);
            }
        
            // run the second command
            int pid2 = fork();
            if (pid2 == -1)
              return -1;
            if (pid2 == 0) {
              dup2(pipefd[0], STDIN_FILENO);
              close(pipefd[0]);
              close(pipefd[1]);
              execvp(argv2[0], argv2);
            }
        
            // wait for them to exit
            close(pipefd[0]);
            close(pipefd[1]);
            wait(&pid1);
            wait(&pid2);
            return 0;
        }
        
        int main(void) {
          printf("[command 1]$ ");
          char* line1 = NULL;
          char* argv1[16] = {NULL};
          if (parse(line1, argv1) == -1) {
            exit(EXIT_FAILURE);
          }
          printf("[command 2]$ ");
          char* line2 = NULL;
          char* argv2[16] = {NULL};
          if (parse(line2, argv2) == -1) {
            exit(EXIT_FAILURE);
          }
          concat(argv1, argv2);
          free(line1);
          free(line2);
        }

4. `**` 擴展內核，實現共享內存機制。

    略

5. `***` 擴展內核，實現signal機制。

    略，設計思路可參見問答題2。

問答題
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. `*` 直接通信和間接通信的本質區別是什麼？分別舉一個例子。

    本質區別是消息是否經過內核，如共享內存就是直接通信，消息隊列則是間接通信。

2. `**` 試說明基於UNIX的signal機制，如果在本章內核中實現，請描述其大致設計思路和運行過程。

    首先需要添加兩個syscall，其一是註冊signal handler，其二是發送signal。其次是添加對應的內核數據結構，對於每個進程需要維護兩個表，其一是signal到handler地址的對應，其二是尚未處理的signal。當進程註冊signal handler時，將所註冊的處理函數的地址填入表一。當進程發送signal時，找到目標進程，將signal寫入表二的隊列之中。隨後修改從內核態返回用戶態的入口點的代碼，檢查是否有待處理的signal。若有，檢查是否有對應的signal handler並跳轉到該地址，如無則執行默認操作，如殺死進程。需要注意的是，此時需要記住原本的跳轉地址，當進程從signal handler返回時將其還原。

3. `**` 比較在Linux中的無名管道（普通管道）與有名管道（FIFO）的異同。

    同：兩者都是進程間信息單向傳遞的通路，可以在進程之間傳遞一個字節流。異：普通管道不存在文件系統上對應的文件，而是僅由讀寫兩端兩個fd表示，而FIFO則是由文件系統上的一個特殊文件表示，進程打開該文件後獲得對應的fd。

4. `**` 請描述Linux中的無名管道機制的特徵和適用場景。

    無名管道用於創建在進程間傳遞的一個字節流，適合用於流式傳遞大量數據，但是進程需要自己處理消息間的分割。

5. `**` 請描述Linux中的消息隊列機制的特徵和適用場景。

    消息隊列用於在進程之間發送一個由type和data兩部分組成的短消息，接收消息的進程可以通過type過濾自己感興趣的消息，適用於大量進程之間傳遞短小而多種類的消息。

6. `**` 請描述Linux中的共享內存機制的特徵和適用場景。

    共享內存用於創建一個多個進程可以同時訪問的內存區域，故而消息的傳遞無需經過內核的處理，適用在需要較高性能的場景，但是進程之間需要額外的同步機制處理讀寫的順序與時機。

7. `**` 請描述Linux的bash shell中執行與一個程序時，用戶敲擊 `Ctrl+C` 後，會產生什麼信號（signal），導致什麼情況出現。

    會產生SIGINT，如果該程序沒有捕獲該信號，它將會被殺死，若捕獲了，通常會在處理完或是取消當前正在進行的操作後主動退出。

8. `**` 請描述Linux的bash shell中執行與一個程序時，用戶敲擊 `Ctrl+Zombie` 後，會產生什麼信號（signal），導致什麼情況出現。

    會產生SIGTSTP，該進程將會暫停運行，將控制權重新轉回shell。

9. `**` 請描述Linux的bash shell中執行 `kill -9 2022` 這個命令的含義是什麼？導致什麼情況出現。

    向pid為2022的進程發送SIGKILL，該信號無法被捕獲，該進程將會被強制殺死。

10. `**` 請指出一種跨計算機的主機間的進程間通信機制。

    一個在過去較為常用的例子是Sun RPC。
