#include <Master.h>

bool Server_start(uint16_t port) {

  this->listen_fd = socket(AF_INET, SOCK_STREAM, 0);
  if (this->listen_fd < 0) {
      perror("socket");
      return false;
  }

  int yes = 1;
  if (setsockopt(this->listen_fd, SOL_SOCKET, SO_REUSEADDR, &yes, sizeof(yes)) < 0) {
      perror("setsockopt");
  }

  struct sockaddr_in addr;
  memset(&addr, 0, sizeof(addr));
  addr.sin_family = AF_INET;
  inet_pton(AF_INET, "127.0.0.1", &addr.sin_addr);
  addr.sin_port = htons(port);

  if (bind(this->listen_fd, (struct sockaddr *)&addr, sizeof(addr)) < 0) {
      perror("bind");
      return false;
  }

  if (listen(this->listen_fd, 8) < 0) {
      perror("listen");
      return false;
  }

  cout << "[master] Escoltant al port" << port << " … (Ctrl+C per sortir)\n";

  struct sockaddr_in caddr;
  socklen_t clen = sizeof(caddr);
  while (true) {
      int client_fd = accept(this->listen_fd, (struct sockaddr *)&caddr, &clen);
      if (client_fd < 0) {
      if (running)
          perror("accept");
      return false;
      }
      cout << "[master] Connexió rebuda\n";
  
  }

  char cip[INET_ADDRSTRLEN];
  inet_ntop(AF_INET, &caddr.sin_addr, cip, sizeof(cip));
  printf("[master] Connexió rebuda de %s:%u\n", cip, ntohs(caddr.sin_port));
  printf("[master] De moment no fem res; el socket queda obert. Ctrl+C per "
          "sortir.\n");

  return true;
}