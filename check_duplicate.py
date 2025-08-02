# check_duplicates.py

import sqlite3

def check_duplicate_entries():
    conn = sqlite3.connect('haber.db')
    cursor = conn.cursor()

    cursor.execute(""" 
        SELECT Link, COUNT(*)
        FROM Haberler
        GROUP BY Link
        HAVING COUNT(*) > 1;
    """)
    duplicates = cursor.fetchall()

    if duplicates:
        print("Aynı linke sahip birden fazla haber bulundu:")
        for row in duplicates:
            print(f"Link: {row[0]}, Sayı: {row[1]}")
    else:
        print("Veritabanında aynı linke sahip haber bulunamadı.")

    conn.close()

# Duplikat kontrolü yap
if __name__ == "__main__":
    check_duplicate_entries()