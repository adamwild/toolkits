import select
import socket


class Netcat:
    """Python 'netcat like' module
    ```python
    exemple:
    import time
    # cmd = "nc challenges.france-cybersecurity-challenge.fr 2001"
    cs = Netcat("challenges.france-cybersecurity-challenge.fr", 2001)
    o = cs.read()

    for j in range(16):
        print(j)
        i_max = 18446744073709551616 #100000000000000000000000000
        i_min = 0
        for _ in range(100):
            i = (i_max + i_min)//2
            cs.write_str(str(i))
            time.sleep(0.1)
            o = cs.read()
            if "-1" in o:
                i_max = i
            elif "+1" in o:
                i_min = i
            elif "0" in o:
                break
    ```
    """

    def __init__(self, ip: str, port: int) -> None:
        self.buff = ""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((ip, port))
        self.socket.setblocking(0)

        self.memory = ""

    def read(self, length=4096) -> str:
        """Read `length` bytes off the socket"""
        ready = select.select([self.socket], [], [], 0.1)
        if ready[0]:
            message = self.socket.recv(length).decode()
            self.memory += message
            return message
        return ""

    def read_until(self, data) -> str:
        """Read data into the buffer until we have data"""
        while data not in self.buff:
            self.buff += self.socket.recv(1024)

        pos = self.buff.find(data)
        rval = self.buff[: pos + len(data)]
        self.buff = self.buff[pos + len(data) :]

        return rval

    def write(self, data) -> None:
        self.socket.send(data)

    def write_str(self, data: str) -> None:
        self.memory += data + "\n"
        self.socket.send((data + "\n").encode())

    def close(self) -> None:
        self.socket.close()
