# Panggung Dongeng Nusantara

Kuis interaktif berbasis suara untuk anak usia dini (4–6 tahun). Narator membacakan dongeng Nusantara adegan demi adegan, lalu anak menjawab pertanyaan dengan suaranya. Jawaban anak diubah menjadi teks (ASR), dinilai dengan **TF-IDF dan cosine similarity** (bukan exact match), lalu dibalas dengan suara (TTS). Suara narator memakai **edge-tts** (suara saraf bahasa Indonesia yang lebih berintonasi), dengan cadangan otomatis gTTS lalu pyttsx3.

Tugas Pemrograman Akhir NLPTA (IT6073), Tugas A.

## Anggota kelompok

> Wajib diisi sebelum dikumpulkan.

| No | NIM | Nama |
|----|-----|------|
| 1  |71230975|Thomas Aquinas Ryan Wisnu Adi|
| 2  |71230994|Putu Gde Kenzie Carlen Mataram|
| 3  |71231023|Yehezkiel Darren Putra Wardoyo|

## Fitur utama

- **Suara narator berintonasi**: edge-tts `id-ID-GadisNeural` sebagai mesin utama. Jika internet atau layanan gagal, aplikasi pindah sendiri ke gTTS, lalu ke pyttsx3 (luring).
- **3 dongeng, 15 adegan**: Si Kancil dan Buaya, Timun Mas, Malin Kundang. Tiap adegan bergambar dan dibacakan narator.
- **Jawaban lisan**: anak merekam jawaban langsung di peramban, lalu Google Speech Recognition mentranskripsinya.
- **Penilaian NLP yang toleran**: menerima "kancil melompat ke punggungnya buaya", "boaya", atau "seneng", tetapi menolak "bukan batu".
- **Umpan balik ramah anak**: pujian, petunjuk bertingkat, lalu kunci jawaban dibacakan pada percobaan ketiga.
- **Penanganan gangguan suara**: rekaman hening, terpotong, tidak jelas, atau internet putus dibalas dengan pesan ramah, dan kesempatan anak tidak berkurang.
- **Demo terpisah**: `tts_demo.py` (membandingkan mesin suara, pra-render audio) dan `asr_demo.py` (menguji pengenalan suara dari mikrofon atau berkas WAV).
- **Panel guru**: batas lulus, detail NLP, mode ketik tanpa mikrofon, narator pelan, dan tabel hasil di akhir cerita.

## Struktur folder

```
uas-nlp/
├── dongeng_nusantara.py        titik masuk aplikasi (main), dijalankan dengan streamlit run
├── tts_demo.py                 demo TTS: edge-tts, gTTS, pyttsx3, cache dan pra-render audio
├── asr_demo.py                 demo ASR: mikrofon atau berkas WAV
├── modul/                      seluruh logika aplikasi
│   ├── konfigurasi.py          lokasi berkas, suara TTS, ambang, dan batas waktu
│   ├── korpus.py               memuat korpus dongeng dan leksikon
│   ├── nlp.py                  praproses, TF-IDF, cosine similarity
│   ├── tts.py                  suara narator: edge-tts, cadangan gTTS lalu pyttsx3
│   ├── asr.py                  pemeriksaan rekaman, Google Speech Recognition
│   ├── kuis.py                 pujian, petunjuk bertingkat, kunci jawaban
│   ├── ilustrasi.py            gambar adegan (SVG)
│   ├── status.py               status permainan di st.session_state
│   ├── komponen.py             CSS, kartu, papan stiker, panel guru
│   └── halaman.py              halaman beranda, cerita, dan tamat
├── korpus/                     data dongeng
│   ├── cerita/
│   │   ├── 01_kancil.json      Si Kancil dan Buaya
│   │   ├── 02_timun.json       Timun Mas
│   │   └── 03_malin.json       Malin Kundang
│   ├── flashcard/              (kosong) tempat korpus flashcard hewan dan buah, rencana
│   └── leksikon.json           stopword, kata pengisi, kamus normalisasi, kata dasar
├── aset/
│   ├── tampilan.css            gaya tampilan
│   ├── gambar/                 (kosong) cerita/, hewan/, buah/ untuk gambar, rencana
│   └── model3d/                (kosong) berkas .glb jika memakai animasi 3D, rencana
├── suara/                      cache MP3 dari tts_demo.py (dibuat otomatis, tidak di-commit)
├── pengujian/
│   └── uji_sistem.py           evaluasi NLP dan 36 uji unit
├── docs/
│   ├── riset.md                riset belajar bahasa anak usia dini
│   ├── keputusan-teknis.md     perbandingan pustaka TTS, ASR, dan UI
│   ├── sketsa-ui.md            sketsa antarmuka
│   ├── laporan/
│   │   └── Laporan_Panggung_Dongeng_Nusantara.pdf
│   └── laporan-ai/
│       └── laporan-progres-week1.md
├── .streamlit/config.toml      memaksa tema terang
├── requirements.txt            pustaka aplikasi (juga dipakai saat deploy)
├── requirements-demo.txt       requirements.txt + PyAudio, untuk asr_demo.py
├── ReadMe.txt                  berkas teks untuk pengumpulan
└── Readme.md
```

