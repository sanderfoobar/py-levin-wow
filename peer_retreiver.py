import sys
import socket
from levin.section import Section
from levin.bucket import Bucket
from levin.ctypes import *
from levin.constants import P2P_COMMANDS, LEVIN_SIGNATURE

args = sys.argv
if len(args) != 3:
    print('./%s ip port')
    sys.exit()

host, ip = args[1], int(args[2])

try:
    sock = socket.socket()
    sock.connect((host, ip))
except:
    sys.stderr.write("unable to connect to %s:%d\n" % (host, ip))
    sys.exit()

bucket = Bucket.create_handshake_request()

head = bucket.header()
body = bucket.payload()

sock.send(head)
sock.send(body)

# print(">> sent packet \'%s\'" % P2P_COMMANDS[bucket.command])

buckets = []

while 1:
    buffer = sock.recv(8)
    if not buffer:
        sys.stderr.write("Invalid response; exiting\n")
        break

    if not buffer.startswith(bytes(LEVIN_SIGNATURE)):
        sys.stderr.write("Invalid response; exiting\n")
        break

    bucket = Bucket.from_buffer(signature=buffer, sock=sock)
    buckets.append(bucket)

    if bucket.command == 1001:
        peers = bucket.get_peers() or []

        for peer in peers:
            try:
                print('%s:%d' % (peer['ip'].ip, peer['port'].value))
            except:
                pass

        sock.close()
        break
