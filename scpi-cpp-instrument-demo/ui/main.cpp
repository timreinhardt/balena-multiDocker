#include "ScpiClient.hpp"
#include "TcpTransport.hpp"

#include <iostream>
#include <memory>
#include <string>

int main(int argc, char* argv[]) {
    if (argc < 4) {
        std::cerr << "Usage:\n";
        std::cerr << "  " << argv[0] << " <host> <port> <command>\n\n";
        std::cerr << "Example:\n";
        std::cerr << "  " << argv[0] << " 127.0.0.1 5025 \"*IDN?\"\n";
        return 1;
    }

    std::string host = argv[1];
    int port = std::stoi(argv[2]);
    std::string command = argv[3];

    try {
        auto transport = std::make_unique<TcpTransport>(host, port);
        ScpiClient client(std::move(transport));

        std::string response = client.query(command);

        std::cout << "Command:  " << command << "\n";
        std::cout << "Response: " << response << "\n";
    } catch (const std::exception& ex) {
        std::cerr << "ERROR: " << ex.what() << "\n";
        return 2;
    }

    return 0;
}