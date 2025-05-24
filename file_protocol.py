import json
import logging
import shlex

from file_interface import FileInterface

"""
* class FileProtocol bertugas untuk memproses 
data yang masuk, dan menerjemahkannya apakah sesuai dengan
protokol/aturan yang dibuat

* data yang masuk dari client adalah dalam bentuk bytes yang 
pada akhirnya akan diproses dalam bentuk string

* class FileProtocol akan memproses data yang masuk dalam bentuk
string
"""

class FileProtocol:
    def __init__(self):
        self.file = FileInterface()

    def proses_string(self, string_datamasuk=''):
        logging.warning(f"string diproses: {string_datamasuk}")

        # Cek apakah ini perintah upload
        if string_datamasuk.upper().startswith('UPLOAD '):
            # Pisahkan menjadi 3 bagian: command, nama_file, isi_file_base64 (bisa mengandung spasi)
            parts = string_datamasuk.split(' ', 2)
            if len(parts) < 3:
                return json.dumps(dict(status='ERROR', data='parameter upload kurang'))
            c_request = parts[0].lower()
            nama_file = parts[1]
            isi_file = parts[2]
            params = [nama_file, isi_file]
        else:
            # Untuk command lain, split normal dengan shlex (untuk dukung nama file tanpa spasi juga)
            tokens = shlex.split(string_datamasuk)
            if not tokens:
                return json.dumps(dict(status='ERROR', data='request kosong'))
            c_request = tokens[0].lower()
            params = tokens[1:]

        logging.warning(f"memproses request: {c_request}")

        try:
            handler = getattr(self.file, c_request)
            return json.dumps(handler(params))
        except AttributeError:
            return json.dumps(dict(status='ERROR', data='request tidak dikenali'))




if __name__ == '__main__':
    fp = FileProtocol()
    print(fp.proses_string("LIST"))
    print(fp.proses_string("GET pokijan.jpg"))
    # contoh upload:
    dummy_b64 = "cHJvZ2phciBrZWxhc...=="  # contoh base64 string pendek
    print(fp.proses_string(f"UPLOAD progjar_kelas_c.txt {dummy_b64}"))