- **Kode** ada di `dongeng_nusantara.py` (hanya titik masuk) dan folder `modul/`. `tts_demo.py` dan `asr_demo.py` adalah skrip demo yang berdiri sendiri. Semua kode ditulis sebagai fungsi, tanpa class.
- **Data** ada di `korpus/`, sehingga menambah cerita tidak perlu mengubah kode.
- **Aset, suara, pengujian, dan dokumen** masing-masing punya folder sendiri. Folder yang bertanda "rencana" baru berisi penanda kosong (`.gitkeep`).

### Peran tiap modul

| Modul | Fungsi penting | Peran | Memakai modul |
|---|---|---|---|
| `konfigurasi.py` | – | Lokasi berkas, suara TTS, ambang skor, batas waktu | – |
| `korpus.py` | `muat_cerita()` | Membaca dan memeriksa berkas JSON dongeng | konfigurasi |
| `nlp.py` | `praproses()`, `nilai_jawaban()`, `nilai_alternatif()` | Inti NLP: menilai jawaban anak | konfigurasi, korpus |
| `tts.py` | `buat_suara()`, `putar_suara()` | Teks menjadi suara: edge-tts, cadangan gTTS lalu pyttsx3. Hasil tiap teks di-cache selama aplikasi berjalan | konfigurasi |
| `asr.py` | `periksa_audio()`, `transkripsi()` | Suara menjadi teks, dan mendeteksi gangguan | konfigurasi |
| `kuis.py` | `putuskan()` | Memilih pujian, petunjuk, atau kunci jawaban | konfigurasi, asr |
| `ilustrasi.py` | `gambar_adegan()` | Menyusun gambar adegan dari korpus | korpus |
| `status.py` | `proses_teks()`, `tangani_rekaman()` | Menghubungkan rekaman, NLP, dan kuis | konfigurasi, korpus, nlp, asr, kuis |
| `komponen.py` | `pasang_css()`, `kartu_banding()` | Potongan tampilan yang dipakai ulang | konfigurasi, korpus |
| `halaman.py` | `halaman_beranda()`, `halaman_cerita()`, `halaman_tamat()` | Susunan tiap halaman | konfigurasi, korpus, ilustrasi, tts, status, komponen |

`dongeng_nusantara.py` hanya menyiapkan halaman, memasang CSS, lalu memanggil halaman yang sedang aktif.

## Kebutuhan

- **Python 3.11 atau lebih baru.** Streamlit 1.66 tidak mendukung Python 3.10.
- Koneksi internet, untuk suara narator (edge-tts, cadangan gTTS) dan pengenalan suara (Google). Tanpa internet, narator memakai pyttsx3 (luring, kualitas bergantung pada suara yang terpasang di komputer).
- Mikrofon, dan peramban Chrome, Edge, atau Firefox.

## Instalasi dan menjalankan

