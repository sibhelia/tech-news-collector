import requests
from bs4 import BeautifulSoup
import sqlite3
from datetime import datetime
import time


# Fonksiyon: Haberleri Çek ve Kaydet
def fetch_and_save_news():
    # Veritabanı bağlantısı oluştur
    conn = sqlite3.connect('haber.db')
    cursor = conn.cursor()

    # Haberler tablosunu oluştur
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

    # Web sayfasından veri çekme
    url = "https://www.tgrthaber.com/teknoloji"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    # Haberleri bulma
    articles = soup.find_all('a', class_='sidebar-news__item')

    for article in articles:
        baslik = article.get('title', 'Başlık bulunamadı')
        link = article.get('href', 'Bağlantı bulunamadı')

        img_tag = article.find('img')
        if img_tag:
            gorsel = img_tag.get('src') or img_tag.get('data-src') or 'Görsel bulunamadı'
        else:
            gorsel = 'Görsel bulunamadı'

        tarih = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Mevcut tarih ve saat
        site_adi = 'TGRT Haber'

        # Haber daha önce eklenmiş mi kontrol et
        cursor.execute('SELECT COUNT(*) FROM Haberler WHERE Link = ?', (link,))
        if cursor.fetchone()[0] > 0:
            print(f"🔄 Zaten kayıtlı: {link}")
            continue  # Bir sonraki habere geç

        # Haberi veritabanına ekle
        cursor.execute('''
            INSERT INTO Haberler (Baslik, Link, Gorsel, Tarih, SiteAdi)
            VALUES (?, ?, ?, ?, ?)
        ''', (baslik, link, gorsel, tarih, site_adi))
        print(f"✅ Yeni haber eklendi: {baslik}")

    conn.commit()
    conn.close()
    print(f"{tarih} - Tüm yeni veriler başarıyla çekildi ve haber.db'ye kaydedildi.")


# Ana Döngü: 3600 saniyede bir çalıştır
while True:
    fetch_and_save_news()
    print("Bir sonraki veri çekme işlemi 3600 saniye sonra gerçekleşecek.\n")
    time.sleep(3600)  # 3600 saniye (1 saat) bekle

