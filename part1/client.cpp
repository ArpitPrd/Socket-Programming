#include <iostream>
#include <string>
#include <sys/socket.h>
#include <netint/in.h>
#include <netdb.h>
#include <unistd.h>

using namespace std;
/**
 * @brief use this to get ip to host
 */
struct hostent ip_to_host(string ip) {
    return gethostbyname(ip);
}

/* use this for making a TCP connection */
void TCP_Connect(int sock_file_descriptor, struct sockaddr * server_addr) {
    int connection = connect(sock_file_descriptor,  server_addr)
    if (connection < 0) {
        cout << "ERROR: connection not done" << endl;
    }
}



int main() {

}