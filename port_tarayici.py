import socket
from datetime import datetime
import argparse
from concurrent.futures import ThreadPoolExecutor


class PortTarayici:
    def __init__(self, hedef, baslangic_port=1, bitis_port=1025, thread_sayisi=100):
        self.hedef = hedef
        self.baslangic_port = baslangic_port
        self.bitis_port = bitis_port
        self.thread_sayisi = thread_sayisi
        self.acik_portlar = []

    def port_tara(self, port):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(1)
                sonuc = sock.connect_ex((self.hedef, port))
                if sonuc == 0:
                    servis = self.servis_tespit(port)
                    self.acik_portlar.append((port, servis))
                    print(f"[+] Port {port} açık - Servis: {servis}")
        except Exception as e:
            print(f"Hata: {port} - {str(e)}")

    def servis_tespit(self, port):
        bilinen_portlar = {
            21: "FTP",
            22: "SSH",
            25: "SMTP",
            80: "HTTP",
        }
        return bilinen_portlar.get(port, "bilinmeyen")

    def tarama_baslat(self):
        print(f"\n[*] hedef: {self.hedef}")
        print(f"[*] tarama başlangıç zamanı: {datetime.now()}\n")

        with ThreadPoolExecutor(max_workers=self.thread_sayisi) as executor:
            executor.map(
                self.port_tara, range(self.baslangic_port, self.bitis_port + 1)
            )

        print(f"\n[*] tarama tamamlandı: {datetime.now()}")
        print(f"[*] toplam {len(self.acik_portlar)} açık port bulundu")


def main():
    parser = argparse.ArgumentParser(description="gelişmiş Port Tarayıcı")
    parser.add_argument("-t", "--target", required=True, help="Hedef IP adresi")
    parser.add_argument(
        "-p", "--ports", default="1-1025", help=")"
    )
    parser.add_argument("-w", "--workers", type=int, default=100, help="Thread sayısı")

    args = parser.parse_args()

    baslangic_port, bitis_port = map(int, args.ports.split("-"))

    tarayici = PortTarayici(args.target, baslangic_port, bitis_port, args.workers)
    tarayici.tarama_baslat()


if __name__ == "__main__":
    main()
