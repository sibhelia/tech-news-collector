import sqlite3
import time
import os
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Veritabanını oluştur ve gerekli tabloyu oluştur
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
def save_news_to_db(haberler, site_adi):
    try:
        conn = sqlite3.connect('haber.db')  # Veritabanı bağlantısını kur
        cursor = conn.cursor()

        # Haberleri veritabanına kaydet
        for haber in haberler:
            try:
                cursor.execute('''
                    INSERT INTO Haberler (Baslik, Link, Gorsel, Tarih, SiteAdi)
                    VALUES (?, ?, ?, ?, ?)
                ''', (haber["Başlık"], haber["Link"], haber.get("Görsel"), haber["Tarih"], site_adi))
            except sqlite3.IntegrityError:
                # Aynı link varsa atla
                continue

        conn.commit()  # Değişiklikleri kaydet
        print(f"{site_adi} haberleri başarıyla kaydedildi.")
    except sqlite3.Error as e:
        print(f"Veritabanı hatası: {e}")
    finally:
        if conn:
            conn.close()

# Tarayıcıyı başlat
def start_browser():
    options = Options()
    options.add_argument("--start-maximized")  # Tarayıcıyı tam ekran başlat
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

# AA sitesine gidip teknoloji haberlerini çek
def get_technology_news_aa():
    driver = start_browser()
    haberler = []  # Haberleri tutmak için liste
    try:
        driver.get("https://www.aa.com.tr/tr/search/?s=teknoloji")
        print("AA sitesi açıldı.")

        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.col-sm-12.col-md-9.p-sm-0.p-md-3"))
        )

        for _ in range(2):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)

        news_elements = driver.find_elements(By.CSS_SELECTOR, "div.col-sm-12.col-md-9.p-sm-0.p-md-3")
        for news in news_elements:
            try:
                title = news.find_element(By.CSS_SELECTOR, "h4").text
                link = news.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
                date = news.find_element(By.CSS_SELECTOR, "span").text

                haberler.append({
                    "Başlık": title,
                    "Link": link,
                    "Tarih": date,
                    "Görsel": None  # Görsel çekme işlemini atlıyoruz
                })
            except Exception as e:
                print(f"Haber bilgisi çekilemedi: {e}")

    except Exception as e:
        print(f"Hata oluştu: {e}")
    finally:
        driver.quit()

    return haberler

# Ana fonksiyon
def main():
    initialize_database()  # Veritabanını başlat

    while True:  # 600 saniyede bir güncelleme yap
        print("AA teknoloji haberleri çekiliyor...")
        aa_haberler = get_technology_news_aa()  # AA haberlerini al
        if aa_haberler:
            save_news_to_db(aa_haberler, "AA")  # AA haberlerini kaydet

        # Diğer siteler için de benzer fonksiyonlar yazabilirsiniz ve burada çağırabilirsiniz

        time.sleep(3600)  # 1 saat bekle

if __name__ == "__main__":
    main()