```bash
# 1. Masuk ke folder proyek, lalu buat lingkungan virtual
python -m venv .venv

# 2. Aktifkan lingkungan virtual
.venv\Scripts\activate          # Windows
source .venv/bin/activate       # macOS atau Linux

# 3. Pasang pustaka
pip install -r requirements.txt

# 4. Jalankan aplikasi
streamlit run dongeng_nusantara.py
```

Peramban akan terbuka di <http://localhost:8501>. Izinkan akses mikrofon saat diminta.

Aplikasi merekam lewat mikrofon peramban, jadi **PyAudio tidak diperlukan**. PyAudio hanya dipakai `asr_demo.py`. Untuk menjalankannya, pasang dengan `pip install -r requirements-demo.txt`.

## Demo suara terpisah

Jalankan dari folder proyek. `tts_demo.py` membaca korpus yang sama dengan aplikasi (`korpus/cerita/*.json`), dan menyimpan hasil suara di `suara/` dengan nama hash dari teks, mesin, suara, kecepatan, dan nada, sehingga teks yang sama tidak disintesis ulang.

```bash
python tts_demo.py --daftar                          # id cerita dan jumlah segmen
python tts_demo.py                                   # segmen 1 cerita kancil, suara Gadis
python tts_demo.py --cerita malin --segmen 2 --suara id-ID-ArdiNeural
python tts_demo.py --rate -10 --pitch 5              # 10% lebih lambat, nada +5 Hz
python tts_demo.py --mesin gtts                      # paksa mesin: auto, edge, gtts, pyttsx3
python tts_demo.py --bandingkan                      # tiga mesin, kalimat yang sama
python tts_demo.py --semua --tanpa-putar             # pra-render seluruh korpus, tanpa memutar

python asr_demo.py                                   # rekam dari mikrofon, cetak teksnya
python asr_demo.py --durasi 8                        # batas rekam 8 detik
python asr_demo.py --berkas contoh.wav               # uji dari berkas WAV, tanpa mikrofon
```

Nilai `--rate` dan `--pitch` ditulis sebagai angka bertanda saja (`-10`, `5`), tanpa `%` atau `Hz`.

## Cara memakai

1. Pilih cerita, lalu tekan **Dengarkan**.
2. Dengarkan narator, lalu tekan **Aku siap menjawab**.
3. Tekan ikon mikrofon, ucapkan jawaban, lalu tekan tombol berhenti.
4. Sistem membandingkan jawaban anak dengan jawaban dari cerita dan memberi umpan balik.
5. Setelah lima adegan, halaman **Tamat** menampilkan stiker yang didapat dan catatan untuk guru.

**Panel "Untuk guru dan orang tua"** ada di bagian bawah halaman:

| Pengaturan | Kegunaan |
|---|---|
| Batas lulus kecocokan | Menaikkan atau menurunkan ambang skor (bawaan 0,75) |
| Tampilkan detail NLP | Memperlihatkan token bersih, kunci terdekat, dan nilai cosine |
| Ketik jawaban tanpa mikrofon | Untuk demo atau jika mikrofon bermasalah |
| Suara narator lebih pelan | Narator membaca 15% lebih lambat |

## Cara kerja penilaian jawaban

```
jawaban (teks ASR) → normalisasi → penanda negasi → stopword → stemming
→ question demoting → koreksi ejaan → TF-IDF (kata + n-gram huruf)
→ cosine similarity → skor ≥ 0,75 ? benar : (≥ 0,5625 ? hampir benar : salah)
```

Contoh: untuk pertanyaan *"Ke mana Kancil melompat?"*, jawaban *"Kancil melompat ke punggungnya buaya"* menjadi token `punggung, buaya` dan lulus, sedangkan *"bukan punggung buaya"* menjadi `tidak_punggung, tidak_buaya` dan ditolak. Rinciannya ada di laporan, bagian 6.

## Daftar korpus

Tiap dongeng berisi 5 adegan. Tiap adegan punya narasi, satu pertanyaan, jawaban utama, dan jawaban lain yang juga diterima.

### Si Kancil dan Buaya (Fabel Nusantara)

