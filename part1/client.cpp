#include <iostream>
#include <string>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netdb.h>
#include <unistd.h>
#include <sys/types.h>
#include <stdlib.h>
#include <cstring>
#include <vector>
#include <map>
#include <arpa/inet.h>
#include <fstream>
#include <sstream>

using namespace std;

/**
 * @brief sets up the host with ip and port, this is a wrapper for the server
 */

void set_up_host(struct sockaddr_in* server_addr, struct hostent* server, int port) {
    server_addr->sin_family = AF_INET;
    server_addr->sin_port = htons(port);
    memcpy(&server_addr->sin_addr.s_addr, server->h_addr, server->h_length);
}


/**
 * @brief use this for connection tcp 
 */
void tcp_connect(int sock_file_descriptor, struct sockaddr * server_addr) {
    int connection = connect(sock_file_descriptor,  server_addr, sizeof(server_addr));
    if (connection < 0) {
        cerr << "ERROR: connection not done" << endl;
    }
}


/**
 * @brief convert a file to a string, just enter filename
 */
string file_to_string(const string &filename) {
    ifstream file(filename);
    if (!file.is_open()) {
        throw runtime_error("Could not open file: " + filename);
    }

    stringstream buffer;
    buffer << file.rdbuf();
    return buffer.str();
}

/**
 * @brief parses a json file and words somewhat like how it is in python
 */
map<string, string> parse_json(const string &filename) {
    
    /* prepare the file as a string */
    string json_string = file_to_string(filename);

    map<string, string> info;
    bool is_key = false, is_value=false;
    string key="",value="";
    for (int i = 0; i < json_string.size(); i++) {
        if (json_string[i]=='"') {
            if (!is_value) {
                is_key = !is_key;
            }
            continue;
        }
        if (json_string[i]==':') {
            is_value = true;
            continue;
        }
        if (json_string[i]==',') {
            info[key] = value;
            key = "";
            value = "";
            is_value = false;
            continue;
        }
        if (json_string[i]=='\n') continue;
        if (json_string[i]=='}') {
            info[key] = value;
            continue;
        }
        if (is_key && !is_value && json_string[i]!=' ') {
            key += json_string[i];
        }
        if (is_value && !is_key && json_string[i]!=' ') {
            value += json_string[i];
        }
    }
    return info;
}


void print_freq(string message) {
    int n = message.size();
    map<string, int> freq;
    string subst = "";
    for (int j = 0; j < n; j++) {
        
        /* checking if end of word */
        if (message[j]==',') {
            if (freq.find(subst) == freq.end()) 
                freq[subst] = 0;
            freq[subst] += 1;
            subst = "";
            continue;
        }
        
        /* adding to substring */
        subst += message[j];
    }

    /* for the last word or EOF */
    if (freq.find(subst) == freq.end()) 
        freq[subst] = 0;
    
    freq[subst] += 1;

    /* printing the word */
    for (auto &p : freq) {
        if (p.first != "EOF\n") {
            cout << p.first << ", " << p.second << endl;
        }
    }


    return;

}

int main(int argc, char * argv[]) {

    string config_file = "config.json";
    int k = -1;
    for (int i = 1; i < argc; i++) {
        string flag = argv[i];

        if (flag=="--config") {
            config_file = argv[i+1];
            i++;
        }

        if (flag=="--k") {
            k = stoi(argv[i+1]);
            i++;
        }
    }

    map<string, string> info = parse_json(config_file);
    string server_ip=info["server_ip"];
    int p=stoi(info["p"]);
    k=stoi(info["k"]);
    int port=stoi(info["server_port"]);
    
    int client_socket_fd = socket(AF_INET, SOCK_STREAM, 0); // the file descriptor of the client
    
    /* now we prepare the server */
    struct hostent* server = gethostbyname(server_ip.c_str());
    if (!server) {
        cerr << "ERROR: No host by ip " << server_ip << "\n";
        exit(1);
    }
    struct sockaddr_in server_addr;
    set_up_host(&server_addr, server, port);
    
    /* establish a TCP connection */
    tcp_connect(client_socket_fd, (struct sockaddr *) &server_addr);

    /* prepare the messahge */
    string send_message = to_string(p) + string(",") + to_string(k) + "\n";
    const char* send_buffer = send_message.c_str();

    /* send the message to the server, message can be found on the file descriptor */
    send(client_socket_fd, send_buffer, send_message.size(), 0);

    /* recieve any message from the server */
    char recv_buffer[1024] = {0};
    recv(client_socket_fd, recv_buffer, sizeof(recv_buffer), 0);

    /* clolsing the client socket */
    close(client_socket_fd);

    /* use this recieved buffer for further manipulations */
    string recv_message(recv_buffer);
    print_freq(recv_message);
}