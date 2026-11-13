========================================================
 KUIS INTERAKTIF BELAJAR BAHASA INDONESIA BERBASIS SUARA
 Tugas Pemrograman Akhir NLP (Tugas A) - Progres Minggu 1
========================================================

Isi arsip minggu 1:
    ReadMe.txt              berkas ini
    tts_demo.py             prototipe Text-to-Speech (narator)
    asr_demo.py             prototipe Automated Speech Recognition (jawaban lisan)
    requirements.txt        daftar pustaka Python
    korpus/cerita/*.json    SATU-SATUNYA sumber cerita: 3 cerita, 15 adegan
    docs/riset.md           riset belajar bahasa anak usia dini
    docs/keputusan-teknis.md  perbandingan pustaka TTS/ASR/UI
    docs/sketsa-ui.md       sketsa 4 layar antarmuka (rencana minggu 2-3)

Minggu 1 hanya menguji TTS dan ASR secara terpisah. Belum ada alur dialog
penuh, penilaian jawaban, atau penanganan kesalahan suara.


--------------------------------------------------------
1. ANGGOTA KELOMPOK
--------------------------------------------------------
    1. 71230975 - Thomas Aquinas Ryan Wisnu Adi
    2. 71230994 - Putu Gde Kenzie Carlen Mataram
    3. 71231023 - Yehezkiel Darren Putra Wardoyo


--------------------------------------------------------
2. SYARAT
--------------------------------------------------------
    - Python 3.9 atau lebih baru (sudah diuji di Python 3.13).
    - Mikrofon untuk asr_demo.py.
    - Sambungan internet untuk suara gTTS dan pengenalan Google.
    - Windows, macOS, atau Linux.


--------------------------------------------------------
3. MEMASANG PUSTAKA
--------------------------------------------------------
Buka terminal di folder berkas ini, lalu jalankan:

    pip install -r requirements.txt

Isi requirements.txt (semua yang dibutuhkan proyek, termasuk aplikasi):
    streamlit, gTTS, pyttsx3, SpeechRecognition, PyAudio,
    scikit-learn, numpy

Atau pasang satu per satu:

    pip install streamlit gTTS pyttsx3 SpeechRecognition PyAudio scikit-learn numpy

Untuk minggu 1 saja, cukup: gTTS, pyttsx3, SpeechRecognition, PyAudio.
Streamlit, scikit-learn, dan numpy baru dipakai antarmuka dan penilaian.
Dua cadangan bila PyAudio gagal terpasang:
    - Pengenalan suara tetap bisa diuji dari berkas: python asr_demo.py --berkas jawab.wav
    - Di minggu 2-3, aplikasi merekam lewat peramban (st.audio_input), tanpa PyAudio.

Catatan per sistem:
    Windows   PyAudio biasanya langsung terpasang. Jika gagal, coba:
              pip install pipwin  lalu  pipwin install pyaudio
    macOS     pip install pyaudio
              brew install flac        (dibutuhkan SpeechRecognition)
    Linux     sudo apt install portaudio19-dev python3-pyaudio flac


--------------------------------------------------------
4. MENJALANKAN TTS (tts_demo.py)
--------------------------------------------------------
Perintah dasar (membaca segmen 1 cerita Si Kancil dan Buaya):

    python tts_demo.py
    python tts_demo.py --daftar                (lihat id cerita, jumlah segmen, berkas)

Contoh lain:
    python tts_demo.py --cerita malin --segmen 2
    python tts_demo.py --pelan                 (gTTS: suara lebih lambat)
    python tts_demo.py --mesin pyttsx3 --laju 130
    python tts_demo.py --tanpa-putar           (simpan saja, tidak diputar)

Id cerita (diambil dari nama berkas): kancil, timun, malin.
Berkas dibaca dari korpus/cerita/*.json, sumber cerita yang sama dengan aplikasi.
Tiap adegan dihitung sebagai satu segmen (1-5).
Hasil suara disimpan di folder suara/ lalu diputar dengan pemutar sistem.
Jika internet putus, program otomatis mencoba pyttsx3 (luring).


--------------------------------------------------------
5. MENJALANKAN ASR (asr_demo.py)
--------------------------------------------------------
Perintah dasar (merekam dari mikrofon, bahasa Indonesia):

    python asr_demo.py

Contoh lain:
    python asr_demo.py --durasi 6            (batas waktu menunggu suara 6 detik)
    python asr_demo.py --ambang 300          (batas bawah ambang suara)
    python asr_demo.py --berkas jawab.wav    (uji tanpa mikrofon, dari berkas WAV)

Cara kerja ambang: program mengukur kebisingan ruangan selama --penyetelan
detik (bawaan 1.0), lalu memakai hasil ukur itu sebagai ambang, tanpa turun
di bawah nilai --ambang. Hasil ukur dicetak di layar.

Bicara setelah tulisan "[asr] Mendengarkan...". Hasil transkripsi dicetak
di layar. Jika mikrofon tidak tersedia, tidak ada ucapan, atau internet
putus, program mencetak pesan singkat dan keluar dengan rapi.


--------------------------------------------------------
6. MEMERIKSA KORPUS
--------------------------------------------------------
Untuk memastikan korpus/cerita/*.json valid sebagai JSON:

    python tts_demo.py --daftar

Hasil yang benar: tiga baris (kancil, timun, malin), masing-masing 5 segmen.


--------------------------------------------------------
7. MASALAH UMUM
--------------------------------------------------------
    - gTTS gagal / lambat          : periksa internet, lalu coba --mesin pyttsx3.
    - Suara terdengar seperti berbahasa Inggris
                                   : pyttsx3 memakai suara sistem; pasang paket
                                     bahasa Indonesia di Windows (Settings >
                                     Time & Language > Speech > Add voices).
    - Pesan "Mikrofon tidak tersedia"
                                   : pasang PyAudio atau sambungkan mikrofon.
    - Pesan "Gagal menghubungi layanan pengenal suara"
                                   : periksa internet atau coba beberapa saat lagi.


--------------------------------------------------------
8. STATUS MINGGU 1
--------------------------------------------------------
    [SELESAI] tts_demo.py membacakan segmen cerita dalam bahasa Indonesia.
    [SELESAI] asr_demo.py merekam dan mencetak teks hasil pengenalan suara.
    [SELESAI] korpus/cerita/*.json berisi 3 cerita dan valid sebagai JSON;
              tts_demo.py membaca korpus yang sama dengan aplikasi.
    [SELESAI] docs/riset.md, docs/keputusan-teknis.md, docs/sketsa-ui.md.
    [BELUM]   Alur dialog penuh, pencocokan jawaban, penanganan kesalahan
              dan antarmuka (minggu 2-3).
    [PERLU DIPERIKSA] Semua tautan di docs/riset.md diperiksa ulang oleh kelompok.