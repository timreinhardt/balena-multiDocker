cmake_minimum_required(VERSION 3.16)

project(scpi_cpp_instrument_demo LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_executable(scpi_cpp_demo
    ui/main.cpp
    core/src/ScpiClient.cpp
    transport/src/TcpTransport.cpp
)

target_include_directories(scpi_cpp_demo PRIVATE
    core/include
    transport/include
)