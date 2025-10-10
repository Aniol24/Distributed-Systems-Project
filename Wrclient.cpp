/*
    WRClient class implementation in c++ by Aniol Verges
*/

#include "Wrclient.h"

WRClient::WRClient(int port): port(port) {

    int clientSocket = socket(AF_INET, SOCK_STREAM, 0);
    if (clientSocket < 0) {
        perror("socket");
        exit(EXIT_FAILURE);
    }

    sockaddr_in serverAddress;
    serverAddress.sin_family = AF_INET;
    serverAddress.sin_port = htons(port);
    serverAddress.sin_addr.s_addr = inet_addr("127.0.0.1");

    if (connect(clientSocket, (struct sockaddr *)&serverAddress, sizeof(serverAddress)) < 0) {
        perror("connect");
        close(clientSocket);
        exit(EXIT_FAILURE);
    }

    while(1){
        // Logic goes here...
    }
    
}

