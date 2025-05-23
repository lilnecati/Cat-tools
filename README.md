# 🐱 Cat Tools - Şifre Kırma Araçları

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-active-success)

<p align="center">
  <img src="https://raw.githubusercontent.com/necati/cat-tools/main/banner.png" alt="Cat Tools Banner" width="600">
</p>

> 🔐 Güvenlik testleri için geliştirilmiş, çok amaçlı şifre kırma aracı.

## 🌟 Özellikler

### 📝 Şifre Listesi Oluşturucu
- 🎯 Kişisel bilgilerden akıllı şifre listesi oluşturma
- 🔄 Gelişmiş kombinasyon algoritmaları
- ⚡ Hızlı ve etkili şifre üretimi
- 🎨 Özel karakterler ve sayılar ile zenginleştirme

### 📦 Arşiv Şifre Kırıcı
- 🗂️ Desteklenen formatlar:
  - ZIP (.zip)
  - RAR (.rar)
  - 7-Zip (.7z)
  - TAR (.tar, .tar.gz, .tar.bz2)
- 🚀 Çoklu thread desteği
- 📊 Gerçek zamanlı ilerleme göstergesi

### 📄 PDF Şifre Kırıcı
- 📱 Modern PDF formatları desteği
- ⚡ Yüksek performanslı şifre deneme
- 🎯 Akıllı şifre analizi

### 📊 Office Şifre Kırıcı
- 📘 Word (.doc, .docx)
- 📊 Excel (.xls, .xlsx)
- 📑 PowerPoint (.ppt, .pptx)
- 🛡️ Modern Office koruma desteği

### 📡 WiFi Handshake Şifre Kırıcı
- 🌐 WPA/WPA2 desteği
- 🔍 Handshake analizi
- ⚡ aircrack-ng entegrasyonu

### 🔒 SSH/FTP Brute Force
- 🌐 SSH ve FTP protokol desteği
- ⚡ Hızlı bağlantı testi
- 🛡️ Güvenli hata yönetimi

## 🚀 Kurulum

### Sistem Gereksinimleri
- Python 3.8 veya üstü
- 64-bit işletim sistemi
- 4GB RAM (önerilen)

### 📥 Adımlar

1. Repoyu klonlayın:
   ```bash
   git clone https://github.com/lilnecati/cat-tools.git
   cd cat-tools
   ```

2. Sanal ortam oluşturun (önerilen):
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   venv\Scripts\activate     # Windows
   ```

3. Gerekli paketleri yükleyin:
   ```bash
   pip install -r requirements.txt
   ```

4. aircrack-ng yükleyin (WiFi modülü için):

   | İşletim Sistemi | Komut |
   |----------------|--------|
   | 🍎 macOS | `brew install aircrack-ng` |
   | 🐧 Linux | `sudo apt-get install aircrack-ng` |
   | 🪟 Windows | [İndirme Sayfası](https://www.aircrack-ng.org/downloads.html) |

## 💻 Kullanım

```bash
python zip_cracker_pro.py
```

### 🎮 Ana Menü
```
    /\___/\  
   (  o o  )  ZIP CRACKER PRO v2.0
   (  =^=  ) 
    (--m-m--)
    
    [ Cat Tools ]

[*] Ana Menü:
1) 📝 Şifre Listesi Oluştur
2) 📦 Arşiv Şifre Kır
3) 📄 PDF Şifre Kır
4) 📊 Office Şifre Kır
5) 📡 WiFi Handshake Şifre Kır
6) 🔒 SSH/FTP Brute Force
7) 🚪 Çıkış
```

## ⚠️ Önemli Not

Bu araç **sadece eğitim amaçlıdır** ve kendi dosyalarınız üzerinde test etmek için tasarlanmıştır. 
- ❌ Başkalarına ait sistemler üzerinde kullanmayın
- ❌ Kötü amaçlı kullanım yasaktır
- ✅ Sadece kendi sistemlerinizde test edin

## 👨‍💻 Geliştirici

Cat Tools, siber güvenlik öğrencileri ve profesyonelleri için geliştirilmiş açık kaynaklı bir projedir.

## 📜 Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Daha fazla bilgi için `LICENSE` dosyasına bakın.

## 🤝 Katkıda Bulunma

1. Bu repoyu fork edin
2. Yeni bir branch oluşturun (`git checkout -b yeni-ozellik`)
3. Değişikliklerinizi commit edin (`git commit -am 'Yeni özellik eklendi'`)
4. Branch'inizi push edin (`git push origin yeni-ozellik`)
5. Pull Request oluşturun

## 🌟 Yıldız Vermeyi Unutmayın!

Eğer bu proje işinize yaradıysa, ⭐️ vermeyi unutmayın! # Cat-tools
