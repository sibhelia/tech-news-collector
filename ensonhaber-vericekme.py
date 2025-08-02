import time
import sqlite3
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


# Veritabanını oluştur veya bağlan
def initialize_database():
    conn = sqlite3.connect('haber.db')
    cursor = conn.cursor()
    # Haberler tablosunu oluştur
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
    conn.close()


# Veritabanına haberleri kaydet
def save_news_to_db(haberler):
    try:
        conn = sqlite3.connect('haber.db')
        cursor = conn.cursor()
        for haber in haberler:
            # Başlık yoksa kaydetme
            if not haber["Baslik"]:
                print(f"Başlık eksik, haber kaydedilmedi: {haber['Link']}")
                continue

            cursor.execute(''' 
                INSERT OR IGNORE INTO Haberler (Baslik, Link, Gorsel, Tarih, SiteAdi)
                VALUES (?, ?, ?, ?, ?)
            ''', (haber["Baslik"], haber["Link"], haber["Gorsel"], haber["Tarih"], haber["SiteAdi"]))
        conn.commit()
        print("Haberler başarıyla kaydedildi.")
    except sqlite3.Error as e:
        print(f"Veritabanı hatası: {e}")
    finally:
        if conn:
            conn.close()


# Tarayıcıyı başlat
def start_browser():
    options = Options()
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")  # Bazı ortamlar için gerekli
    options.add_argument("--disable-dev-shm-usage")  # /dev/shm kullanımı devre dışı bırak
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver


# Ensonhaber Teknoloji haberlerini çek
def get_technology_news():
    driver = start_browser()
    haberler = []

    try:
        driver.get("https://www.ensonhaber.com/arama/?q=teknoloji")
        print("Ensonhaber Teknoloji sayfası açıldı.")

        # Sayfanın tamamen yüklenmesini bekle
        try:
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.item"))
            )
            print("Sayfa tamamen yüklendi.")
        except Exception as e:
            print(f"Sayfa yüklenirken hata: {e}")
            driver.save_screenshot("page_load_error.png")  # Hata durumunda ekran görüntüsü al
            return haberler

        # Haber öğelerini çek
        news_elements = driver.find_elements(By.CSS_SELECTOR, "div.item")
        print(f"{len(news_elements)} haber bulundu.")

        for news in news_elements:
            try:
                baslik = news.find_element(By.CSS_SELECTOR, "h3 a").text  # Başlık
                link = news.find_element(By.CSS_SELECTOR, "h3 a").get_attribute("href")  # Link
                tarih = news.find_element(By.CSS_SELECTOR, "div.details div.column.text-right").text  # Tarih
                gorsel = news.find_element(By.CSS_SELECTOR, "figure.image img").get_attribute("src")  # Görsel

                # Başlık kontrolü: Eğer başlık yoksa bu haberi atla
                if not baslik:
                    print(f"Başlık eksik: {link}")
                    continue

                haberler.append({
                    "Baslik": baslik,
                    "Link": link,
                    "Tarih": tarih,
                    "Gorsel": gorsel,
                    "SiteAdi": "Ensonhaber"  # Site adı sabit olarak "Ensonhaber" girildi
                })
            except Exception as e:
                print(f"Haber bilgisi çekilemedi: {e}")

    except Exception as e:
        print(f"Selenium hatası: {e}")
    finally:
        driver.quit()

    return haberler


# Ana fonksiyon
def main():
    initialize_database()
    while True:
        haberler = get_technology_news()
        if haberler:
            save_news_to_db(haberler)
            print(f"{len(haberler)} haber veritabanına kaydedildi.")
        else:
            print("Haber çekilemedi.")
        time.sleep(3600)  # 1 saat bekle


# Script doğrudan çalıştırıldığında
if __name__ == "__main__":
    main()
