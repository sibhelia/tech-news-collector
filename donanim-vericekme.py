import requests
from bs4 import BeautifulSoup
import sqlite3
import datetime
import time

# SQLite Veritabanı Ayarı
db_name = "haber.db"
conn = sqlite3.connect(db_name)
cursor = conn.cursor()

# Tabloyu Oluştur
cursor.execute('''
CREATE TABLE IF NOT EXISTS Haberler (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    Baslik TEXT NOT NULL,
    Link TEXT NOT NULL UNIQUE,
    Gorsel TEXT,
    Tarih TEXT,
    SiteAdi TEXT NOT NULL
)
''')
conn.commit()

# Haberleri Çek ve Kaydet Fonksiyonu
def fetch_and_save_news():
    try:
        # DonanımHaber verilerini sil
        cursor.execute('DELETE FROM Haberler WHERE SiteAdi = "DonanımHaber"')
        conn.commit()
        print("Eski DonanımHaber verileri silindi.")

        # Web Sayfasını Çek
        url = "https://www.donanimhaber.com/"
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")

        # Verileri Çek ve İşle
        articles = soup.find_all("article", class_="medya")  # Haberleri temsil eden 'article' etiketlerini seç
        print(f"Toplam {len(articles)} haber bulundu.")

        for article in articles:
            try:
                # Başlık
                baslik = article.find("a", class_="baslik").get_text(strip=True)

                # Link
                link = article.find("a")["href"]
                if not link.startswith("http"):
                    link = "https://www.donanimhaber.com" + link

                # Görsel
                img_tag = article.find("img")
                if img_tag and "src" in img_tag.attrs:
                    gorsel = img_tag["src"]
                elif img_tag and "data-src" in img_tag.attrs:
                    gorsel = img_tag["data-src"]
                else:
                    gorsel = None

                # Tarih
                tarih = datetime.datetime.now().strftime("%Y-%m-%d")

                # Site Adı
                site_adi = "DonanımHaber"

                # Veritabanına Kaydet
                cursor.execute('''
                INSERT INTO Haberler (Baslik, Link, Gorsel, Tarih, SiteAdi) 
                VALUES (?, ?, ?, ?, ?)
                ''', (baslik, link, gorsel, tarih, site_adi))
                conn.commit()
                print(f"Haber kaydedildi: {baslik}")

            except Exception as e:
                print(f"Veri çekme hatası: {e}")

    except Exception as e:
        print(f"Genel hata: {e}")


# Ana Döngü: 3600 saniyede bir çalıştır
try:
    while True:
        fetch_and_save_news()
        print("Bir sonraki veri çekme işlemi 3600 saniye sonra gerçekleşecek.\n")
        time.sleep(3600)  # 3600 saniye (1 saat) bekle

except KeyboardInterrupt:
    print("Program kullanıcı tarafından durduruldu.")

except Exception as e:
    print(f"Beklenmeyen bir hata oluştu: {e}")

finally:
    conn.close()
    print("Veritabanı bağlantısı kapatıldı.")
