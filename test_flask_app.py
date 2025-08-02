import unittest
import sqlite3
from app import get_news_with_summary, create_db


class TestFlaskApp(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Veritabanını oluştur ve örnek veri ekle
        create_db()
        conn = sqlite3.connect('haber.db')
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO Haberler (Baslik, Link, Gorsel, Tarih, SiteAdi) VALUES 
                          ('Test Haber 1', 'http://example.com/1', '', '2024-12-26', 'Donanım Haber'),
                          ('Test Haber 2', 'http://example.com/2', '', '2024-12-26', 'Başka Site')''')
        conn.commit()
        conn.close()

    def test_get_news_with_summary(self):
        news_with_images, news_without_images = get_news_with_summary()

        # "Donanım Haber" site adı içeren haberlerin çekilmediğini doğrula
        for news in news_with_images:
            self.assertNotIn('Donanım Haber', news)

        for news in news_without_images:
            self.assertNotIn('Donanım Haber', news)


if __name__ == '__main__':
    unittest.main()
