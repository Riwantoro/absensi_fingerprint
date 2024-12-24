import sqlite3

def create_connection():
    conn = sqlite3.connect('absensi.db')
    return conn

def setup_database():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS karyawan (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nama TEXT NOT NULL,
                        fingerprint_id TEXT UNIQUE NOT NULL)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS absensi (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        karyawan_id INTEGER,
                        tanggal DATE,
                        waktu_masuk TIME,
                        waktu_keluar TIME,
                        status TEXT,
                        FOREIGN KEY (karyawan_id) REFERENCES karyawan (id))''')
    conn.commit()
    conn.close()