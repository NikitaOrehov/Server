#include <iostream>
#include <string>
#include <sstream>

#ifdef _WIN32
#include <winsock2.h>
#pragma comment(lib, "ws2_32.lib")
#else
#include <sys/socket.h>
#include <netinet/in.h>
#include <unistd.h>
#endif

#include <thread>
#include <cstring>
#include <cstdlib>

const int PORT = 8080;
const int BUFFER_SIZE = 1024;

void handleClient(int clientSocket) {
    char buffer[BUFFER_SIZE] = { 0 };
    size_t bytesRead;

#ifdef _WIN32
    bytesRead = recv(clientSocket, buffer, BUFFER_SIZE - 1, 0);
#else
    bytesRead = recv(clientSocket, buffer, BUFFER_SIZE - 1, 0);
#endif

    if (bytesRead > 0) {
        std::cout << "Received from client: " << buffer << std::endl;

        std::string response = "HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\nHello from C++ Server!";

#ifdef _WIN32
        send(clientSocket, response.c_str(), response.length(), 0);
#else
        send(clientSocket, response.c_str(), response.length(), 0);
#endif

    }
    else {
        std::cerr << "Error reading from socket or client disconnected." << std::endl;
    }

#ifdef _WIN32
    closesocket(clientSocket);
#else
    close(clientSocket);
#endif
}

int main() {
#ifdef _WIN32
    WSADATA wsaData;
    if (WSAStartup(MAKEWORD(2, 2), &wsaData) != 0) {
        std::cerr << "WSAStartup failed." << std::endl;
        return 1;
    }
#endif

    int serverSocket, clientSocket;
    struct sockaddr_in serverAddress, clientAddress;
#ifdef _WIN32
    typedef int socklen_t;
#endif
    socklen_t clientAddressLength = sizeof(clientAddress);

    serverSocket = socket(AF_INET, SOCK_STREAM, 0);
    if (serverSocket == -1) {
        std::cerr << "Error creating socket" << std::endl;
        return -1;
    }

    serverAddress.sin_family = AF_INET;
    serverAddress.sin_addr.s_addr = INADDR_ANY;
    serverAddress.sin_port = htons(PORT);

    if (bind(serverSocket, (struct sockaddr*)&serverAddress, sizeof(serverAddress)) < 0) {
        std::cerr << "Error binding socket" << std::endl;
#ifdef _WIN32
        closesocket(serverSocket);
#else
        close(serverSocket);
#endif
        return -1;
    }

    if (listen(serverSocket, 5) < 0) {
        std::cerr << "Error listening on socket" << std::endl;
#ifdef _WIN32
        closesocket(serverSocket);
#else
        close(serverSocket);
#endif
        return -1;
    }

    std::cout << "Server listening on port " << PORT << std::endl;

    while (true) {
        clientSocket = accept(serverSocket, (struct sockaddr*)&clientAddress, &clientAddressLength);
        if (clientSocket < 0) {
            std::cerr << "Error accepting connection" << std::endl;
            continue;
        }

        std::thread clientThread(handleClient, clientSocket);
        clientThread.detach();
    }

#ifdef _WIN32
    closesocket(serverSocket);
    WSACleanup();
#else
    close(serverSocket);
#endif
    return 0;
}