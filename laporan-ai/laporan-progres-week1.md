# Laporan Progres Minggu 1

Tanggal: 13 November 2026. Basis: `revisi-progress-week1.md` + `prompt/review1-revisi-week1.md`.

## Ringkasan

Selesai: TTS demo, ASR demo, korpus tunggal, tiga dokumen `docs/`, `ReadMe.txt`.
Belum: alur dialog penuh, pencocokan jawaban, penanganan kesalahan suara, antarmuka (minggu 2-3).
Satu butir review (pengecekan semua tautan `docs/riset.md`) **tidak dikerjakan** karena dokumen review menulis "JANGAN DIEKSEKUSI DAHULU".

## Status butir review1

| # | Butir | Status | Bukti |
|---|---|---|---|
| 1 | Korpus ganda | Selesai | Sumber kebenaran = `korpus/cerita/*.json`. `korpus/cerita.json` dihapus. `tts_demo.py` sekarang membaca folder yang sama dengan `modul/korpus.py`; id cerita `kancil`, `timun`, `malin`. |
| 2 | `requirements.txt` tidak lengkap | Selesai | Tambah `PyAudio>=0.2.14`. ReadMe kini menyebut isi lengkap: streamlit, gTTS, pyttsx3, SpeechRecognition, PyAudio, scikit-learn, numpy, plus paket minimum untuk minggu 1. |
| 3a | `--durasi` tidak berpengaruh | Selesai | `transkripsi()` menerima `durasi` dan memakainya di `listen(timeout=durasi, phrase_time_limit=durasi)`. Diuji: `--durasi 2` mencetak "batas 2 detik" dan berhenti sesuai batas. |
| 3b | `energy_threshold` menimpa hasil ukur | Selesai | Urutan: `adjust_for_ambient_noise()` lalu `energy_threshold = max(hasil_ukur, ambang)`. Diuji: hasil ukur 231, batas bawah 300, keduanya dicetak. |
| 3c | `--berkas` memakai `listen()` | Selesai | Jalur berkas memakai `record()` (`dari_berkas=True`), tidak ada lagi ambang/waktu tunggu di jalur ini. Diuji dengan WAV sintetis: log "Membaca berkas suara..." lalu transkripsi jalan. |
| 4 | Folder `/laporan-ai` | Selesai | Berkas ini. |
| 5 | Isi keputusan kelompok + verifikasi semua tautan riset | **Belum, sengaja** | Dokumen review menulis "JANGAN DIEKSEKUSI DAHULU". Bagian 5 `docs/keputusan-teknis.md` masih `[KEPUTUSAN KELOMPOK]`, `docs/riset.md` masih memakai `[perlu diverifikasi]`. |

## Hasil uji nyata

```
python tts_demo.py --daftar
kancil     Si Kancil dan Buaya (5 segmen, berkas 01_kancil.json)
timun      Timun Mas (5 segmen, berkas 02_timun.json)
malin      Malin Kundang (5 segmen, berkas 03_malin.json)

python tts_demo.py --segmen 1 --tanpa-putar
[sukses] Suara disimpan: ...\suara\kancil_segmen1_normal.mp3

python tts_demo.py --cerita malin --segmen 5 --tanpa-putar
[sukses] Suara disimpan: ...\suara\malin_segmen5_normal.mp3

python tts_demo.py --cerita kancil-buaya
[gagal] Korpus tidak bisa dibaca: Cerita 'kancil-buaya' tidak ada. Pilihan: kancil, timun, malin
exit=1

python asr_demo.py --durasi 2 --penyetelan 0.2
[asr] Mengukur kebisingan ruangan (0.2 detik)...
[asr] Ambang suara hasil ukur: 231 (batas bawah 300)
[asr] Mendengarkan... (bicara sekarang, batas 2 detik)
[info] Suara terdengar, tetapi belum bisa dimengerti. Coba bicara lebih jelas.
exit=0
```

`python -m py_compile tts_demo.py asr_demo.py` bersih.

## Masalah yang ditemui

1. **`listen()` di `AudioFile` tidak error, tapi mengabaikan isi berkas.** Uji langsung: `listen()` pada WAV 1,5 detik berhenti tanpa galat, padahal `record()` membaca seluruh 1,5 detik. Jadi `record()` tetap pilihan benar untuk `--berkas`, walau efeknya tidak terlihat dari pesan galat.
2. **ASR mikrofon di mesin pengembang tidak menghasilkan teks.** Mikrofon terdeteksi, ucapan tertangkap, tetapi Google menjawab `UnknownValueError`. Duga: tidak ada suara bicara saat uji, atau `flac` kurang. Belum bisa disimpulkan; perlu uji dengan orang yang benar-benar bicara.
3. **pyttsx3 di mesin pengembang hanya punya suara Inggris** (David, Hazel, Zira). Kata Indonesia dilafalkan beraksen Inggris. gTTS tetap mesin utama. Di perangkat lain hasilnya bisa beda, perlu dicek tiap anggota.
4. **`tts_demo.py` dulu baca kolom `teks`, sedangkan korpus aplikasi memakai `narasi`.** Sudah disesuaikan.
5. **Fetch halaman `https://paudpedia.kemdikbud.go.id/` gagal dari mesin ini** (error koneksi). Ini termasuk butir 5 yang belum boleh dikerjakan, jadi hanya dicatat. `https://www.healthychildren.org/English/fmp/Pages/MediaPlan.aspx` terbuka (judul "AAP Media Plan").
6. **Simulasi uji sempat meninggalkan `w.wav`** karena `AudioFile` masih terbuka saat `unlink()`. Sudah dihapus, tidak ada sisa berkas.

## Sisa pekerjaan untuk minggu 2-3

- Antarmuka (Streamlit) sesuai `docs/sketsa-ui.md`.
- Pencocokan jawaban dengan `variasi`, `kata_kunci`, `hint`.
- Penanganan suara tidak jelas, terpotong, tidak dimengerti (bonus 3 poin).
- Butir review 5 (keputusan kelompok + verifikasi tautan) setelah izin dari pembimbing/kelompok.

## Berkas yang berubah pada revisi ini

| Berkas | Perubahan |
|---|---|
| `requirements.txt` | + `PyAudio>=0.2.14` |
| `asr_demo.py` | `durasi` dipakai; ambang tidak menimpa hasil ukur; `record()` untuk berkas |
| `tts_demo.py` | Baca `korpus/cerita/*.json`, kolom `narasi`, opsi `--daftar`, id baru (`kancil`) |
| `ReadMe.txt` | Isi pustaka lengkap, id cerita baru, cara cek korpus, status, NIM dari `Readme.md` |
| `korpus/cerita.json` | Dihapus (sumber ganda) |
| `laporan-ai/laporan-progres-week1.md` | Baru |
