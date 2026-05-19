#include "TcpTransport.hpp"

#include <arpa/inet.h>
#include <netdb.h>
#include <unistd.h>

#include <cstring>
#include <stdexcept>

TcpTransport::TcpTransport(const std::string& host, int port)
    : host_(host), port_(port) {}

bool TcpTransport::connectToTarget() {
    struct addrinfo hints {};
    struct addrinfo* result = nullptr;

    hints.ai_family = AF_UNSPEC;
    hints.ai_socktype = SOCK_STREAM;

    int status = getaddrinfo(host_.c_str(), std::to_string(port_).c_str(), &hints, &result);
    if (status != 0) {
        throw std::runtime_error("getaddrinfo failed: " + std::string(gai_strerror(status)));
    }

    for (auto* rp = result; rp != nullptr; rp = rp->ai_next) {
        sockfd_ = socket(rp->ai_family, rp->ai_socktype, rp->ai_protocol);
        if (sockfd_ == -1) {
            continue;
        }

        if (connect(sockfd_, rp->ai_addr, rp->ai_addrlen) == 0) {
            freeaddrinfo(result);
            return true;
        }

        close(sockfd_);
        sockfd_ = -1;
    }

    freeaddrinfo(result);
    throw std::runtime_error("Could not connect to " + host_ + ":" + std::to_string(port_));
}

std::string TcpTransport::sendCommand(const std::string& command) {
    if (sockfd_ < 0) {
        connectToTarget();
    }

    std::string message = command;
    if (message.empty() || message.back() != '\n') {
        message += "\n";
    }

    ssize_t sent = send(sockfd_, message.c_str(), message.size(), 0);
    if (sent < 0) {
        throw std::runtime_error("send failed");
    }

    char buffer[4096] {};
    ssize_t received = recv(sockfd_, buffer, sizeof(buffer) - 1, 0);
    if (received < 0) {
        throw std::runtime_error("recv failed");
    }

    return std::string(buffer, received);
}