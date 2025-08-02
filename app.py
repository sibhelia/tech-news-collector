from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import sqlite3
import hashlib
import re
from datetime import timedelta

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Güvenlik anahtarı, değiştirin


@app.before_request
def before_request():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=30)
    session.modified = True


# Kullanıcı veritabanı bağlantısını oluştur
def create_user_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    # Users tablosu oluştur
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL)''')
    # Likes tablosu oluştur
    c.execute('''CREATE TABLE IF NOT EXISTS likes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    news_id INTEGER NOT NULL)''')
    conn.commit()
    conn.close()


# Haber veritabanı bağlantısını oluştur
def create_news_db():
    conn = sqlite3.connect('haber.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS Haberler (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    Baslik TEXT NOT NULL,
                    Link TEXT NOT NULL UNIQUE,
                    Gorsel TEXT,
                    Tarih TEXT,
                    SiteAdi TEXT NOT NULL)''')
    conn.commit()
    conn.close()


# Haber metninden özet çıkartma
def get_summary(text):
    sentences = re.split(r'(?<=[.!?]) +', text)
    summary = " ".join(sentences[:2])
    return summary


# Haber veritabanından verileri çekme ve özet ekleme
def get_news_with_summary():
    news_with_images = []
    news_without_images = []

    # haber veritabanından haberleri al, site adı Donanım Haber olmayanları filtrele
    conn_haber = sqlite3.connect('haber.db')
    cursor_haber = conn_haber.cursor()
    cursor_haber.execute("SELECT id, Baslik, Link, Gorsel, Tarih FROM Haberler WHERE SiteAdi != 'Donanım Haber'")
    haber_news = cursor_haber.fetchall()
    conn_haber.close()

    # Haberlerin özetlerini ekle
    for haber in haber_news:
        haber_id, baslik, link, gorsel, tarih = haber
        if gorsel and gorsel.strip() != "":
            news_with_images.append((haber_id, baslik, link, gorsel))
        else:
            news_without_images.append((haber_id, baslik, link))

    return news_with_images, news_without_images


# Döviz veritabanı bağlantısını oluştur
def get_latest_exchange_rates():
    conn = sqlite3.connect('doviz_altin_verileri.db')
    cursor = conn.cursor()
    cursor.execute('''SELECT tarih, dolar, euro, altin FROM doviz_altin ORDER BY id DESC LIMIT 1''')
    latest_rates = cursor.fetchone()
    conn.close()
    return latest_rates



# Ana sayfa
@app.route('/')
def home():
    return redirect(url_for('news'))


# Kayıt sayfası
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        try:
            c.execute('''INSERT INTO users (username, password) VALUES (?, ?)''', (username, hashed_password))
            conn.commit()
            flash("Kayıt başarılı, giriş yapabilirsiniz.", "success")
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash("Kullanıcı adı zaten var.", "danger")
        finally:
            conn.close()

    return render_template('signup.html')


# Giriş sayfası
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute('''SELECT * FROM users WHERE username = ? AND password = ?''', (username, hashed_password))
        user = c.fetchone()
        conn.close()

        if user:
            session['username'] = username
            flash("Başarıyla giriş yaptınız.", "success")
            return redirect(url_for('news'))
        else:
            flash("Giriş bilgileri yanlış.", "danger")

    return render_template('login.html')


# Kullanıcı paneli
@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        username = session['username']
        conn_users = sqlite3.connect('users.db')
        cursor_users = conn_users.cursor()

        cursor_users.execute('SELECT id FROM users WHERE username = ?', (username,))
        user = cursor_users.fetchone()
        liked_news = []
        if user:
            user_id = user[0]
            cursor_users.execute('SELECT news_id FROM likes WHERE user_id = ?', (user_id,))
            liked_news_ids = cursor_users.fetchall()

            if liked_news_ids:
                news_ids = [news_id[0] for news_id in liked_news_ids]
                conn_haber = sqlite3.connect('haber.db')
                cursor_haber = conn_haber.cursor()
                placeholder = '?'
                placeholders = ', '.join(placeholder for unused in news_ids)
                query = f'SELECT Baslik, Link, Gorsel FROM Haberler WHERE id IN ({placeholders})'
                cursor_haber.execute(query, news_ids)
                liked_news = cursor_haber.fetchall()
                conn_haber.close()

        conn_users.close()
        return render_template('dashboard.html', liked_news=liked_news, username=username)
    else:
        return redirect(url_for('login'))



# Haber beğenme veya beğenmeyi geri çekme
@app.route('/toggle_like/<int:news_id>', methods=['POST'])
def toggle_like_news(news_id):
    if 'username' not in session:
        return jsonify({'error': 'Beğenmek için giriş yapmanız gerekiyor.'}), 401

    username = session['username']
    conn_users = sqlite3.connect('users.db')
    cursor_users = conn_users.cursor()

    cursor_users.execute('SELECT id FROM users WHERE username = ?', (username,))
    user = cursor_users.fetchone()
    if user:
        user_id = user[0]
        cursor_users.execute('SELECT * FROM likes WHERE user_id = ? AND news_id = ?', (user_id, news_id))
        like = cursor_users.fetchone()

        if like:
            cursor_users.execute('DELETE FROM likes WHERE user_id = ? AND news_id = ?', (user_id, news_id))
            liked = False
        else:
            cursor_users.execute('INSERT INTO likes (user_id, news_id) VALUES (?, ?)', (user_id, news_id))
            liked = True

        conn_users.commit()

    conn_users.close()
    return jsonify({'liked': liked})



# Haber sayfası
@app.route('/news')
def news():
    news_with_images, news_without_images = get_news_with_summary()
    latest_rates = get_latest_exchange_rates()
    return render_template('news.html', news_with_images=news_with_images, news_without_images=news_without_images, latest_rates=latest_rates)


# Çıkış
@app.route('/logout')
def logout():
    session.pop('username', None)
    flash("Başarıyla çıkış yaptınız.", "success")
    return redirect(url_for('news'))


if __name__ == '__main__':
    create_user_db()
    create_news_db()
    app.run(debug=True)