| No | Pertanyaan | Jawaban utama | Juga diterima |
|----|------------|---------------|---------------|
| 1 | Buah apa yang dilihat Si Kancil? | rambutan | buah rambutan |
| 2 | Hewan apa yang ada di dalam sungai? | buaya | – |
| 3 | Buaya berbaris seperti apa? | jembatan | – |
| 4 | Ke mana Kancil melompat? | punggung buaya | punggung, atas buaya, buaya |
| 5 | Apa yang Kancil ucapkan kepada buaya? | maaf | minta maaf |

### Timun Mas (Cerita rakyat Jawa Tengah)

| No | Pertanyaan | Jawaban utama | Juga diterima |
|----|------------|---------------|---------------|
| 1 | Apa yang diberikan raksasa? | biji timun | biji, timun |
| 2 | Apa warna timun itu? | emas | kuning, kuning emas, warna emas |
| 3 | Siapa yang datang menjemput Timun Mas? | raksasa | raksasa hijau, buto ijo |
| 4 | Jarum berubah menjadi apa? | hutan bambu | bambu |
| 5 | Timun Mas pulang kepada siapa? | ibu | mbok srini, mbok |

### Malin Kundang (Cerita rakyat Sumatera Barat)

| No | Pertanyaan | Jawaban utama | Juga diterima |
|----|------------|---------------|---------------|
| 1 | Malin tinggal bersama siapa? | ibu | – |
| 2 | Malin pergi naik apa? | kapal | kapal besar, perahu |
| 3 | Bagaimana perasaan ibu saat Malin pulang? | senang | gembira, bahagia, sangat senang |
| 4 | Malin menjadi anak yang bagaimana? | sombong | durhaka, jahat, nakal, tidak baik |
| 5 | Malin berubah menjadi apa? | batu | – |

### Leksikon (`korpus/leksikon.json`)

| Daftar | Jumlah | Contoh |
|---|---|---|
| normalisasi | 23 | gak → tidak, bunda → ibu, ijo → hijau |
| pertentangan | 4 | tapi, tetapi, melainkan, namun |
| stopword | 71 | yang, di, ke, itu, kak |
| pengisi | 27 | eh, hmm, menurut, mungkin |
| kata_dasar | 132 | lompat, sungai, jembatan, raksasa |

## Menambah dongeng baru

1. Salin salah satu berkas di `korpus/cerita/`, misalnya menjadi `04_bawang.json`. Angka di depan menentukan urutan, dan sisanya (`bawang`) menjadi kode cerita.
2. Isi `judul`, `asal`, `ajaran`, `warna`, dan daftar `adegan`. Contoh satu adegan:

   ```json
   {
     "narasi": "Bawang Putih mencuci baju di sungai. Tiba-tiba selendangnya hanyut.",
     "tanya": "Apa yang hanyut di sungai?",
     "kunci": ["selendang", "kain"],
     "utama": "selendang",
     "petunjuk": "Kain panjang yang dipakai di bahu.",
     "stiker": "🧣",
     "gambar": {"latar": "sungai", "objek": [
       {"emoji": "👧", "x": 300, "y": 300, "ukuran": 120},
       {"emoji": "🧣", "x": 620, "y": 380, "ukuran": 90}
     ]}
   }
   ```

   - `utama` harus ada di daftar `kunci`.
   - Latar yang tersedia: `sungai`, `senja`, `ladang`, `bambu`, `lumpur`, `pantai`, `dermaga`, `badai`, `polos`.
   - Objek gambar berupa emoji (`"emoji"`), atau gambar buatan sendiri (`"gambar": "kancil" | "pohon" | "batu" | "rambutan"`). Ukuran bidang gambar 960 × 480.
3. Tambahkan kata dasar baru dari cerita itu ke `kata_dasar` di `korpus/leksikon.json`, misalnya `selendang` dan `cuci`, agar stemmer mengenali "mencuci" dan "selendangnya".
4. Jalankan `python pengujian/uji_sistem.py`. Kolom yang hilang atau kunci yang tidak bisa dicocokkan langsung dilaporkan.

## Pengujian

