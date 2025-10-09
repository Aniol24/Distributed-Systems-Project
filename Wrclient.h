#include <cstring>
#include <iostream>
#include <netinet/in.h>
#include <sys/socket.h>
#include <unistd.h>

class WRClient {
public:

    int port;

    WRClient(int port);

};