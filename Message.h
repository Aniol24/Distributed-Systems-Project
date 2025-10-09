#include <string>

using namespace std;

class Message {
    private:
        uint8_t type; // 1: r, 2: rw
        uint32_t var; // variable value

    public:
        Message(uint8_t type, uint32_t var);

        Message(uint8_t buffer[]);

        uint8_t get_type();

        uint32_t get_var();

        bool message_send(int socket_fd);

        string to_string();
};