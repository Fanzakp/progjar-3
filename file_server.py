from socket import *
import socket
import threading
import logging

from file_protocol import FileProtocol
fp = FileProtocol()


class ProcessTheClient(threading.Thread):
    def __init__(self, connection, address):
        self.connection = connection
        self.address = address
        threading.Thread.__init__(self)

    def run(self):
        buffer = b''
        while True:
            try:
                chunk = self.connection.recv(4096)
                if not chunk:
                    # Client tutup koneksi
                    break
                buffer += chunk

                # Proses semua pesan jika ada terminator \r\n\r\n
                while b'\r\n\r\n' in buffer:
                    idx = buffer.index(b'\r\n\r\n')
                    raw_msg = buffer[:idx]
                    buffer = buffer[idx+4:]  # sisakan sisa buffer

                    data_str = raw_msg.decode()
                    logging.warning(f"string diproses: {data_str}")

                    hasil = fp.proses_string(data_str)
                    hasil = hasil + "\r\n\r\n"
                    self.connection.sendall(hasil.encode())

            except Exception as e:
                logging.error(f"error saat proses client {self.address}: {e}")
                break

        self.connection.close()


class Server(threading.Thread):
    def __init__(self, ipaddress='0.0.0.0', port=8889):
        self.ipinfo = (ipaddress, port)
        self.the_clients = []
        self.my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        threading.Thread.__init__(self)

    def run(self):
        logging.warning(f"server berjalan di ip address {self.ipinfo}")
        self.my_socket.bind(self.ipinfo)
        self.my_socket.listen(5)
        while True:
            self.connection, self.client_address = self.my_socket.accept()
            logging.warning(f"connection from {self.client_address}")

            clt = ProcessTheClient(self.connection, self.client_address)
            clt.start()
            self.the_clients.append(clt)


def main():
    svr = Server(ipaddress='0.0.0.0', port=6666)
    svr.start()


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING)
    main()
