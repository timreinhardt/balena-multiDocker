#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <netinet/in.h>
#include <sys/socket.h>
#include <sys/stat.h>
#include <time.h>

int led_on = 0;
int counter = 0;

#define LOG_DIR "/data"
#define LOG_FILE "/data/c-demo.log"

void log_message(const char *message) {
    FILE *file;
    time_t now;
    struct tm *time_info;
    char timestamp[64];

    mkdir(LOG_DIR, 0777);

    now = time(NULL);
    time_info = localtime(&now);

    strftime(timestamp, sizeof(timestamp), "%Y-%m-%d %H:%M:%S", time_info);

    printf("[%s] %s\n", timestamp, message);
    fflush(stdout);

    file = fopen(LOG_FILE, "a");

    if (file != NULL) {
        fprintf(file, "[%s] %s\n", timestamp, message);
        fclose(file);
    }
}

void send_response(int client, const char *body) {
    char response[4096];

    snprintf(response, sizeof(response),
        "HTTP/1.1 200 OK\r\n"
        "Content-Type: text/html\r\n"
        "Connection: close\r\n"
        "\r\n"
        "%s",
        body
    );

    write(client, response, strlen(response));
}

int main() {
    int server_fd;
    int client;
    struct sockaddr_in address;
    char buffer[1024];

    server_fd = socket(AF_INET, SOCK_STREAM, 0);

    address.sin_family = AF_INET;
    address.sin_addr.s_addr = INADDR_ANY;
    address.sin_port = htons(8080);

    bind(server_fd, (struct sockaddr *)&address, sizeof(address));
    listen(server_fd, 5);

    log_message("========================================");
    log_message("Starting Balena C Demo Server");
    log_message("Open browser at: http://<PI-IP>:8080");
    log_message("Log file: /data/c-demo.log");
    log_message("========================================");

    while (1) {
        client = accept(server_fd, NULL, NULL);

        memset(buffer, 0, sizeof(buffer));
        read(client, buffer, sizeof(buffer) - 1);

        log_message(buffer);

        if (strstr(buffer, "POST /toggle")) {
            led_on = !led_on;

            if (led_on) {
                log_message("LED toggled ON");
            } else {
                log_message("LED toggled OFF");
            }
        }

        if (strstr(buffer, "POST /count")) {
            counter++;

            char count_log[128];
            snprintf(count_log, sizeof(count_log),
                "Counter incremented to %d", counter);

            log_message(count_log);
        }

        char body[2048];

        snprintf(body, sizeof(body),
            "<html>"
            "<body style='font-family: Arial; padding: 30px;'>"
            "<h1>Balena C Demo</h1>"
            "<p>Raw C socket HTTP server</p>"
            "<p>LED state: <b>%s</b></p>"
            "<p>Counter: <b>%d</b></p>"
            "<p>Log file: <b>/data/c-demo.log</b></p>"
            "<form action='/toggle' method='POST'>"
            "<button>Toggle LED</button>"
            "</form>"
            "<form action='/count' method='POST'>"
            "<button>Increment Counter</button>"
            "</form>"
            "</body>"
            "</html>",
            led_on ? "ON" : "OFF",
            counter
        );

        send_response(client, body);

        close(client);
    }

    return 0;
}
