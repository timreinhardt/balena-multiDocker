#include <stdio.h>      // printf, snprintf, FILE
#include <string.h>     // strstr, memset, strlen
#include <unistd.h>     // read, write, close
#include <netinet/in.h> // sockaddr_in, htons
#include <sys/socket.h> // socket, bind, listen, accept
#include <sys/stat.h>   // mkdir
#include <time.h>       // timestamps

// Server will run on:
#define PORT 8080

// Shared persistent log folder/file
#define LOG_DIR "/data"
#define LOG_FILE "/data/c-demo.log"

// Simple state variables (simulate hardware/app state)
int led_on = 0;
int counter = 0;


/*
----------------------------------------
LOGGING FUNCTION
----------------------------------------
Writes message to:
1. Terminal
2. /data/c-demo.log
*/
void log_message(const char *message) {
    FILE *file;
    time_t now;
    struct tm *time_info;
    char timestamp[64];

    // Ensure log folder exists
    mkdir(LOG_DIR, 0777);

    // Current time
    now = time(NULL);
    time_info = localtime(&now);

    // Format timestamp
    strftime(timestamp, sizeof(timestamp), "%Y-%m-%d %H:%M:%S", time_info);

    // Print to container logs
    printf("[%s] %s\n", timestamp, message);
    fflush(stdout);

    // Append to persistent log file
    file = fopen(LOG_FILE, "a");

    if (file != NULL) {
        fprintf(file, "[%s] %s\n", timestamp, message);
        fclose(file);
    }
}


/*
----------------------------------------
SEND HTTP RESPONSE
----------------------------------------
Builds full HTTP response:
Status line
Content type
Body

Example:
GET /status -> JSON
GET /       -> HTML
*/
void send_response(int client, const char *content_type, const char *body) {
    char response[4096];

    snprintf(response, sizeof(response),
        "HTTP/1.1 200 OK\r\n"
        "Content-Type: %s\r\n"
        "Connection: close\r\n"
        "\r\n"
        "%s",
        content_type,
        body
    );

    write(client, response, strlen(response));
}


/*
----------------------------------------
JSON API STATUS
----------------------------------------
Used for:
GET  /status
POST /toggle
POST /count
POST /reset

Returns machine-readable JSON
*/
void send_json_status(int client) {
    char json[256];

    snprintf(json, sizeof(json),
        "{ \"ledOn\": %s, \"counter\": %d }\n",
        led_on ? "true" : "false",
        counter
    );

    send_response(client, "application/json", json);
}


/*
----------------------------------------
HTML DASHBOARD
----------------------------------------
Used for:
GET /

Human browser dashboard
*/
void send_html_dashboard(int client) {
    char body[2048];

    snprintf(body, sizeof(body),
        "<html>"
        "<body style='font-family: Arial; padding: 30px;'>"
        "<h1>Balena C Demo</h1>"
        "<p>Raw C socket HTTP server + JSON API</p>"
        "<p>LED state: <b>%s</b></p>"
        "<p>Counter: <b>%d</b></p>"
        "<p>Log file: <b>/data/c-demo.log</b></p>"
        "<p>GET JSON status: <a href='/status'>/status</a></p>"
        "<form action='/toggle' method='POST'>"
        "<button>POST Toggle LED</button>"
        "</form>"
        "<form action='/count' method='POST'>"
        "<button>POST Increment Counter</button>"
        "</form>"
        "<form action='/reset' method='POST'>"
        "<button>POST Reset</button>"
        "</form>"
        "</body>"
        "</html>",
        led_on ? "ON" : "OFF",
        counter
    );

    send_response(client, "text/html", body);
}


/*
----------------------------------------
MAIN SERVER
----------------------------------------
Browser/Postman/curl = CLIENT
This C app = SERVER

GET:
Read/view data

POST:
Change data/state
*/
int main(void) {
    int server_fd;
    int client;
    struct sockaddr_in address;

    // Raw HTTP request from browser/client
    char buffer[1024];

    // Create TCP socket
    server_fd = socket(AF_INET, SOCK_STREAM, 0);

    // Allow quick restart without port lock
    int reuse = 1;
    setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR, &reuse, sizeof(reuse));

    // Configure server address
    address.sin_family = AF_INET;
    address.sin_addr.s_addr = INADDR_ANY;
    address.sin_port = htons(PORT);

    // Bind socket to port
    bind(server_fd, (struct sockaddr *)&address, sizeof(address));

    // Listen for incoming clients
    listen(server_fd, 5);

    log_message("========================================");
    log_message("Starting Balena C Demo Server");
    log_message("GET dashboard: http://<PI-IP>:8080");
    log_message("GET API JSON: http://<PI-IP>:8080/status");
    log_message("POST endpoints: /toggle /count /reset");
    log_message("Log file: /data/c-demo.log");
    log_message("========================================");


    /*
    Infinite loop:
    Wait for requests forever
    */
    while (1) {

        // Wait for browser/client connection
        client = accept(server_fd, NULL, NULL);

        // Clear previous request
        memset(buffer, 0, sizeof(buffer));

        // Read HTTP request
        read(client, buffer, sizeof(buffer) - 1);

        log_message(buffer);


        /*
        ----------------------------------------
        POST /toggle
        Browser button or curl:
        curl -X POST http://IP:8080/toggle
        ----------------------------------------
        */
        if (strstr(buffer, "POST /toggle")) {

            led_on = !led_on;

            log_message(led_on ? "LED toggled ON" : "LED toggled OFF");

            send_json_status(client);
        }


        /*
        ----------------------------------------
        POST /count
        Increment state
        ----------------------------------------
        */
        else if (strstr(buffer, "POST /count")) {

            counter++;

            char count_log[128];

            snprintf(count_log, sizeof(count_log),
                "Counter incremented to %d", counter);

            log_message(count_log);

            send_json_status(client);
        }


        /*
        ----------------------------------------
        POST /reset
        Reset all state
        ----------------------------------------
        */
        else if (strstr(buffer, "POST /reset")) {

            led_on = 0;
            counter = 0;

            log_message("State reset");

            send_json_status(client);
        }


        /*
        ----------------------------------------
        GET /status
        Machine/API check
        ----------------------------------------
        */
        else if (strstr(buffer, "GET /status")) {

            log_message("Status requested");

            send_json_status(client);
        }


        /*
        ----------------------------------------
        Default:
        GET /
        Browser homepage/dashboard
        ----------------------------------------
        */
        else {

            log_message("Dashboard requested");

            send_html_dashboard(client);
        }

        // Close client connection
        close(client);
    }

    return 0;
}