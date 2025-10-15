#include <arpa/inet.h>
#include <errno.h>
#include <netinet/in.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <unistd.h>
#include <iostream>

using namespace std;

static volatile sig_atomic_t running = 1;

class Master {
    private:
        int listen_fd = -1;

    public:
        Master();

        ~Master();

        void error_handler(int signal);

        bool Server_start(uint16_t port);

        bool process_request();
};


