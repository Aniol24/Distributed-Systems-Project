#include "Message.h"
#include <cstring>
#include <io.h>

Message::Message(uint8_t type, uint32_t var): type(type), var(var) {};

Message::Message(uint8_t buffer[]) {
    memcpy(&type, buffer, sizeof(type));
    memcpy(&var, buffer + sizeof(type), sizeof(var));
}

uint8_t Message::get_type() {
    return this->type;
}

uint32_t Message::get_var() {
    return this->var;
}

bool Message::message_send(int socket_fd) {

    // Serialize the message
    uint8_t buffer[sizeof(type) + sizeof(var)];
    memcpy(buffer, &type, sizeof(type));
    memcpy(buffer + sizeof(type), &var, sizeof(var));

    // Send the message
    ssize_t bytes_sent = write(socket_fd, &buffer, sizeof(buffer));
    return bytes_sent == sizeof(buffer);
}

string Message::to_string() {
    return "Message(type=" + std::to_string(this->type) + ", var=" + std::to_string(this->var) + ")";
}

