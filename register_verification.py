import smtplib
import random
import string
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import sys
import json
import logging


logging.basicConfig(filename='email_dogrulama_hata.log', level=logging.DEBUG)

class EpostaDogrulama:
    def __init__(self):
        # SMTP sunucu ayarları
        self.smtp_sunucu = "smtp.gmail.com"
        self.smtp_port = 587
        self.gonderen_email = "snakecollections4@gmail.com" 
        self.gonderen_sifre = "epza hubt quuq lxao" 
        
    def dogrulama_kodu_gonder(self, alici_email, kullaniciAdi):
        """Doğrulama kodunu e-posta ile gönderir"""
        try:
            alici_email = alici_email.strip().replace("'", "").replace('"', '')
            logging.info(f"Temizlenmiş e-posta: {alici_email}")
            
            dogrulama_kodu = ''.join(random.choices(string.digits, k=6))
            guncel_yil = datetime.now().year
            
            html_icerik = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
            </head>
            <body style="margin: 0; padding: 0; font-family: Arial, sans-serif;">
                <div style="background-color: #1a1a1a; padding: 20px; text-align: center;">
                    <h1 style="color: rgb(165, 0, 100); margin: 0; font-size: 32px;">GedikFlix</h1>
                </div>
                
                <div style="background: linear-gradient(45deg, rgb(165, 0, 100), rgb(200, 30, 120)); padding: 40px 20px; text-align: center;">
                    <h2 style="color: #fff; margin-bottom: 20px; font-size: 32px;">E-POSTA DOĞRULAMA</h2>
                    <p style="color: #fff; font-size: 20px; margin: 0;">
                        Merhaba <strong>{kullaniciAdi}</strong>
                    </p>
                    <p style="color: rgba(255,255,255,0.9); font-size: 16px;">
                        GedikFlix'e hoş geldiniz! Hesabınızı aktifleştirmek için aşağıdaki doğrulama kodunu kullanın:
                    </p>
                </div>
                
                <div style="padding: 40px 20px; text-align: center;">
                    <div style="display: inline-block; background-color: #f8f9fa; border: 2px dashed rgb(165, 0, 100); padding: 20px 40px; border-radius: 10px;">
                        <h2 style="color: rgb(165, 0, 100); letter-spacing: 8px; margin: 0; font-size: 36px;">{dogrulama_kodu}</h2>
                        <p style="color: #999; margin-top: 10px; font-size: 14px;">Bu kod 10 dakika içinde geçerliliğini yitirecektir</p>
                    </div>
                    
                    <div style="margin-top: 40px; display: flex; justify-content: center; gap: 20px;">
                        <div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px; text-align: center; width: 200px;">
                            <div style="font-size: 32px;">🎬</div>
                            <h3 style="color: #333; margin: 10px 0;">En İyi Filmler</h3>
                            <p style="color: #666; font-size: 14px;">Özenle seçilmiş koleksiyon</p>
                        </div>
                        
                        <div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px; text-align: center; width: 200px;">
                            <div style="font-size: 32px;">📺</div>
                            <h3 style="color: #333; margin: 10px 0;">HD Kalite</h3>
                            <p style="color: #666; font-size: 14px;">Yüksek çözünürlük</p>
                        </div>
                        
                        <div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px; text-align: center; width: 200px;">
                            <div style="font-size: 32px;">🌟</div>
                            <h3 style="color: #333; margin: 10px 0;">Özel İçerikler</h3>
                            <p style="color: #666; font-size: 14px;">Size özel seçkiler</p>
                        </div>
                    </div>
                </div>
                
                <div style="background-color: #fff8f6; border-left: 4px solid rgb(165, 0, 100); padding: 15px; margin: 25px auto; max-width: 500px;">
                    <h4 style="color: #333; margin: 0 0 10px 0;">🔒 Güvenlik Bildirimi</h4>
                    <p style="color: #666; margin: 0; font-size: 14px;">
                        Bu e-postayı siz talep etmediyseniz, lütfen dikkate almayın.
                    </p>
                </div>
                
                <div style="background-color: #f8f9fa; padding: 20px; text-align: center;">
                    <p style="color: #999; font-size: 14px; margin-bottom: 10px;">
                        Bu e-posta <strong>{alici_email}</strong> adresine gönderilmiştir.
                    </p>
                    <p style="color: #999; font-size: 12px; margin: 0;">
                        © {guncel_yil} GedikFlix. Tüm hakları saklıdır.
                    </p>
                </div>
            </body>
            </html>
            """
            
            mesaj = MIMEMultipart('alternative')
            mesaj['Subject'] = "GedikFlix - E-posta Doğrulama Kodunuz"
            mesaj['From'] = self.gonderen_email
            mesaj['To'] = alici_email
            
            mesaj.attach(MIMEText(html_icerik, 'html'))
            
            logging.info("SMTP sunucusuna bağlanılıyor...")
            with smtplib.SMTP(self.smtp_sunucu, self.smtp_port) as sunucu:
                logging.info("SMTP bağlantısı başlatıldı")
                sunucu.starttls()
                logging.info("TLS başlatıldı")
                
                try:
                    sunucu.login(self.gonderen_email, self.gonderen_sifre)
                    logging.info("SMTP login başarılı")
                except Exception as login_hatasi:
                    logging.error(f"SMTP login hatası: {str(login_hatasi)}")
                    return {'basarili': False, 'hata': f"SMTP login hatası: {str(login_hatasi)}"}
                
                try:
                    sunucu.send_message(mesaj)
                    logging.info("E-posta başarıyla gönderildi")
                except Exception as gonderim_hatasi:
                    logging.error(f"E-posta gönderim hatası: {str(gonderim_hatasi)}")
                    return {'basarili': False, 'hata': f"E-posta gönderim hatası: {str(gonderim_hatasi)}"}
            
            return {'basarili': True, 'kod': dogrulama_kodu}
            
        except Exception as e:
            logging.error(f"Genel hata: {str(e)}")
            return {'basarili': False, 'hata': str(e)}

if __name__ == "__main__":
    try:
        logging.info("Script başlatıldı")
        logging.info(f"Argümanlar: {sys.argv}")
        
        if len(sys.argv) != 3:
            hata_mesaji = 'E-posta ve kullanıcı adı gerekli'
            logging.error(hata_mesaji)
            print(json.dumps({'basarili': False, 'hata': hata_mesaji}))
            sys.exit(1)
            
        email = sys.argv[1]
        kullaniciAdi = sys.argv[2]
        
        logging.info(f"E-posta: {email}, Kullanıcı adı: {kullaniciAdi}")
        
        dogrulayici = EpostaDogrulama()
        sonuc = dogrulayici.dogrulama_kodu_gonder(email, kullaniciAdi)
        
        logging.info(f"İşlem sonucu: {sonuc}")
        print(json.dumps(sonuc))
        
    except Exception as e:
        logging.error(f"Ana script hatası: {str(e)}")
        print(json.dumps({'basarili': False, 'hata': str(e)}))