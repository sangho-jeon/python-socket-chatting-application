#Jeon Sang Ho 20174677
import time
from socket import *
import sys
import os
import argparse
import threading

# code = 1 -> sending nickname
# code = 2 -> normal message
# code = 3~ -> commands
# issue: close thread gracefully... the socket doesn't close well.

global lock
global exited
lock = threading.Lock()

def nickname_vaild(nickname):
    valid = True
    nick = list(nickname)
    for i in nick:
        ascii = ord(i)
        if ascii == 45 or 65 <= ascii <= 90 or 97 <= ascii <= 122:
            continue
        else:
            valid = False

    if valid == False:
        print("nickname is not valid!")
        sys.exit()

def modifying_nickname(nickname):
    global clientSocket
    global myname
    global lock

    clientSocket.send(("1:" + nickname + ": non").encode())

    status = clientSocket.recv(2048)
    status = status.decode().split(":")
    if status[2] == "accepted":
        ipport = str(clientSocket.getpeername())
        ipport = ipport.replace("(", "")
        ipport = ipport.replace(")" , "")
        info = ipport.split(",")
        print("welcome " + status[3] + " to cau-netclass chat room at IP=" + info[0] + " Port=" + info[1] + " you are " + status[4] + "th user.")
        print(">commands \n>\\users: shows list of people in this room \n>\\wh 'nickname' 'contents' : whispers to the person you want")
        print(">\\rtt: shows response time to server \n>\\fsend 'filename': sends file to all people in this room")
        print(">\\rename 'nickname': changes your nickname \n>\\exit: leave the room\n")
    elif status[2] == "deny":
        print("duplicate nickname. cannot connect. set other nickname")
        clientSocket.shutdown(SHUT_RDWR)
        clientSocket.close()
        sys.exit()



def fsend(data, nick, filename):
    packet_length = 2000
    end = False
    mod = []
    while not end:
        if len(data) <= packet_length:
            mod.append("10:"+ data) # 10 = starting simbol
            end = True
        else:
            mod.append("10:"+ data[0:packet_length]) # 11 = middle packet
            data = data[packet_length:]
    mod.append("11:" + nick + ":" + filename) # 12 = end simbol
    return mod

def wsend(data, nick, filename, dst):
    packet_length = 2000
    end = False
    mod = []
    while not end:
        if len(data) <= packet_length:
            mod.append("12:"+ dst + ":" + data) # 12 = starting simbol
            end = True
        else:
            mod.append("12:"+ dst + ":"+ data[0:packet_length]) # 12 = middle packet
            data = data[packet_length:]
    mod.append("13:" + dst + ":" + nick + ":" + filename) # 13 = end simbol, 14 = nickname vaild check
    return mod



global startting_time


def send():
    global lock
    global clientSocket
    global startting_time
    global exited
    global nickname
    global program_stop

    connection = True
    #connected
    while connection is True:
        global valid
        global recvnick
        valid = False
        try:
            message = input()
            message = message.split(" ")
            if "\\users" in message:
                lock.acquire()
                clientSocket.send("3:".encode())
                lock.release()

            elif "\\wh" in message:
                message[0] = "4"
                modified_message = ":".join(message)
                lock.acquire()
                clientSocket.send(modified_message.encode())
                lock.release()

            elif "\\exit" in message:
                exited = False
                lock.acquire()
                clientSocket.send("5:".encode())
                lock.release()
                clientSocket.shutdown(SHUT_RDWR)
                clientSocket.close()
                connection = False
                # os._exit()

            elif '\\version' in message:
                lock.acquire()
                clientSocket.send("6:non:non".encode())
                lock.release()

            elif '\\rename' in message:
                my_message = ["7:" + nickname +":" + message[1]]
                modified_message = "".join(my_message)
                lock.acquire()
                clientSocket.send(modified_message.encode())
                lock.release()

            elif '\\rtt' in message:
                lock.acquire()
                startting_time = time.time()
                clientSocket.send("8:".encode())
                lock.release()

            elif '\\fsend' in message:
                lock.acquire()
                try:
                    file = open(message[1], 'r')
                    data = file.read()
                    file.close()
                    modified_message = ("2:" + "non:" + "file " + message[1] + " received from " + nickname)
                    print(nickname)
                    clientSocket.send(modified_message.encode())

                    mod = fsend(data, nickname, message[1])
                    for i in range(len(mod)):
                        clientSocket.send(mod[i].encode())
                        time.sleep(0.05)
                except:
                    print("file does not exist")
                lock.release()

            elif '\\wsend' in message:
                lock.acquire()
                modified_message = ("14:" + nickname + ":" + message[2])
                clientSocket.send(modified_message.encode())
                recvnick = message[2]
                time.sleep(1.0)
                if valid == True:
                    try:
                        file = open(message[1], 'r')
                        data = file.read()
                        file.close()
                        modified_message=("4:" + message[2] + ":&" + message[1]) #2=receiver 1=filename
                        clientSocket.send(modified_message.encode())
                        mod = wsend(data, nickname, message[1], message[2]) # data, myname, filename, destination
                        for i in range(len(mod)):
                            clientSocket.send(mod[i].encode())
                            time.sleep(0.05)
                        lock.release()
                    except:
                        print("file does not exist")
                valid = False


            else:
                modified_message = ("2:" + nickname + ":" + " ".join(message))
                lock.acquire()
                clientSocket.send(modified_message.encode())
                lock.release()


        except EOFError:
            exited = False
            lock.acquire()
            clientSocket.send("5:".encode())
            lock.release()
            clientSocket.shutdown(SHUT_RDWR)
            clientSocket.close()
            connection = False


