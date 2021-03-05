# Jeon Sang Ho 20174677
import select
from socket import *
import sys
import time
import queue

serverPort = 34677
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
serverSocket.setblocking(0) # set socket to non blocking socket
serverSocket.bind(('', serverPort))
serverSocket.listen()
print("The server is ready to receive on port", serverPort)

input_list = [serverSocket]
output_list = []
clientsum = 0
init = time.time()
message_queue = {}
client_info = {} # save client information as dictionary form {socket : nickname}


def message_decoder(message):
    line = message.decode()
    modified_message = line.split(":")
    return modified_message


def message_encoder(command, nickname, message):
    modified_message = (command + ":" + nickname + ":" + message)
    return modified_message.encode()

if __name__ == "__main__":

    try:
        count = 0
        while input_list:

            input_ready, write_ready, except_ready = select.select(input_list, output_list, input_list, 0)

            for ir in input_ready:

                if ir == serverSocket: # checking connections
                    connectionSocket, clientAddress = ir.accept()
                    clientsum += 1
                    connectionSocket.setblocking(0)
                    input_list.append(connectionSocket)
                    message_queue[connectionSocket] = queue.Queue(0)

                else: # receiving messages
                    message = ir.recv(2048)
                    tmp = message.decode()[0:3]
                    if tmp == "10:" or tmp == "11:":
                        command = []
                        command.append("9")
                    else:
                        command = message_decoder(message)

                    if command:
                        if command[0] == '5': # client has ended communication
                            clientsum -= 1
                            print("Client ", client_info[ir], " disconnected.")
                            print("Number of connected clients = ", clientsum)
                            input_list.remove(ir)
                            del client_info[ir]
                            del message_queue[ir]

                        elif command[0] == "1": ## modifing nickname
                            if command[1] in client_info.values() or clientsum>10:
                                clientsum -= 1
                                modified_message = ("1:"+ command[1] +":deny")
                                message_queue[ir].put(modified_message)
                                if ir not in output_list:
                                    output_list.append(ir)
                            else:
                                print("Client " +command[1]+ ' connected.')
                                print("Number of connected clients = ", clientsum)
                                modified_message = ("1:" + command[1] +":accepted")
                                client_info[ir] = command[1]
                                message_queue[ir].put(modified_message)
                                if ir not in output_list:
                                    output_list.append(ir)


                        elif command[0] == "2":
                            message = ":".join(command)
                            vaild_check = " ".join(command)
                            print(vaild_check)
                            if "i hate professor" in vaild_check:
                                print(client_info[ir] + " have cursed professor")
                                message_queue[ir].put("5:non:non")
                                if ir not in output_list:
                                    output_list.append(ir)

                            else:
                                for i in input_list:
                                    if i != serverSocket and i != ir:
                                        message_queue[i].put(message)
                                        if i not in output_list:
                                            output_list.append(i)

                        elif command[0] == "3":
                            message = ["3:non:"]
                            for i in client_info.keys():
                                message.append(str(client_info[i]) + str(i.getpeername()) + " ")
                            modified_message = "".join(message)
                            message_queue[ir].put(modified_message)
                            if ir not in output_list:
                                output_list.append(ir)


                        elif command[0] == "4":
                            message = ("4:" + client_info[ir] + ":" + str(command[2:]))
                            isthere = False
                            for socket, nick in client_info.items():
                                if command[1] == nick:
                                    isthere = True
                                    message_queue[socket].put(message)
                                    if socket not in output_list:
                                        output_list.append(socket)
                            if isthere == False:
                                message_queue[ir].put("4: non :no such person!")
                                if socket not in output_list:
                                    output_list.append(ir)

                        elif command[0] == "6":
                            message = ("6:non:version 1.1")
                            message_queue[ir].put(message)
                            if ir not in output_list:
                                output_list.append(ir)

                        elif command[0] == "7":
                            new_nick = command[2]
                            if new_nick in client_info.values():
                                message = ("7:non:deny")
                                message_queue[ir].put(message)
                                if ir not in output_list:
                                    output_list.append(ir)
                            else:
                                del client_info[ir]
                                client_info[ir] = new_nick
                                message = ("7:"+ new_nick +":accept")
                                message_queue[ir].put(message)
                                if ir not in output_list:
                                    output_list.append(ir)

                        elif command[0] == "8":
                            message = ("8:non:non")
                            message_queue[ir].put(message)
                            if ir not in output_list:
                                output_list.append(ir)

                        elif command[0] == "9":
                            # count += 1
                            # print(count)
                            for i in input_list:
                                if i != serverSocket and i != ir:
                                    message_queue[i].put(message.decode())
                                    if i not in output_list:
                                        output_list.append(i)

                        elif command[0] == "14":
                            isthere = False
                            for socket, nick in client_info.items():
                                if command[2] == nick:
                                    isthere = True
                                    message_queue[ir].put("14:valid")
                                    if socket not in output_list:
                                        output_list.append(ir)
                            if isthere == False:
                                message_queue[ir].put("14: non :no such person!")
                                if socket not in output_list:
                                    output_list.append(ir)

                        elif command[0] == "12":
                            dest = command[1]
                            data = command[1:]
                            data = ":".join(data)
                            message = ("12:" + data)
                            for socket, nick in client_info.items():
                                if dest == nick:
                                    message_queue[socket].put(message)
                                    if socket not in output_list:
                                        output_list.append(socket)

                        elif command[0] == "13":
                            dest = command[1]
                            sender = command[2]
                            filename= command[3]
                            message = ("13:" + sender +":" +filename)
                            for socket, nick in client_info.items():
                                if dest == nick:
                                    message_queue[socket].put(message)
                                    if socket not in output_list:
                                        output_list.append(socket)

                    else:  # client has ended communication
                        clientsum -= 1
                        input_list.remove(ir)
                        print("Client ", client_info[ir], " disconnected.")
                        print("Number of connected clients = ", clientsum)
                        ir.shutdown(SHUT_RDWR)
                        ir.close()
                        input_list.remove(ir)
                        del message_queue[ir]

            for wr in write_ready: # sending messages
                try:
                    next_msg = message_queue[wr].get_nowait()
                except queue.Empty:
                    output_list.remove(wr)
                else:
                    line = str(next_msg)
                    rmp = line[0:3]
                    if rmp == "10:" or rmp == "11:" or rmp == "12:" or rmp == "13:" or rmp == "14:":
                        command = "9"
                    else:
                        line = line.split(":")
                        command = line[0]
                        nickname = line[1]
                        message = line[2]

                    if command == "1":
                        modified_message = (command+":"+ nickname+":"+ message+":"+nickname+":"+str(clientsum)).encode()
                        wr.send(modified_message)

                    elif command == "5":
                        modified_message = message_encoder(command,nickname,message)
                        wr.send(modified_message)
                        clientsum -= 1
                        print("Client ", client_info[wr], " disconnected.")
                        print("Number of connected clients = ", clientsum)
                        input_list.remove(wr)
                        del client_info[wr]
                        del message_queue[wr]
                        output_list.remove(wr)

                    elif command == "9":
                        wr.send(line.encode())

                    elif command != "1" and command != "5" and command != "9":
                        modified_message = message_encoder(command,nickname,message)
                        wr.send(modified_message)

            for er in except_ready:
                input_list.remove(er)
                if er in output_list:
                    output_list.remove(er)
                er.close()
                del message_queue[er]

    except KeyboardInterrupt:  # closing server socket and end program
        serverSocket.close()
        print("bye~")
        sys.exit()
