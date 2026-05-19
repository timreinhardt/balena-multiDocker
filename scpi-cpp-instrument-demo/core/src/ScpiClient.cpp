#include "ScpiClient.hpp"

ScpiClient::ScpiClient(std::unique_ptr<ITransport> transport)
    : transport_(std::move(transport)) {}

std::string ScpiClient::query(const std::string& command) {
    return transport_->sendCommand(command);
}