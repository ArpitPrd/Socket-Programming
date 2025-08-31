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
void set_up_host(struct sockaddr_in* server_addr, int port) {
    server_addr->sin_family = AF_INET;
    server_addr->sin_port = htons(port);
    server_addr->sin_addr.s_addr = INADDR_ANY;
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


/**
 * @brief splits a string of words about the delimiter
 * 
 * @param s string to be dplit
 * @param delimiter can be anyhting in chars
 */
vector<string> split(string s, char delimiter) {
    vector<string> words;
    string word;

    stringstream ss(s);
    while (getline(ss, word)) { // split by '\n' first
        stringstream line_ss(word);
        string token;
        while (getline(line_ss, token, delimiter)) { // then split further by delimiter
            if (!token.empty())
                words.push_back(token);
        }
    }

    return words;
}

string handle_request(string message, string filename) {
    string words = file_to_string(filename);
    vector<string> words_vector = split(words, ',');

    vector<string> p_and_k = split(message, ',');
    int p = stoi(p_and_k[0]), k = stoi(p_and_k[1]);
    
    if (p >= words_vector.size()) {
        return "EOF\n";
    }

    string req_words = "";

    int j = min<int>(p+k, static_cast<int>(words_vector.size()));
    for (int i = p; i < j; i++) {
        req_words += words_vector[i];
        if (i!=(j-1)) {
            req_words += ",";
        }
    }
    if ((p+k)>words_vector.size()) {
        req_words += ",EOF";
    }

    req_words += "\n";

    return req_words;
    
}

int main(int argc, char *argv[]) {

    string config_file = "config.json";

    for (int i = 1; i < argc; i++) {
        string flag = argv[i];

        if (flag=="--config") {
            config_file = argv[i+1];
            i++;
        }
    }

    map<string, string> info = parse_json(config_file);
    string filename=info["filename"];
    int port=stoi(info["server_port"]);
    
    /* opening a socket at server can check if inside a function this works or not */
    int server_socket_fd = socket(AF_INET, SOCK_STREAM, 0);
    
    /* now we prepare the server */
    struct sockaddr_in server_addr;
    set_up_host(&server_addr, port);
    
    /* establish a binding */
    int bind_index=bind(server_socket_fd, (struct sockaddr *) &server_addr, sizeof(server_addr));
    if (bind_index < 0) {
        cerr << "ERROR: in binding";
        exit(1);
    }
    /* listen on all of the ports */
    listen(server_socket_fd, 5);

    /* accept message from the client */
    struct sockaddr_in client_addr;
    socklen_t client_len = sizeof(client_addr);
    int client_socket_fd = accept(server_socket_fd, (struct sockaddr *) &client_addr, &client_len);
    if (client_socket_fd < 0) {
        cerr << "ERROR: unable to accept";
        exit(1);
    }

    /* reading from the client */
    char recv_buffer[128] = {0};
    int index = read(client_socket_fd, recv_buffer, 127);
    if (index < 0) {
        cerr << "ERROR: reading from socket";
    }

    /* handling the request */
    string recv_message(recv_buffer, index);
    string send_message = handle_request(recv_message, filename);

    /* sending the request */
    const char * send_buffer = send_message.c_str();
    index = write(client_socket_fd, send_buffer, send_message.size());
    if (index < 0) {
        cerr << "ERROR: write to socket";
        exit(1);
    }

    /* clolsing the client socket */
    close(client_socket_fd);
    close(server_socket_fd);
}