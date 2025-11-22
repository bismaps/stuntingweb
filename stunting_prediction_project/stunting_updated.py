import joblib
import pandas as pd
import warnings
import os

# Suppress warnings
warnings.filterwarnings('ignore', category=UserWarning)

# Try to load the new model first
model_path = "artifacts_sklearn171/best_model_RandomForest.joblib"
if os.path.exists(model_path):
    try:
        model = joblib.load(model_path)
        print(f"✅ Model terbaru berhasil dimuat dari: {model_path}")
    except Exception as e:
        print(f"❌ Error loading new model: {e}")
        exit(1)
else:
    # Fallback to old model with proper error handling
    try:
        model = joblib.load("best_model_RandomForest.joblib")
        print("⚠️  Menggunakan model lama (mungkin ada warning versi)")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nSolusi:")
        print("1. Jalankan training ulang: python train.py --csv stunting_wasting_dataset.csv --target Stunting")
        print("2. Atau gunakan environment dengan scikit-learn versi yang kompatibel")
        exit(1)

# Input dari user
print("\n=== Prediksi Risiko Stunting ===")
try:
    umur = float(input("Masukkan umur anak (bulan): "))
    berat = float(input("Masukkan berat badan anak (kg): "))
    tinggi = float(input("Masukkan tinggi badan anak (cm): "))
    jk = input("Masukkan jenis kelamin (L/P): ").strip()
    
    # Convert jenis kelamin to format yang diharapkan model
    jk_converted = "Laki-laki" if jk.upper() in ['L', 'LAKI', 'LAKI-LAKI'] else "Perempuan"
    
    # Buat DataFrame sesuai format dataset yang ditraining
    data_baru = pd.DataFrame([{
        "Jenis_Kelamin": jk_converted,
        "Umur_(bulan)": umur,
        "Tinggi_Badan_(cm)": tinggi,
        "Berat_Badan_(kg)": berat,
        "Wasting": "Normal"  # Default value untuk kolom yang tidak digunakan dalam prediksi stunting
    }])
    
    # Prediksi
    pred = model.predict(data_baru)[0]
    prob = model.predict_proba(data_baru)[0]
    
    print(f"\n✅ Hasil prediksi:")
    print(f"📊 Input data:")
    print(f"   - Jenis Kelamin: {jk_converted}")
    print(f"   - Umur: {umur} bulan")
    print(f"   - Berat: {berat} kg")
    print(f"   - Tinggi: {tinggi} cm")
    
    print(f"\n🎯 Hasil:")
    print(f"   - Kelas: {'🔴 Stunting' if pred == 1 else '🟢 Tidak Stunting'}")
    print(f"   - Probabilitas Tidak Stunting: {prob[0]:.1%}")
    print(f"   - Probabilitas Stunting: {prob[1]:.1%}")
    
    if pred == 1:
        print(f"\n⚠️  PERINGATAN: Anak berisiko stunting!")
        print(f"   Segera konsultasi dengan tenaga kesehatan.")
    else:
        print(f"\n✅ BAIK: Status pertumbuhan normal.")
        print(f"   Tetap jaga pola makan dan kesehatan anak.")

except ValueError as e:
    print(f"❌ Error input: Pastikan memasukkan angka yang valid")
except Exception as e:
    print(f"❌ Error tidak terduga: {e}")
