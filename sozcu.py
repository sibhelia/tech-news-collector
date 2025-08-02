import sqlite3
import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime


# SQLite veritabanı oluşturma ve bağlantı
def create_db():
    conn = sqlite3.connect('sozcu.db')
    c = conn.cursor()

    # Tabloyu oluşturma (Eğer tablo yoksa)
    c.execute('''
        CREATE TABLE IF NOT EXISTS news (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            link TEXT,
            image_url TEXT,
            date TEXT
        )
    ''')

    conn.commit()
    conn.close()


# Veritabanına veri ekleme
def insert_into_db(title, link, image_url, date):
    conn = sqlite3.connect('sozcu.db')
    c = conn.cursor()

    c.execute('''
        INSERT INTO news (title, link, image_url, date)
        VALUES (?, ?, ?, ?)
    ''', (title, link, image_url, date))

    conn.commit()
    conn.close()


# Web scraping işlemi
def scrape_and_store():
    url = 'https://www.sozcu.com.tr/bilim-teknoloji'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    articles = soup.find_all('div', class_='col-md-6 col-lg-4 mb-4')

    for article in articles:
        link = article.find('a')['href']
        image_url = article.find('img')['src']
        title = article.find('span', class_='d-block fs-5 fw-semibold text-truncate-2').text.strip()

        # Tarih kısmı genelde makale içinde olmadığı için şu an boş bırakıyoruz
        date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Güncel tarihi ekliyoruz

        # Veriyi veritabanına ekliyoruz
        insert_into_db(title, link, image_url, date)


# Zamanlayıcı ile her 3600 saniyede bir çalıştırma
def schedule_scraping():
    create_db()  # Veritabanını oluşturuyoruz
    while True:
        scrape_and_store()  # Verileri scrape edip veritabanına kaydediyoruz
        print("Veriler kaydedildi. Bir saat sonra tekrar çalışacak.")
        time.sleep(3600)  # 3600 saniye (1 saat) bekleme


# Başlatma
if __name__ == '__main__':
    schedule_scraping()
