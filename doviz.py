from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sqlite3
from datetime import datetime
import time

# Veritabanı bağlantısı oluştur
conn = sqlite3.connect('doviz_altin_verileri.db')
cursor = conn.cursor()

# Tablo oluştur (eğer yoksa)
cursor.execute('''
    CREATE TABLE IF NOT EXISTS doviz_altin (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tarih TEXT,
        dolar TEXT,
        euro TEXT,
        altin TEXT
    )
''')
conn.commit()

# WebDriver'ı başlat
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # Tarayıcıyı arka planda çalıştır
driver = webdriver.Chrome(options=options)

try:
    while True:
        driver.get("https://www.cumhuriyet.com.tr")
        wait = WebDriverWait(driver, 30)  # Bekleme süresini artırdık

        try:
            # Dolar verisini çek
            dolar_element = wait.until(EC.presence_of_element_located(
                (By.XPATH, "/html/body/nav[1]/div[2]/div[1]/div[2]/div/ul/li[2]/span[2]")
            ))
            dolar = dolar_element.text if dolar_element else "Bulunamadı"
            print(f"Dolar: {dolar}")

            # Euro verisini çek
            euro_element = wait.until(EC.presence_of_element_located(
                (By.XPATH, "/html/body/nav[1]/div[2]/div[1]/div[2]/div/ul/li[3]/span[2]")
            ))
            euro = euro_element.text if euro_element else "Bulunamadı"
            print(f"Euro: {euro}")

            # Altın verisini çek
            altin_element = wait.until(EC.presence_of_element_located(
                (By.XPATH, "/html/body/nav[1]/div[2]/div[1]/div[2]/div/ul/li[4]/span[2]")
            ))
            altin = altin_element.text if altin_element else "Bulunamadı"
            print(f"Altın: {altin}")

            # Tarih ekleyerek veritabanına kaydet
            tarih = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            # Veritabanında mevcut olan son veriyi kontrol et
            cursor.execute('''SELECT * FROM doviz_altin ORDER BY id DESC LIMIT 1''')
            son_veri = cursor.fetchone()

            # Eğer veritabanında hiç veri yoksa ya da dolar, euro, altın verileri farklıysa ekle
            if son_veri is None or (son_veri[1] != dolar or son_veri[2] != euro or son_veri[3] != altin):
                # Yeni veriyi ekle
                cursor.execute('''
                    INSERT INTO doviz_altin (tarih, dolar, euro, altin)
                    VALUES (?, ?, ?, ?)
                ''', (tarih, dolar, euro, altin))
                conn.commit()

                print(f"🔄 Veriler güncellendi!")
                print(f"Tarih: {tarih}\nDolar: {dolar}\nEuro: {euro}\nAltın: {altin}")
            else:
                print("🔴 Veriler değişmedi, yeni bir satır eklenmedi.")

        except Exception as e:
            print(f"❌ Veri çekme hatası: {e}")
            driver.save_screenshot("veri_cekme_hatasi.png")  # Hata durumunda ekran görüntüsü al

        # 3600 saniye bekle (1 saat)
        time.sleep(3600)

except KeyboardInterrupt:
    print("🛑 Program manuel olarak durduruldu.")

except Exception as e:
    print(f"❌ Genel hata: {e}")
    driver.save_screenshot("genel_hata.png")  # Genel hata durumunda ekran görüntüsü al

finally:
    driver.quit()
    conn.close()