```bash
python pengujian/uji_sistem.py              # evaluasi NLP + 36 uji unit, tanpa internet
python pengujian/uji_sistem.py --langsung   # tambah uji Streamlit, gTTS, dan Google ASR sungguhan
python pengujian/uji_sistem.py --json hasil.json   # simpan hasil evaluasi ke berkas JSON
```

Langkah Google ASR pada `--langsung` memerlukan `ffmpeg` untuk mengubah MP3 menjadi WAV. Tanpa ffmpeg, langkah itu dilewati.

Hasil evaluasi saat ini (ambang 0,75):

| Set data | Exact match (F1) | Sistem ini (F1) |
|---|---|---|
| A uji, 105 jawaban | 0,310 | 0,992 |
| B bersih, 378 jawaban | 0,286 | 1,000 |
| B berderau (salah ejaan), 318 jawaban | 0,026 | 0,904 |

Data uji ditulis atau dibuat oleh pembuat sistem, bukan rekaman suara anak. Penjelasan lengkapnya ada di laporan, bagian 9.

## Jika ada masalah

| Gejala | Penyebab dan solusi |
|---|---|
| `pip install` gagal memasang streamlit | Versi Python terlalu lama. Periksa dengan `python --version`; minimal 3.11. |
| Suara narator tidak otomatis berbunyi | Peramban memblokir autoplay sebelum ada interaksi. Klik di mana saja pada halaman, lalu tekan play. |
| Mikrofon tidak bisa dipakai | Buka lewat `http://localhost:8501`. Jika dibuka dari komputer lain, peramban mewajibkan HTTPS untuk mikrofon. |
| Pesan "Alat pengenal suara belum lengkap" | Di Mac Apple Silicon atau Linux ARM, pasang flac (contoh: `brew install flac`). |
| Suara narator terdengar lebih datar dari biasanya | edge-tts gagal, sehingga aplikasi memakai gTTS atau pyttsx3. Periksa internet, perbarui dengan `python -m pip install -U edge-tts`, dan pastikan jam komputer benar. |
| `tts_demo.py` menampilkan `403 Invalid response status` atau `NoAudioReceived` | Versi edge-tts lama, jam komputer tidak tepat, atau jaringan (proxy, VPN, kampus) memblokir layanan. Coba hotspot HP. Untuk demo, pra-render dengan `--semua` saat jaringan baik. |
| Pesan "Sambungan internetnya sedang terganggu" | Periksa koneksi internet. Untuk demo tanpa internet, nyalakan mode ketik di panel guru. |
| Galat `Korpus ... belum lengkap` saat membuka aplikasi | Ada kolom yang hilang di berkas JSON cerita. Pesannya menyebut nama berkas, nomor adegan, dan kolomnya. |

## Rencana pengembangan

Belum diimplementasikan; folder pendukungnya sudah disiapkan.

- Menu tema di halaman awal: **Cerita Rakyat**, **Hewan**, dan **Buah**.
- Mode **flashcard** untuk Hewan dan Buah: gambar, tulisan, dan suara TTS, lalu anak menyebutkan kata ke mikrofon (korpus di `korpus/flashcard/`, gambar di `aset/gambar/`).
- Tampilan cerita seperti buku anak dengan animasi balik halaman, dan animasi 3D (Three.js) bila perlu.
- Pra-render audio narasi, pertanyaan, dan umpan balik agar demo tetap lancar tanpa internet.

## Riwayat versi

| Versi | Perubahan |
|---|---|
| 1.0 | Aplikasi Streamlit: dongeng bersuara, penilaian TF-IDF dan cosine, penanganan gangguan suara, panel guru |
| 1.1 | edge-tts menjadi mesin suara utama (cadangan gTTS dan pyttsx3), `tts_demo.py` dengan cache dan pra-render, perapian struktur folder |

## Laporan

Penjelasan lengkap tentang landasan teori, modul NLP, penanganan kesalahan, daftar fungsi, dan hasil uji ada di [docs/laporan/Laporan_Panggung_Dongeng_Nusantara.pdf](docs/laporan/Laporan_Panggung_Dongeng_Nusantara.pdf).