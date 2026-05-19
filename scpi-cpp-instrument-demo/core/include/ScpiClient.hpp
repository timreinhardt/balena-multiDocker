#pragma once

#include "ITransport.hpp"
#include <memory>
#include <string>

class ScpiClient {
public:
    explicit ScpiClient(std::unique_ptr<ITransport> transport);

    std::string query(const std::string& command);

private:
    std::unique_ptr<ITransport> transport_;
};