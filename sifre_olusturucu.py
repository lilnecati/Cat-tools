import argparse
import itertools
from datetime import datetime

class SifreOlusturucu:
    def __init__(self, output_file="sifreler.txt"):
        self.output_file = output_file
        self.sifreler = set()
        self.ozel_karakterler = ["!", "@", "#", "$", "%", "&", "*"]
        self.yillar = [str(y) for y in range(1970, datetime.now().year + 1)]
        self.common_ekler = ["123", "1234", "12345", "123456", "1", "2", "01", "02"]

    def veri_topla(self):
        print("\n[*] Kişisel bilgileri girin (boş bırakılabilir):")
        self.ad = input("Ad: ").strip()
        self.soyad = input("Soyad: ").strip()
        self.dogum_tarihi = input("Doğum tarihi (GG.AA.YYYY): ").strip()
        self.onemli_tarih = input("Önemli bir tarih (GG.AA.YYYY): ").strip()
        self.sehir = input("Doğum yeri/yaşadığı şehir: ").strip()
        self.takma_ad = input("Takma ad/nickname: ").strip()
        self.pet = input("Evcil hayvan adı: ").strip()
        self.ekstra_kelimeler = input("Ek anahtar kelimeler (virgülle ayırın): ").strip().split(",")
        self.ekstra_kelimeler = [k.strip() for k in self.ekstra_kelimeler if k.strip()]

    def tarih_manipulasyonlari(self, tarih):
        if not tarih:
            return []
        
        sonuclar = []
        try:
            gun, ay, yil = tarih.split(".")
            sonuclar.extend([gun+ay+yil, gun+ay+yil[2:], gun+ay, yil, yil[2:]])
        except:
            pass
        return sonuclar

    def kelime_manipulasyonlari(self, kelime):
        if not kelime:
            return []
            
        sonuclar = [kelime]
        sonuclar.append(kelime.lower())
        sonuclar.append(kelime.upper())
        sonuclar.append(kelime.capitalize())
        
        leet_map = {'a': '4', 'e': '3', 'i': '1', 'o': '0', 's': '5', 'l': '1'}
        leet_kelime = ''.join(leet_map.get(c.lower(), c) for c in kelime)
        if leet_kelime != kelime:
            sonuclar.append(leet_kelime)
        
        return sonuclar

    def kombinasyon_olustur(self):
        temel_kelimeler = []
        
        if self.ad:
            temel_kelimeler.extend(self.kelime_manipulasyonlari(self.ad))
        if self.soyad:
            temel_kelimeler.extend(self.kelime_manipulasyonlari(self.soyad))
        if self.ad and self.soyad:
            temel_kelimeler.extend(self.kelime_manipulasyonlari(self.ad + self.soyad))
            temel_kelimeler.extend(self.kelime_manipulasyonlari(self.soyad + self.ad))
            temel_kelimeler.extend(self.kelime_manipulasyonlari(self.ad[:1] + self.soyad))
            temel_kelimeler.extend(self.kelime_manipulasyonlari(self.ad + self.soyad[:1]))
        
        if self.dogum_tarihi:
            temel_kelimeler.extend(self.tarih_manipulasyonlari(self.dogum_tarihi))
        if self.onemli_tarih:
            temel_kelimeler.extend(self.tarih_manipulasyonlari(self.onemli_tarih))
        if self.takma_ad:
            temel_kelimeler.extend(self.kelime_manipulasyonlari(self.takma_ad))
        if self.sehir:
            temel_kelimeler.extend(self.kelime_manipulasyonlari(self.sehir))
        if self.pet:
            temel_kelimeler.extend(self.kelime_manipulasyonlari(self.pet))
        
        for kelime in self.ekstra_kelimeler:
            temel_kelimeler.extend(self.kelime_manipulasyonlari(kelime))
        
        temel_kelimeler = [k for k in temel_kelimeler if k]
        temel_kelimeler = list(set(temel_kelimeler))
        
        for kelime in temel_kelimeler:
            self.sifreler.add(kelime)
        
        for kelime in temel_kelimeler:
            for yil in self.yillar:
                self.sifreler.add(kelime + yil)
                self.sifreler.add(yil + kelime)
        
        for kelime in temel_kelimeler:
            for ek in self.common_ekler:
                self.sifreler.add(kelime + ek)
        
        for kelime in temel_kelimeler:
            for karakter in self.ozel_karakterler:
                self.sifreler.add(kelime + karakter)
                self.sifreler.add(karakter + kelime)
                
                for ek in self.common_ekler:
                    self.sifreler.add(kelime + karakter + ek)
                    self.sifreler.add(kelime + ek + karakter)
        
        self.sifreler = set(sifre for sifre in self.sifreler if len(sifre) >= 6)

    def sifreleri_kaydet(self):
        try:
            with open(self.output_file, "w", encoding="utf-8") as f:
                for sifre in sorted(self.sifreler):
                    f.write(f"{sifre}\n")
            print(f"\n[+] Toplam {len(self.sifreler)} adet potansiyel şifre oluşturuldu")
            print(f"[+] Şifreler '{self.output_file}' dosyasına kaydedildi")
        except Exception as e:
            print(f"\n[!] Hata: iifreler kaydedilemedi - {str(e)}")

    def olustur(self):
        print("\n[*] Şifre oluşturucu başlatıldı")
        self.veri_topla()
        print("\n[*] Şifreler oluşturuluyor...")
        self.kombinasyon_olustur()
        self.sifreleri_kaydet()


def main():
    parser = argparse.ArgumentParser(description="kişisel Bilgilerden Şifre Oluşturucu")
    parser.add_argument("-o", "--output", default="sifreler.txt", help="çıktı dosyası adı")
    
    args = parser.parse_args()
    
    olusturucu = SifreOlusturucu(args.output)
    olusturucu.olustur()


if __name__ == "__main__":
    main() 