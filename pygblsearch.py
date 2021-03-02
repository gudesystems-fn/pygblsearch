from socket import *
import time


class GblClient(object):
    def __init__(self):
        print("init GBL socket...")
        self.sock = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
        self.sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.sock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

    def search(self, maxwait=3.0, expectedDevs=None):
        # 'GBL' '4' '1' 0x4c
        self.sock.sendto(b'\x47\x42\x4c\x04\x01\x4c', ("255.255.255.255", 50123))

        self.sock.settimeout(1)
        startedTime = time.time()
        numDevices = 0

        while True:
            try:
                data, addr = self.sock.recvfrom(1024)
                gblReply = {
                    'version': int(data[3]),
                    'command': int(data[4]),
                    'mac': ':'.join(f'{c:02x}' for c in data[5:11])
                }
                if (gblReply['version'] == 4) and (gblReply['command'] == 1):
                    numDevices += 1
                    gblReply['bootloader'] = int(data[17:18][0])
                    gblReply['ip'] = '.'.join(f'{c}' for c in data[18:22])
                    print(f"received from {str(addr)}: {gblReply}")

                if expectedDevs is not None and expectedDevs == numDevices:
                    return numDevices

            except timeout:
                pass

            thisTime = time.time()
            if thisTime - startedTime >= maxwait:
                break

        return numDevices

    def __del__(self):
        print("closing GBL socket...")
        self.sock.close()


# run 'search'
if __name__ == '__main__':
    gbl = GblClient()
    # numDevics = gbl.search(maxwait=1.0, expectedDevs=1)
    numDevics = gbl.search()
