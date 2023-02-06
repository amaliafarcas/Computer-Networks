import socket
import threading
import struct
import random
import time

mylock = threading.Lock()
e = threading.Event()
e.clear()
threads = []
client_count=0
clients = dict()
discovered_treasures = 0
treasures_list = []

N = 10
matrix_data = [[0] * N for i in range(N)] #-1 - no treasure,  1 - treasure, 0 - discovered treasure

def send_thread(cs):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 16)

    global discovered_treasures

    while True:
        time.sleep(5)
        s = str(discovered_treasures) + " treaures discovered from 5"

        sock.sendto(struct.pack('!I', len(s)), ('127.0.0.1', clients[cs][1]))
        sock.sendto(bytes(s, 'ascii'), ('127.0.0.1', clients[cs][1]))
        if discovered_treasures == 5:
            print("all treasures were discovered")
            break


def init_matrix_data():
    for i in range(N):
        for j in range(N):
            matrix_data[i][j] = -1

def empty_squares():
    """
    Return a list of all non-played squares
    :return:
    """
    result = []
    for i in range(N):
        for j in range(N):
            if matrix_data[i][j] == -1:
                result.append((i, j))
    return result


def choose_random():
    empty_list = empty_squares()
    square = random.choice(empty_list)
    print("random", square)
    row = square[0]
    col = square[1]
    matrix_data[row][col] = 1
    treasures_list.append((row, col))


def worker(cs):
    global mylock, e, matrix_data, clients, client_count, discovered_treasures

    my_idcount = client_count
    print('client #', client_count, 'from ', cs.getpeername(), cs)
    message = 'Hello client #' + str(client_count) + '!'
    cs.sendall(bytes(message, 'ascii'))

    try:

        while discovered_treasures < 5:
            row = cs.recv(4)
            row = struct.unpack('!I', row)[0]
#i -signed integer
            col = cs.recv(4)
            col = struct.unpack('!I', col)[0]

            if row < 0 or row > 9 or col < 0 or col > 9:
                cs.send(str(-1).encode('utf-8'))

            else:
                if matrix_data[row][col] == -1:
                    cs.send(str(0).encode('utf-8'))

                elif matrix_data[row][col] == 1:
                    cs.send(str(1).encode('utf-8'))

                    mylock.acquire()
                    matrix_data[row][col] = 0
                    discovered_treasures+=1
                    mylock.release()

                elif matrix_data[row][col] == 0:
                    cs.send(str(2).encode('utf-8'))

    except socket.error as msg:
        print('Error:', msg.strerror)

    cs.close()


if __name__ == '__main__':
    clients = dict() # key: tcp socket - used to send the list of clients ,
                     # values: (udp_port - udp communication happens here, ip address - communication)
    init_matrix_data()
    for i in range(int(N/2)):
        choose_random()

    rdv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    rdv.bind(('127.0.0.1', 1234))
    rdv.listen(7)
    while True:
        # we have a new client connection
        cs, addr = rdv.accept()
        print('new client from addr: ', addr)
        c_udpp = cs.recv(4)
        c_udpp = struct.unpack('!I', c_udpp)[0]
        clients[cs] = (addr[0], c_udpp)

        t1 = threading.Thread(target=worker, args=(cs,))
        threads.append(t1)
        client_count += 1
        t1.start()
        threading.Thread(target=send_thread, args=(cs,)).start()



