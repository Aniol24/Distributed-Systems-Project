#define _POSIX_C_SOURCE 200112L
#include <arpa/inet.h>
#include <errno.h>
#include <netinet/in.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <unistd.h>

static volatile sig_atomic_t running = 1;
static int listen_fd = -1, client_fd = -1;

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

  listen_fd = socket(AF_INET, SOCK_STREAM, 0);
  if (listen_fd < 0) {
    perror("socket");
    return 1;
  }

  int yes = 1;
  if (setsockopt(listen_fd, SOL_SOCKET, SO_REUSEADDR, &yes, sizeof(yes)) < 0) {
    perror("setsockopt");
  }

  struct sockaddr_in addr;
  memset(&addr, 0, sizeof(addr));
  addr.sin_family = AF_INET;
  addr.sin_addr.s_addr = htonl(INADDR_ANY);
  addr.sin_port = htons(port);

  if (bind(listen_fd, (struct sockaddr *)&addr, sizeof(addr)) < 0) {
    perror("bind");
    return 1;
  }

  if (listen(listen_fd, 8) < 0) {
    perror("listen");
    return 1;
  }

  printf("[master] Escoltant al port %u… (Ctrl+C per sortir)\n", port);

  struct sockaddr_in caddr;
  socklen_t clen = sizeof(caddr);
  client_fd = accept(listen_fd, (struct sockaddr *)&caddr, &clen);
  if (client_fd < 0) {
    if (running)
      perror("accept");
    return 1;
  }

  char cip[INET_ADDRSTRLEN];
  inet_ntop(AF_INET, &caddr.sin_addr, cip, sizeof(cip));
  printf("[master] Connexió rebuda de %s:%u\n", cip, ntohs(caddr.sin_port));
  printf("[master] De moment no fem res; el socket queda obert. Ctrl+C per "
         "sortir.\n");

  while (running)
    pause();

  return 0;
}
