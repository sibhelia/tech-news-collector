import sqlite3

def fetch_weather_data():
    # Veritabanına bağlan
    conn = sqlite3.connect('hava.db')
    cursor = conn.cursor()

    # HavaDurumu tablosundaki tüm verileri seç
    cursor.execute("SELECT * FROM HavaDurumu")
    rows = cursor.fetchall()
    conn.close()

    # Verileri terminale yazdır
    print("\n--- Veritabanındaki Hava Durumu Verileri ---\n")
    for row in rows:
        print(f"ID: {row[0]}, Şehir: {row[1]}, Sıcaklık: {row[2]}, İkon: {row[3]}")

if __name__ == '__main__':
    fetch_weather_data()