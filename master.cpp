#include <Master.h>

bool Server_start(uint16_t port) {

      listen_fd = socket(AF_INET, SOCK_STREAM, 0);
      if (listen_fd < 0) {
        perror("socket");
        return false;
      }

      int yes = 1;
      if (setsockopt(listen_fd, SOL_SOCKET, SO_REUSEADDR, &yes, sizeof(yes)) < 0) {
        perror("setsockopt");
      }

      struct sockaddr_in addr;
      memset(&addr, 0, sizeof(addr));
      addr.sin_family = AF_INET;
      inet_pton(AF_INET, "127.0.0.1", &addr.sin_addr);
      addr.sin_port = htons(port);

      if (bind(listen_fd, (struct sockaddr *)&addr, sizeof(addr)) < 0) {
        perror("bind");
        return false;
      }

      if (listen(listen_fd, 8) < 0) {
        perror("listen");
        return false;
      }

      printf("[master] Escoltant al port %u… (Ctrl+C per sortir)\n", port);

      struct sockaddr_in caddr;
      socklen_t clen = sizeof(caddr);
      client_fd = accept(listen_fd, (struct sockaddr *)&caddr, &clen);
      if (client_fd < 0) {
        if (running)
          perror("accept");
        return false;
      }

      char cip[INET_ADDRSTRLEN];
      inet_ntop(AF_INET, &caddr.sin_addr, cip, sizeof(cip));
      printf("[master] Connexió rebuda de %s:%u\n", cip, ntohs(caddr.sin_port));
      printf("[master] De moment no fem res; el socket queda obert. Ctrl+C per "
            "sortir.\n");

      return true;
    }

    ~Master() {}

};

static void on_sigint(int sig) {
  (void)sig;
  running = 0;
  if (client_fd >= 0)
    close(client_fd);
  if (listen_fd >= 0)
    close(listen_fd);
  write(STDOUT_FILENO, "\n[master] Sortint...\n", 22);
}

int main(int argc, char **argv) {
  uint16_t port = (argc >= 2) ? (uint16_t)atoi(argv[1]) : 5000;

  signal(SIGINT, on_sigint);
  signal(SIGTERM, on_sigint);

  Master master;
  if (!master.Server_Start(port)) printf("Error iniciant el servidor\n");
  

  while (running)
    pause();

  return 0;
}
