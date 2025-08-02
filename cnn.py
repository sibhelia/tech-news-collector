import requests
from bs4 import BeautifulSoup
import sqlite3
import time

# Veritabanı bağlantısı oluştur
conn = sqlite3.connect("haber.db")
cursor = conn.cursor()

# Haber tablosunu oluştur
cursor.execute("""
CREATE TABLE IF NOT EXISTS Haberler (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    Baslik TEXT NOT NULL,
    Link TEXT NOT NULL UNIQUE,
    Gorsel TEXT,
    Tarih TEXT,
    SiteAdi TEXT NOT NULL
)
""")
conn.commit()

def haberleri_cek():
    url = "https://www.cnnturk.com/teknoloji-haberleri/"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    haber_listesi = soup.find_all("a", class_="card card-news")

    for haber in haber_listesi:
        try:
            baslik = haber.find("h3", class_="card-title").text.strip() if haber.find("h3", class_="card-title") else None
            link = "https://www.cnnturk.com" + haber["href"] if haber.get("href") else None
            resim = haber.find("img")["data-src"] if haber.find("img") and haber.find("img").get("data-src") else None
            tarih = None  # Tarih bu HTML yapısında olmadığı için None bırakıldı
            site_adi = "CNN Türk"

            if baslik and link:
                # Haberin zaten eklenip eklenmediğini kontrol et
                cursor.execute("SELECT COUNT(*) FROM Haberler WHERE Link = ?", (link,))
                exists = cursor.fetchone()[0]

                if exists == 0:
                    # Haberleri konsola yazdır (kontrol amaçlı)
                    print(f"Başlık: {baslik}")
                    print(f"Link: {link}")
                    print(f"Resim: {resim}")
                    print(f"Tarih: {tarih}")
                    print(f"Site Adı: {site_adi}")
                    print("---------------------------")

                    # Veriyi veritabanına kaydet
                    cursor.execute("""
                    INSERT INTO Haberler (Baslik, Link, Gorsel, Tarih, SiteAdi)
                    VALUES (?, ?, ?, ?, ?)
                    """, (baslik, link, resim, tarih, site_adi))
                    conn.commit()
                else:
                    print(f"Haber zaten mevcut: {baslik} - {link}")

        except Exception as e:
            print(f"Hata: {e}")

while True:
    haberleri_cek()
    print("Haberler çekildi ve veritabanına kaydedildi.")
    time.sleep(3600)  # 3600 saniye bekle (1 saat)
