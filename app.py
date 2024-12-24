from flask import Flask, render_template, request, redirect, url_for
from database import create_connection, setup_database
from fingerprint_handler import FingerprintHandler
import datetime
import sqlite3  # Pastikan sqlite3 diimpor

app = Flask(__name__)
fp_handler = FingerprintHandler()  # Inisialisasi perangkat fingerprint

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/daftar', methods=['POST'])
def daftar_karyawan():
    nama = request.form['nama']
    # Logika untuk mendaftarkan karyawan
    if not fp_handler:
        fp_id = input("Mode simulasi - Masukkan ID Fingerprint manual: ")
    else:
        fp_id = fp_handler.enroll_fingerprint()
        if fp_id is None:
            return "Gagal mendaftarkan sidik jari!", 400

    with create_connection() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO karyawan (nama, fingerprint_id) VALUES (?, ?)", 
                           (nama, str(fp_id)))
            conn.commit()
            return redirect(url_for('index'))
        except sqlite3.IntegrityError:
            return "Error: ID Fingerprint sudah terdaftar!", 400

@app.route('/absen', methods=['POST'])
def absen():
    if not fp_handler:
        fp_id = input("Mode simulasi - Masukkan ID Fingerprint: ")
    else:
        fp_id = fp_handler.scan_fingerprint()
        if fp_id is None:
            return "Gagal membaca sidik jari!", 400

    with create_connection() as conn:
        cursor = conn.cursor()
        
        # Cek karyawan
        cursor.execute("SELECT * FROM karyawan WHERE fingerprint_id = ?", (str(fp_id),))
        karyawan = cursor.fetchone()
        
        if not karyawan:
            return "Fingerprint tidak terdaftar!", 400
        
        # Proses absensi
        tanggal = datetime.date.today()
        waktu = datetime.datetime.now().time()
        
        # Konversi waktu ke string
        waktu_str = waktu.strftime("%H:%M:%S")  # Format waktu sebagai string

        cursor.execute("""SELECT waktu_masuk, waktu_keluar 
                          FROM absensi 
                          WHERE karyawan_id = ? AND tanggal = ?""", (karyawan[0], tanggal))
        
        absensi = cursor.fetchone()
        
        if not absensi:
            # Absen masuk
            cursor.execute("""INSERT INTO absensi (karyawan_id, tanggal, waktu_masuk, status)
                              VALUES (?, ?, ?, 'MASUK')""", (karyawan[0], tanggal, waktu_str))
            return f"Selamat datang {karyawan[1]}!"
        elif not absensi[1]:
            # Absen keluar
            cursor.execute("""UPDATE absensi 
                              SET waktu_keluar = ?, status = 'LENGKAP'
                              WHERE karyawan_id = ? AND tanggal = ?""", (waktu_str, karyawan[0], tanggal))
            return f"Terima kasih {karyawan[1]}, Anda telah absen keluar!"
        else:
            return "Anda sudah absen hari ini!", 400

if __name__ == '__main__':
    setup_database()  # Setup database saat aplikasi dijalankan
    app.run(debug=True)