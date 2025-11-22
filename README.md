# Stunting Prediction System (Hybrid Microservices)

Aplikasi web untuk memprediksi status stunting pada anak menggunakan arsitektur **Hybrid Microservices**.
- **Frontend**: Native PHP + Tailwind CSS
- **Backend**: Python Flask + Scikit-Learn (RandomForest)
- **Akurasi Model**: **~94.91%** (Evaluasi pada 20.000 data test)

## Persyaratan Sistem
- Python 3.8+
- PHP 7.4+
- Koneksi Internet (untuk CDN Tailwind CSS)

## Instalasi

1.  **Install Python Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Setup Model AI:**
    - Pastikan folder `stunting_prediction_project/` ada di direktori root.
    - Backend akan otomatis memuat model dari `stunting_prediction_project/artifacts_sklearn171/best_model_RandomForest.joblib`.

## Cara Menjalankan Aplikasi

Anda perlu menjalankan **dua terminal** terpisah.

### Terminal 1: Jalankan Backend (Flask)
```bash
python api_model.py
```
*Server akan berjalan di `http://127.0.0.1:5000`*

### Terminal 2: Jalankan Frontend (PHP Built-in Server)
```bash
php -S localhost:8000
```
*Aplikasi dapat diakses di `http://localhost:8000`*

## Cara Menggunakan
1.  Buka browser dan kunjungi `http://localhost:8000`.
2.  Masukkan data Usia, Tinggi Badan, Berat Badan, dan Jenis Kelamin.
3.  Klik "Analisa Sekarang".
4.  Hasil prediksi (Normal/Stunting) akan muncul dengan indikator warna.

## Evaluasi Sistem
Untuk memverifikasi akurasi model terhadap dataset asli (20.000 data test):
```bash
python evaluate_system.py
```
*Script ini akan melakukan testing otomatis dan menampilkan laporan akurasi.*

## Catatan Teknis
- **Model**: Menggunakan RandomForest Classifier (Binary: Normal vs Stunting).
- **Fitur Wasting**: Karena model membutuhkan input `Wasting`, sistem secara otomatis menggunakan nilai default "Normal weight" untuk prediksi stunting agar UX tetap sederhana (hanya input tinggi/berat/usia).
