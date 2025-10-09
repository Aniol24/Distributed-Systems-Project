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
};

int main(int argc, char **argv) {
  uint16_t port = (argc >= 2) ? (uint16_t)atoi(argv[1]) : 5000;
  Master master;
  signal(SIGINT, master.error_handler);
  signal(SIGTERM, master.error_handler);

  
  if (!master.Server_start(port)) printf("Error iniciant el servidor\n");
  

  while (running)
    pause();

  return 0;
}
