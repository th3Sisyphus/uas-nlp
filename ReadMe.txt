========================================================
 PANGGUNG DONGENG NUSANTARA
 Kuis Interaktif Belajar Bahasa Indonesia Berbasis Suara
 Tugas Pemrograman Akhir NLP (Tugas A) - Versi 1.1
========================================================

Aplikasi untuk anak usia dini (4-6 tahun). Narator membacakan dongeng
Nusantara adegan demi adegan, lalu anak menjawab pertanyaan dengan
suaranya. Jawaban diubah menjadi teks (ASR), dinilai dengan TF-IDF dan
cosine similarity, lalu dibalas dengan suara narator (TTS).

Suara narator: edge-tts (suara saraf id-ID-GadisNeural) sebagai mesin
utama. Jika gagal, otomatis pindah ke gTTS, lalu pyttsx3 (luring).


--------------------------------------------------------
1. ISI ARSIP
--------------------------------------------------------
    ReadMe.txt                  berkas ini
    Readme.md                   penjelasan lengkap proyek
    dongeng_nusantara.py        aplikasi utama (Streamlit)
    tts_demo.py                 demo Text-to-Speech
    asr_demo.py                 demo Automated Speech Recognition
    modul/*.py                  seluruh logika aplikasi
    korpus/cerita/*.json        korpus mini: 3 cerita, 15 adegan
    korpus/leksikon.json        stopword, kata pengisi, kamus normalisasi
    aset/tampilan.css           gaya tampilan
    pengujian/uji_sistem.py     evaluasi NLP dan 36 uji unit
    docs/                       riset, keputusan teknis, sketsa UI, laporan
    requirements.txt            pustaka aplikasi
    requirements-demo.txt       requirements.txt + PyAudio (untuk asr_demo.py)

Folder suara/ berisi cache MP3 dari tts_demo.py. Folder ini dibuat
otomatis dan tidak wajib ikut diarsipkan.


--------------------------------------------------------
2. ANGGOTA KELOMPOK
--------------------------------------------------------
    1. 71230975 - Thomas Aquinas Ryan Wisnu Adi
    2. 71230994 - Putu Gde Kenzie Carlen Mataram
    3. 71231023 - Yehezkiel Darren Putra Wardoyo


--------------------------------------------------------
3. SYARAT
--------------------------------------------------------
    - Python 3.11 atau lebih baru (sudah diuji di Python 3.13).
    - Peramban Chrome, Edge, atau Firefox, dan mikrofon.
    - Sambungan internet untuk suara edge-tts (cadangan gTTS) dan
      pengenalan suara Google. Tanpa internet, narator memakai pyttsx3
      (luring), tetapi pengenalan suara tidak bisa dipakai; gunakan mode
      ketik di panel guru.
    - Windows, macOS, atau Linux.


--------------------------------------------------------
4. MEMASANG PUSTAKA
--------------------------------------------------------
Buka terminal di folder berkas ini, lalu jalankan:

    python -m venv .venv
    .venv\Scripts\activate            (Windows)
    source .venv/bin/activate         (macOS atau Linux)
    python -m pip install -r requirements.txt

Isi requirements.txt:
    streamlit, edge-tts, gTTS, pyttsx3, SpeechRecognition,
    scikit-learn, numpy

PyAudio TIDAK diperlukan oleh aplikasi, karena aplikasi merekam lewat
mikrofon peramban. PyAudio hanya dipakai asr_demo.py. Untuk
menjalankan asr_demo.py dengan mikrofon, pasang:

    python -m pip install -r requirements-demo.txt

Catatan per sistem (untuk PyAudio dan SpeechRecognition):
    Windows   Jika PyAudio gagal terpasang, coba:
              pip install pipwin  lalu  pipwin install pyaudio
    macOS     pip install pyaudio
              brew install flac        (dibutuhkan SpeechRecognition)
    Linux     sudo apt install portaudio19-dev python3-pyaudio flac

Jika PyAudio tidak bisa dipasang, asr_demo.py tetap bisa diuji dari
berkas: python asr_demo.py --berkas jawab.wav


--------------------------------------------------------
5. MENJALANKAN APLIKASI
--------------------------------------------------------
Dari folder proyek:

    streamlit run dongeng_nusantara.py

Peramban terbuka di http://localhost:8501. Izinkan akses mikrofon.

Cara memakai:
    1. Pilih cerita, lalu tekan "Dengarkan".
    2. Dengarkan narator, lalu tekan "Aku siap menjawab".
    3. Tekan ikon mikrofon, ucapkan jawaban, lalu tekan berhenti.
    4. Sistem menilai jawaban dan memberi umpan balik: pujian,
       petunjuk bertingkat, lalu kunci jawaban pada percobaan ketiga.
    5. Setelah lima adegan, halaman "Tamat" menampilkan stiker dan
       catatan untuk guru.

Panel "Untuk guru dan orang tua" (bagian bawah halaman):
    - Batas lulus kecocokan (bawaan 0,75)
    - Tampilkan detail NLP
    - Ketik jawaban tanpa mikrofon (untuk demo atau jika mikrofon rusak)
    - Suara narator lebih pelan (15% lebih lambat)

Gangguan suara (rekaman hening, terpotong, tidak jelas, internet
putus) dibalas dengan pesan ramah, dan kesempatan anak tidak berkurang.


--------------------------------------------------------
6. MENJALANKAN TTS (tts_demo.py)
--------------------------------------------------------
Membaca segmen dari korpus/cerita/*.json (korpus yang sama dengan
aplikasi) lalu menyuarakannya.

    python tts_demo.py
    python tts_demo.py --daftar              (lihat id cerita dan segmen)
    python tts_demo.py --cerita malin --segmen 2
    python tts_demo.py --suara id-ID-ArdiNeural
    python tts_demo.py --rate -10 --pitch 5  (10% lebih lambat, nada +5 Hz)
    python tts_demo.py --mesin gtts          (pilihan: auto, edge, gtts, pyttsx3)
    python tts_demo.py --bandingkan          (tiga mesin, kalimat yang sama)
    python tts_demo.py --semua --tanpa-putar (pra-render seluruh korpus)

Nilai --rate dan --pitch berupa angka bertanda (-10, 5), tanpa "%" dan
"Hz". Id cerita: kancil, timun, malin. Tiap adegan satu segmen (1-5).

Hasil suara disimpan di folder suara/ sebagai MP3 dengan nama hash dari
teks, mesin, suara, rate, dan pitch. Teks yang sama tidak disintesis
ulang. Jika mesin utama gagal, program pindah ke cadangan otomatis.


--------------------------------------------------------
7. MENJALANKAN ASR (asr_demo.py)
--------------------------------------------------------
Memerlukan PyAudio untuk mikrofon (lihat bagian 4).

    python asr_demo.py                       (rekam dari mikrofon, id-ID)
    python asr_demo.py --durasi 8            (batas waktu menunggu suara)
    python asr_demo.py --ambang 300          (batas bawah ambang suara)
    python asr_demo.py --berkas jawab.wav    (uji dari berkas WAV)

Bicara setelah tulisan "[asr] Mendengarkan...". Hasil transkripsi
dicetak di layar. Jika mikrofon tidak tersedia, tidak ada ucapan, atau
internet putus, program mencetak pesan singkat dan keluar dengan rapi.


--------------------------------------------------------
8. PENGUJIAN
--------------------------------------------------------
    python pengujian/uji_sistem.py              evaluasi NLP + 36 uji unit,
                                                tanpa internet
    python pengujian/uji_sistem.py --langsung   tambah uji gTTS dan Google
                                                ASR sungguhan (butuh ffmpeg)

Hasil yang benar: "36 dari 36 uji lulus".


--------------------------------------------------------
9. MASALAH UMUM
--------------------------------------------------------
    - Suara narator terdengar datar
        : edge-tts gagal sehingga aplikasi memakai gTTS atau pyttsx3.
          Periksa internet, perbarui: python -m pip install -U edge-tts,
          dan pastikan jam komputer benar.
    - Galat "403 Invalid response status" atau "NoAudioReceived"
        : versi edge-tts lama, jam komputer tidak tepat, atau jaringan
          (proxy, VPN, kampus) memblokir layanan. Coba hotspot HP, atau
          pra-render audio dengan: python tts_demo.py --semua
    - Suara terdengar seperti berbahasa Inggris
        : pyttsx3 memakai suara sistem. Pasang paket bahasa Indonesia di
          Windows (Settings > Time & Language > Speech > Add voices).
    - Suara narator tidak otomatis berbunyi
        : peramban memblokir autoplay. Klik halaman, lalu tekan play.
    - Mikrofon tidak bisa dipakai di aplikasi
        : buka lewat http://localhost:8501. Dari komputer lain,
          peramban mewajibkan HTTPS untuk mikrofon.
    - Pesan "Mikrofon tidak tersedia" pada asr_demo.py
        : pasang PyAudio (requirements-demo.txt) atau sambungkan mikrofon.
    - Pesan "Alat pengenal suara belum lengkap"
        : di Mac Apple Silicon atau Linux ARM, pasang flac.
    - Pesan "Gagal menghubungi layanan pengenal suara"
        : periksa internet atau coba beberapa saat lagi.
    - pip gagal memasang streamlit
        : versi Python terlalu lama; minimal 3.11 (python --version).


--------------------------------------------------------
10. STATUS
--------------------------------------------------------
    [SELESAI] Aplikasi Streamlit: dongeng bersuara, 3 cerita, 15 adegan.
    [SELESAI] Penilaian jawaban dengan TF-IDF dan cosine similarity.
    [SELESAI] TTS: edge-tts, cadangan gTTS dan pyttsx3; tts_demo.py
              dengan cache dan pra-render.
    [SELESAI] ASR: Google Speech Recognition; asr_demo.py.
    [SELESAI] Penanganan gangguan suara (hening, terpotong, tidak jelas,
              internet putus) dan panel guru.
    [SELESAI] Pengujian: 36 uji unit dan evaluasi NLP.
    [RENCANA] Menu tema (Cerita Rakyat, Hewan, Buah), mode flashcard,
              animasi balik halaman seperti buku.
    [SELESAI] Semua tautan di docs/riset.md diperiksa ulang oleh
              kelompok.