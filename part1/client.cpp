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
#include <chrono>

using namespace std;
using namespace std::chrono;
using hrc = time_point<high_resolution_clock>;
#define now() high_resolution_clock::now()

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

void print_freq(string message) {
    int n = message.size();
    map<string, int> freq;
    vector<string> words = split(message, ',');
    
    for (string word: words) {
        if (freq.find(word) == freq.end()) {
            freq[word]=0;
        }
        freq[word] += 1;
    }

    /* printing the word */
    for (auto &p : freq) {
        if (p.first != "EOF\n") {
            cout << p.first << ", " << p.second << endl;
        }
    }


    return;

}

/**
 *@brief parses the file and finds out if there actually is some EOF token
 */
bool eof(vector<string> words) {
    for (string word: words) {
        if (word=="EOF") {
            return true;
        }
    }
    return false;
}

int main(int argc, char * argv[]) {

    string config_file = "config.json";
    map<string, string> info = parse_json(config_file);
    string server_ip=info["server_ip"];

    int p=stoi(info["p"]);
    int k=stoi(info["k"]);
    int port=stoi(info["server_port"]);
    bool single_run = false, quiet=false;

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

        if (flag=="--run") {
            single_run = true;
        }

        if (flag=="--quiet") {
            quiet = true;
        }
    }


    
    int client_socket_fd = socket(AF_INET, SOCK_STREAM, 0); // the file descriptor of the client
    
    /* now we prepare the server */
    struct hostent* server = gethostbyname(server_ip.c_str());
    if (!server) {
        cerr << "ERROR: No host by ip " << server_ip << "\n";
        exit(1);
    }
    struct sockaddr_in server_addr;
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(port);
    memcpy(&server_addr.sin_addr.s_addr, server->h_addr, server->h_length);
    
    /* establish a TCP connection */
    int index = connect(client_socket_fd, (struct sockaddr*) &server_addr, sizeof(server_addr));
    if (index < 0) {
        cerr << "ERROR: connection not done" << endl;
    }
    
    double file_download_time = 0;
    string full_doc = "";
    while (true) {
        /* prepare the messahge */
        string send_message = to_string(p) + string(",") + to_string(k) + "\n";
        const char* send_buffer = send_message.c_str();

        /* recieve any message from the server */
        string recv_message;
        char recv_buffer[4096];  // larger buffer is fine

        /* loggin the time */
        hrc start = now();

        /* send the message to the server, message can be found on the file descriptor */
        cout << "sending request" << endl;
        send(client_socket_fd, send_buffer, send_message.size(), 0);

        int bytes_received = recv(client_socket_fd, recv_buffer, sizeof(recv_buffer), 0);
        
        /* logging download time */
        hrc end = now();
        
        if (bytes_received > 0) {
            recv_message.assign(recv_buffer, bytes_received);  // use only valid bytes
        }

        double delta = duration<double, std::milli>(end - start).count();

        file_download_time += delta;

        full_doc += recv_message;

        vector<string> words = split(recv_message, ',');
        if (eof(words)) {
            break;
        }

        if (single_run) break;

        p += k;
    }

    /* telling the server I am done */
    string send_message = "STOP";
    const char* send_buffer = send_message.c_str();
    send(client_socket_fd, send_buffer, send_message.size(), 0);

    /*diplaying ELAPSED_MS*/
    if (!quiet) cout << "ELAPSED_MS:" << file_download_time << endl;

    /* clolsing the client socket */
    close(client_socket_fd);

    /* use this recieved buffer for further manipulations */
    if (!quiet) print_freq(full_doc);
    
}