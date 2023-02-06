import select
import socket, struct, random, sys, time
import threading


UDP_PORT = int(sys.argv[1])

all_discovered = 0

def recv_thread():

    global all_discovered

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    sock.bind(('', UDP_PORT))

    mreq = struct.pack("4sl", socket.inet_aton('224.1.1.1'), socket.INADDR_ANY)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    while True:

        read_sockets, write_sockets, error_sockets = select.select([sock], [], [], 0)
        if sock in read_sockets:
            q, adress = sock.recvfrom(4)
            n = struct.unpack('!I', q)[0]
            q, adress = sock.recvfrom(n)
            s = q.decode('ascii')

            print('\n', s, '\n')
            all_discovered = int(s[0])
            if all_discovered == 5:
                print("all treasures discovered")
                break


if __name__ == '__main__':
    try:
        s = socket.create_connection(('localhost', 1234))
    except socket.error as msg:
        print("Error: ",msg.strerror)
        exit(-1)

    client_port = int(sys.argv[1])
    print(client_port)
    s.send(struct.pack('!I', client_port))

    threading.Thread(target=recv_thread, args=()).start()

    data=s.recv(1024)
    print(data.decode('ascii'))

    while all_discovered<5:
        row=int(input("Row: "))
        s.send(struct.pack('!I', row))

        col = int(input("Col: "))
        s.send(struct.pack('!I', col))

        n = s.recv(4)
        n = int(n.decode('utf-8'))

        if n==-1:
            print("invalid pos")
        elif n==0:
            print("no treasure")
        elif n==1:
            print("You`ve discovered a treasure")
        elif n==2:
            print("treasure already discovered")
        elif n==10:
            print("all treasures were discovered")
            break

    s.close()