def listening():
    global clientSocket
    global exited
    global nickname
    global valid
    global recvnick
    f_filedata = []
    w_filedata = []
    exited = True

    try:
        while exited:

            message = clientSocket.recv(2048)
            line = message.decode()
            data = message.decode()
            tmp = data[0:3]
            if tmp == "10:" or tmp == "11:" or tmp == "12:" or tmp == "13:":
                if tmp == "10:" :
                    f_filedata.append(line[3:])

                elif tmp =="12:":
                    w_filedata.append(line[3:])

                elif tmp == "13:":
                    w_filedata = "".join(w_filedata)
                    code = line.split(":")
                    filename = ("wsend_" + code[1] + "_" + nickname + "_" + code[2])
                    filename = "".join(filename)
                    file = open(filename, 'w')
                    file.write(w_filedata)
                    file.close()
                    w_filedata = []

                elif tmp == "11:":
                    f_filedata = "".join(f_filedata)
                    code = line.split(":")
                    filename = ("fsend_" + code[1] + "_" + nickname + "_" + code[2])
                    filename = "".join(filename)
                    file = open(filename, 'w')
                    file.write(f_filedata)
                    file.close()
                    f_filedata = []

            else:
                code = line.split(":")

                if code[0]=="2":
                    if code[1] != "non":
                        print(code[1] + ":" + code[2])
                    else:
                        print(code[2])

                elif code[0] == "3":
                    print("users =" + code[2])

                elif code[0] == "4":
                    string = code[2].replace("[", "")
                    string = string.replace("]", "")
                    string = string.replace("'", "")
                    string = string.replace(",", "")
                    if code[1] != " non ":
                        val = string
                        if val[0] == "&":
                            print(code[1] + " is sending " + val[1:] + " to " + nickname)
                        else:
                            print("whispered by " + code[1] + ": " + string)
                    else:
                        print(code[2])

                elif code[0] =="6":
                    print(code[2])

                elif code[0] == "7":
                    if code[2] == "deny":
                        print("nickname occupied!! please pick another one!!")
                    elif code[2] == "accept":
                        print("nick name changed!!")
                        nickname = code[1]

                elif code[0] == "8":
                    end_time = time.time()
                    print("response time = " +str(end_time-startting_time))

                elif code[0] == "5":
                    print("you have been banned!!")
                    #os._exit()
                    exited = False
                    program_stop = True

                elif code[0] == "14":
                    if code[1] == "valid":
                        valid = True
                    else:
                        print(recvnick + " does not exist!")

    except:
        print("adios~")


if __name__=='__main__':
    global program_stop
    program_stop = False
    parser = argparse.ArgumentParser()
    parser.add_argument('nickname', type=str, help="set your nickname")
    args = parser.parse_args()
    nickname = args.nickname
    # check if the nickname is valid or not
    serverName = '127.0.0.1'
    serverPort = 34677
    connection = False

    clientSocket = socket(AF_INET, SOCK_STREAM)
    #connection part
    while connection == False:
        try:
            nickname_vaild(nickname)

            clientSocket.connect((serverName, serverPort))

            modifying_nickname(nickname)
            connection = True


        except KeyboardInterrupt:
            print("\nadios~~")
            clientSocket.shutdown(SHUT_RDWR)
            clientSocket.close()

    sending = threading.Thread(target=send)
    sending.daemon = True
    sending.start()
    listen = threading.Thread(target=listening())
    listen.daemon = True
    listen.start()

    if program_stop == True:

        sys.exit()






