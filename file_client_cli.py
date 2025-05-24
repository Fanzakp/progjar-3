import socket
import json
import base64
import logging
import os

server_address = ('127.0.0.1', 6666)

def send_command(cmd):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(server_address)
    try:
        full_msg = cmd + "\r\n\r\n"
        sock.sendall(full_msg.encode())
        buffer = b''
        while True:
            chunk = sock.recv(4096)
            if not chunk:
                break
            buffer += chunk
            if b'\r\n\r\n' in buffer:
                break
        response_str = buffer.decode()
        response_str = response_str.replace('\r\n\r\n', '')
        return json.loads(response_str)
    finally:
        sock.close()


def remote_list():
    res = send_command('LIST')
    if res['status']=='OK':
        print("Daftar file:")
        for f in res['data']:
            print(f" - {f}")
    else:
        print("ERROR:", res['data'])

def remote_get():
    fn = input("Nama file yang akan di-download: ").strip()
    res = send_command(f'GET {fn}')
    if res['status']=='OK':
        data = base64.b64decode(res['data_file'])
        with open(res['data_namafile'], 'wb') as fp:
            fp.write(data)
        print(f"File '{fn}' berhasil di-download")
    else:
        print("ERROR:", res['data'])

def remote_upload():
    path = input("Path file lokal yang akan di-upload: ").strip()
    if not os.path.isfile(path):
        print("ERROR: File tidak ditemukan.")
        return
    fn = os.path.basename(path)
    with open(path, 'rb') as fp:
        b64 = base64.b64encode(fp.read()).decode()
    res = send_command(f'UPLOAD {fn} {b64}')
    if res['status']=='OK':
        print(res['data'])
    else:
        print("ERROR:", res['data'])

def remote_delete():
    fn = input("Nama file yang akan dihapus: ").strip()
    confirm = input(f"Yakin hapus '{fn}'? (y/n): ").lower()
    if confirm!='y':
        print("Dibatalkan.")
        return
    res = send_command(f'DELETE {fn}')
    if res['status']=='OK':
        print(res['data'])
    else:
        print("ERROR:", res['data'])

def menu():
    while True:
        print("\n=== MENU FILE SERVER ===")
        print("1. List files")
        print("2. Download file")
        print("3. Upload file")
        print("4. Delete file")
        print("5. Exit")
        choice = input("Pilih menu (1-5): ").strip()
        if choice=='1':
            remote_list()
        elif choice=='2':
            remote_get()
        elif choice=='3':
            remote_upload()
        elif choice=='4':
            remote_delete()
        elif choice=='5':
            print("Keluar.")
            break
        else:
            print("Pilihan tidak valid, silakan coba lagi.")

if __name__ == '__main__':
    logging.basicConfig(level=logging.WARNING)
    menu()
