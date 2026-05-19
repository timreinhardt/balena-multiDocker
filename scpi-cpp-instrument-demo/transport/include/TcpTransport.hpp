#pragma once

#include "ITransport.hpp"
#include <string>

class TcpTransport : public ITransport {
public:
    TcpTransport(const std::string& host, int port);

    bool connectToTarget() override;
    std::string sendCommand(const std::string& command) override;

private:
    std::string host_;
    int port_;
    int sockfd_ = -1;
};