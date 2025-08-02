import requests
import sqlite3
import time
import xml.etree.ElementTree as ET
import re

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

def webtekno_haberleri_cek():
    url = "https://www.webtekno.com/rss.xml"
    response = requests.get(url)
    root = ET.fromstring(response.content)

    # Yalnızca Webtekno haberlerini sil
    cursor.execute("DELETE FROM Haberler WHERE SiteAdi = 'Webtekno'")
    conn.commit()

    # Haber sayısı sınırlaması
    article_count = 0
    for item in root.findall(".//item"):
        if article_count >= 10:
            break  # 10 haber çekildikten sonra döngüden çık

        try:
            baslik = item.find("title").text.strip() if item.find("title") is not None else None
            link = item.find("link").text.strip() if item.find("link") is not None else None
            description = item.find("description").text if item.find("description") is not None else None
            tarih = item.find("pubDate").text.strip() if item.find("pubDate") is not None else None
            site_adi = "Webtekno"

            # Resim URL'sini description'dan çıkar
            resim = None
            if description:
                match = re.search(r'<img src="(.*?)"', description)
                if match:
                    resim = match.group(1)

            if baslik and link:
                # Haberi veritabanına kaydet
                cursor.execute("""
                INSERT INTO Haberler (Baslik, Link, Gorsel, Tarih, SiteAdi)
                VALUES (?, ?, ?, ?, ?)
                """, (baslik, link, resim, tarih, site_adi))
                conn.commit()
                article_count += 1  # Haber sayısını artır

        except Exception as e:
            print(f"Hata: {e}")

while True:
    webtekno_haberleri_cek()
    print("Webtekno haberleri çekildi ve veritabanına kaydedildi.")
    time.sleep(3600)  # 3600 saniye bekle (1 saat)
