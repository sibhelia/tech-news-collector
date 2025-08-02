import sqlite3
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time

# Veritabanını oluştur veya bağlan
def initialize_database():
    conn = sqlite3.connect('hava.db')
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS HavaDurumu (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            Sehir TEXT NOT NULL,
            Sicaklik INTEGER,
            Icon TEXT
        )
    """)
    conn.commit()
    conn.close()

# Veritabanındaki mevcut hava durumu verisini al
def get_current_weather_from_db(sehir):
    conn = sqlite3.connect('hava.db')
    cursor = conn.cursor()
    cursor.execute("SELECT Sicaklik, Icon FROM HavaDurumu WHERE Sehir = ?", (sehir,))
    current_weather = cursor.fetchone()
    conn.close()
    return current_weather

# Veritabanına hava durumu kaydet
def save_weather_to_db(sehir, sicaklik, icon):
    try:
        conn = sqlite3.connect('hava.db')
        cursor = conn.cursor()

        # Veritabanındaki mevcut veriyi kontrol et
        current_weather = get_current_weather_from_db(sehir)

        # Eğer şehir kaydedilmemişse veya hava durumu değişmişse, veritabanına kaydet
        if current_weather is None or current_weather[0] != sicaklik or current_weather[1] != icon:
            cursor.execute('''
                INSERT INTO HavaDurumu (Sehir, Sicaklik, Icon)
                VALUES (?, ?, ?)
            ''', (sehir, sicaklik, icon))
            conn.commit()
            print(f"{sehir} için hava durumu kaydedildi.")
        else:
            print(f"{sehir} için hava durumu değişmedi, kaydedilmedi.")

    except sqlite3.Error as e:
        print(f"Veritabanı hatası: {e}")
    finally:
        if conn:
            conn.close()

# Selenium tarayıcıyı başlat
def start_browser():
    options = Options()
    options.add_argument("--headless")  # Tarayıcıyı arka planda çalıştırmak için
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

# Hava durumu verilerini çek
def fetch_weather():
    driver = start_browser()
    driver.get("https://www.ntv.com.tr/hava-durumu/istanbul")  # NTV Hava Durumu sayfası

    # Sayfanın tamamen yüklenmesi için biraz bekleyelim
    time.sleep(5)

    try:
        # Şehir adı (Her zaman İstanbul olacak)
        sehir = "İstanbul"

        # Sıcaklık değeri
        sicaklik = driver.find_element(By.CSS_SELECTOR, "span.header-weather-degree").text.strip()

        # Hava durumu ikonu
        icon = driver.find_element(By.CSS_SELECTOR, "img.header-weather-icon").get_attribute("src")

        # Veritabanına kaydet
        save_weather_to_db(sehir, sicaklik, icon)

    except Exception as e:
        print(f"Hata oluştu: {e}")

    driver.quit()

# Ana fonksiyon
def main():
    initialize_database()  # Veritabanını başlat

    while True:  # Sonsuz döngü
        fetch_weather()  # Hava durumu verilerini çek ve kaydet
        print("Bir sonraki güncellemeyi bekliyoruz...")
        time.sleep(3600)  # 60 dakika (3600 saniye) bekle

# Script doğrudan çalıştırıldığında
if __name__ == "__main__":
    main()
