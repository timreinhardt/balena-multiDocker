#pragma once
#include <string>

class ITransport {
public:
    virtual ~ITransport() = default;

    virtual bool connectToTarget() = 0;
    virtual std::string sendCommand(const std::string& command) = 0;
};