import sqlite3

def fetch_all_news(db_name):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Haberler tablosundaki tüm kayıtları seç
    cursor.execute("SELECT * FROM Haberler")
    news = cursor.fetchall()
    conn.close()

    # Haberleri terminalde göster
    print("\n--- Veritabanındaki Haberler ---\n")
    for row in news:
        print(f"ID: {row[0]}, Başlık: {row[1]}, Link: {row[2]}, Görsel: {row[3]}, Tarih: {row[4]}")

# Veritabanı adını kullanarak tüm haberleri çek ve terminalde göster
fetch_all_news('haber.db')