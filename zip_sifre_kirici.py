import argparse
import os
import subprocess
import time
import sys
from concurrent.futures import ThreadPoolExecutor
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


class ZipSifreKirici:
    def __init__(self, zip_dosyasi, sifre_dosyasi="sifreler.txt", thread_sayisi=5, cikti_dosyasi=None, verbose=False):
        self.zip_dosyasi = zip_dosyasi
        self.sifre_dosyasi = sifre_dosyasi
        self.thread_sayisi = thread_sayisi
        self.cikti_dosyasi = cikti_dosyasi
        self.basarili_sifre = None
        self.denenen_sayisi = 0
        self.toplam_sifre = 0
        self.verbose = verbose
        self.lock = __import__('threading').Lock()
    
    def sifreler_oku(self):
        try:
            with open(self.sifre_dosyasi, "r", encoding="utf-8") as f:
                sifreler = [line.strip() for line in f if line.strip()]
                self.toplam_sifre = len(sifreler)
                return sifreler
        except Exception as e:
            print(f"{RenkliYazi.KIRMIZI}[!] Hata: Şifre dosyası okunamadı: {str(e)}{RenkliYazi.SON}")
            sys.exit(1)
    
    def zip_sifre_dene(self, sifre):
        if self.basarili_sifre:  
            return
        
        with self.lock:
            self.denenen_sayisi += 1
            if not self.verbose:
                yuzde = min(int(self.denenen_sayisi / self.toplam_sifre * 100), 100)
                print(f"{RenkliYazi.BEYAZ}[*] İlerleme: %{yuzde} | Deneniyor: {sifre} [{self.denenen_sayisi}/{self.toplam_sifre}]          {RenkliYazi.SON}", end="\r")
            else:
                print(f"{RenkliYazi.BEYAZ}[*] Deneniyor ({self.denenen_sayisi}/{self.toplam_sifre}): {sifre}{RenkliYazi.SON}")
        
        try:
            temp_dir = "/tmp/zip_extract_temp"
            os.makedirs(temp_dir, exist_ok=True)
            
            cmd = ["unzip", "-qq", "-P", sifre, self.zip_dosyasi, "-d", temp_dir]
            
            result = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            if result.returncode == 0:
                with self.lock:
                    self.basarili_sifre = sifre
                    print(f"\n{RenkliYazi.YESIL}{RenkliYazi.KALIN}[+] Şifre bulundu! {sifre}{RenkliYazi.SON}")
                    print(f"{RenkliYazi.YESIL}[+] Toplam denenen şifre: {self.denenen_sayisi}/{self.toplam_sifre}{RenkliYazi.SON}")
                    
                    if self.cikti_dosyasi:
                        with open(self.cikti_dosyasi, "a") as f:
                            f.write(f"ZIP dosyası: {self.zip_dosyasi}\n")
                            f.write(f"Şifre: {sifre}\n")
                            f.write(f"Tarih: {datetime.now()}\n")
                            f.write(f"Denenen şifre sayısı: {self.denenen_sayisi}/{self.toplam_sifre}\n")
                            f.write("-" * 40 + "\n")
                    
                subprocess.run(["rm", "-rf", temp_dir], 
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return True
                
            if self.verbose:
                with self.lock:
                    print(f"{RenkliYazi.KIRMIZI}[-] Başarısız: {sifre}{RenkliYazi.SON}")
                
            subprocess.run(["rm", "-rf", temp_dir], 
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return False
            
        except Exception as e:
            if self.verbose:
                with self.lock:
                    print(f"{RenkliYazi.KIRMIZI}[!] Hata: {sifre} - {str(e)}{RenkliYazi.SON}")
            return False
    
    def dosya_kontrol(self):
        if not os.path.exists(self.zip_dosyasi):
            print(f"{RenkliYazi.KIRMIZI}[!] Hata: {self.zip_dosyasi} dosyası bulunamadı!{RenkliYazi.SON}")
            return False
        
        try:
            result = subprocess.run(["file", self.zip_dosyasi], 
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
                                   universal_newlines=True)
            
            if "Zip archive data" not in result.stdout:
                print(f"{RenkliYazi.KIRMIZI}[!] Uyarı: {self.zip_dosyasi} bir ZIP arşivi olmayabilir!{RenkliYazi.SON}")
                print(f"{RenkliYazi.SARI}[*] Dosya türü: {result.stdout.strip()}{RenkliYazi.SON}")
        except:
            pass
            
        return True
    
    def kirma_baslat(self):
        if not self.dosya_kontrol():
            return
            
        sifreler = self.sifreler_oku()
        
        print(f"\n{RenkliYazi.MAVI}[*] Hedef ZIP: {self.zip_dosyasi}")
        print(f"[*] Toplam şifre sayısı: {len(sifreler)}")
        print(f"[*] Thread sayısı: {self.thread_sayisi}")
        print(f"[*] Ayrıntılı mod: {'Açık' if self.verbose else 'Kapalı'}{RenkliYazi.SON}")
        
        baslangic_zamani = time.time()
        print(f"\n{RenkliYazi.SARI}[*] ZIP şifre kırma başlatıldı...{RenkliYazi.SON}")
        
        with ThreadPoolExecutor(max_workers=self.thread_sayisi) as executor:
            for _ in executor.map(self.zip_sifre_dene, sifreler):
                if self.basarili_sifre:
                    break
        
        bitis_zamani = time.time()
        gecen_sure = bitis_zamani - baslangic_zamani
        
        print(f"\n{RenkliYazi.TURKUAZ}[*] deneme tamamlandı")
        print(f"[*] denenen şifre sayısı: {self.denenen_sayisi}/{self.toplam_sifre}")
        print(f"[*] geçen süre: {gecen_sure:.2f} saniye{RenkliYazi.SON}")
        
        if not self.basarili_sifre:
            print(f"{RenkliYazi.KIRMIZI}[!] Doğru şifre bulunamadı.{RenkliYazi.SON}")
        else:
            print(f"{RenkliYazi.YESIL}[+] Bulunan şifre: {self.basarili_sifre}{RenkliYazi.SON}")


def main():
    parser = argparse.ArgumentParser(description="ZIP Şifre Kırıcı")
    parser.add_argument("-z", "--zip", required=True, help="Şifresi kırılacak ZIP dosyasının yolu")
    parser.add_argument("-w", "--wordlist", default="sifreler.txt", help="Şifre listesi dosyası")
    parser.add_argument("-t", "--threads", type=int, default=5, help="Eşzamanlı thread sayısı")
    parser.add_argument("-o", "--output", help="Sonucun kaydedileceği dosya")
    parser.add_argument("-v", "--verbose", action="store_true", help="Ayrıntılı çıktılar göster")
    
    args = parser.parse_args()
    
    try:
        kirici = ZipSifreKirici(
            zip_dosyasi=args.zip,
            sifre_dosyasi=args.wordlist,
            thread_sayisi=args.threads,
            cikti_dosyasi=args.output,
            verbose=args.verbose
        )
        kirici.kirma_baslat()
    except KeyboardInterrupt:
        print(f"\n{RenkliYazi.KIRMIZI}[!] Kullanıcı tarafından sonlandırıldı.{RenkliYazi.SON}")
    except Exception as e:
        print(f"\n{RenkliYazi.KIRMIZI}[!] Hata: {str(e)}{RenkliYazi.SON}")


if __name__ == "__main__":
    print(f"{RenkliYazi.KALIN}{RenkliYazi.SARI}")
    print("┌─┐┬┌─┐  ┌─┐┬┌─┐┬─┐┌─┐  ┬┌─┬┬─┐┬┌─┐┬")
    print("└─┐│├─┘  └─┐│├┤ ├┬┘├┤   ├┴┐│├┬┘││  │")
    print("└─┘┴┴    └─┘┴└  ┴└─└─┘  ┴ ┴┴┴└─┴└─┘o")
    print(f"{RenkliYazi.SON}")
    
    main() 