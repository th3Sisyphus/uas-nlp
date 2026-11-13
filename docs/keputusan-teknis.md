# Keputusan Teknis: Pustaka dan Antarmuka

Dokumen ini membandingkan pilihan pustaka untuk prototipe minggu 1, lalu
memberi **usulan** rekomendasi. Keputusan akhir tetap ada di tangan kelompok.

## 1. Text-to-Speech (TTS)

| Aspek | `gTTS` | `pyttsx3` |
|---|---|---|
| Kelebihan | Suara bahasa Indonesia (`lang="id"`) jelas dan alami; hasil berupa MP3 yang mudah diputar/diunduh; ada pengaturan lambat (`slow=True`) | Berjalan luring (tanpa internet); langsung berbunyi dari speaker; ada pengaturan kecepatan (`rate`) dan volume |
| Kekurangan | Butuh internet setiap kali membuat suara; lama menunggu bergantung jaringan; tidak bisa mengatur kecepatan selain normal/lambat | Suara bergantung sistem operasi. Di Windows yang terpasang umumnya suara **Microsoft SAPI** tanpa paket bahasa Indonesia, sehingga kata Indonesia dilafalkan dengan aksen Inggris; di Linux sering butuh `espeak`/`espeak-ng` |
| Internet | Wajib | Tidak perlu |
| Ramah anak | Baik: pelafalan Indonesia jelas, kalimat bisa diulang | Bergantung perangkat; bisa terdengar aneh dan membingungkan anak |
| Mudah didemokan | Perlu jaringan kelas/warnet yang stabil | Tidak bisa diandalkan untuk demo antar perangkat karena tiap laptop berbeda |
| Pengaturan kecepatan | `slow=True` (dua pilihan) | `rate` dalam kata/menit (rentang lebih luas) |

**Usulan: `gTTS` sebagai mesin utama, `pyttsx3` sebagai cadangan.**

Alasan: (1) tujuan minggu 1 adalah *membuktikan TTS berbahasa Indonesia berbunyi
benar*, dan pelafalan yang jelas lebih penting daripada kemampuan luring;
(2) `pyttsx3` tetap dipakai supaya demo tidak mati total saat internet putus.
Keduanya sudah diuji di `tts_demo.py` (opsi `--mesin gtts` / `--mesin pyttsx3`).
Catatan pengujian: pada komputer pengembang, `pyttsx3` hanya menemukan suara
Inggris, sehingga skrip mencetak peringatan bahwa suara Indonesia belum terpasang.

## 2. Automated Speech Recognition (ASR)

| Aspek | `SpeechRecognition` + Google | Whisper |
|---|---|---|
| Kelebihan | Kode paling pendek (`recognize_google(..., language="id-ID")`); tidak perlu unduh model; akurasi bahasa Indonesia cukup baik di internet biasa; bisa mengambil beberapa tebakan sekaligus (`show_all=True`) | Luring; akurasi tinggi; bisa memakai model kecil (`tiny`/`base`) agar ringan |
| Kekurangan | Butuh internet; kuota/penggunaan API gratis tanpa jaminan; rekaman dikirim ke layanan Google | Perlu memasang `openai-whisper` + `torch`/`ffmpeg` (unduhan besar, ratusan MB); di laptop tanpa GPU, transkripsi lambat; instalasi sering gagal di Windows |
| Internet | Wajib | Tidak perlu (setelah model diunduh) |
| Ramah anak | Cukup; respons cepat (1–3 detik) sehingga anak tidak bosan menunggu | Respons bisa lambat di laptop kelas sehingga anak mengulang-ulang jawaban |
| Mudah didemokan | Cukup: satu `pip install` | Berisiko: unduhan besar dan variabel CUDA/ffmpeg |
| Bahasa Indonesia | Terbuka langsung lewat `language="id-ID"` | Didukung model multibahasa, tetapi tidak ada kode bahasa sederhana |

**Usulan: `SpeechRecognition` + Google (`language="id-ID"`).**

Alasan: instalasinya ringan (`SpeechRecognition` + `PyAudio`), kodenya pendek
sehingga mudah dijelaskan saat demo, dan sudah diuji berjalan di `asr_demo.py`
pada komputer pengembang. Whisper tetap dicatat sebagai **rencana cadangan
luring** jika internet kelas tidak stabil pada minggu 3.

## 3. Antarmuka (UI)

| Aspek | Tkinter | Streamlit | Gradio |
|---|---|---|---|
| Kelebihan | Sudah bawaan Python; aplikasi desktop; tanpa server web | Widget siap pakai (`st.audio_input`, `st.audio`) sehingga mikrofon peramban langsung bisa direkam; tata letak cepat diubah; CSS bisa ditambahkan | Komponen audio/mikrofon bawaan; sangat cepat untuk demo; mudah dibagikan lewat tautan |
| Kekurangan | Tombol besar, warna, dan gambar harus dibuat manual; merekam suara butuh pustaka tambahan; tampilan terasa "kaku" | Perlu peramban dan server lokal; mikrofon hanya berfungsi di `localhost` atau HTTPS; menjalankan ulang skrip setiap interaksi | Tata letak kurang bebas; tampilan sulit disesuaikan untuk anak; mikrofon juga butuh HTTPS saat dibagikan |
| Internet | Tidak perlu | Tidak perlu untuk server lokal, tetapi gTTS/Google ASR perlu | Sama seperti Streamlit |
| Ramah anak | Bisa, tetapi butuh banyak kerja desain | Baik, dengan CSS dan gambar besar | Cukup, tetapi tampilannya lebih "alat demo" daripada "permainan" |
| Mudah didemokan | Perlu perangkat siap (tanpa pemasangan pustaka web) | Satu perintah `streamlit run` | Satu perintah `python app.py` |

**Usulan: Streamlit untuk antarmuka penuh di minggu 2–3**, karena
`st.audio_input` merekam suara langsung dari peramban sehingga **tidak perlu
PyAudio** di sisi anak, dan hasil TTS mudah diputar dengan `st.audio`.

Catatan untuk minggu 1: antarmuka belum dibuat. `tts_demo.py` dan `asr_demo.py`
sengaja berupa skrip terminal sesuai lingkup minggu 1. Pada `asr_demo.py`,
PyAudio tetap diperlukan karena rekaman diambil lewat mikrofon komputer.

## 4. Ringkasan rekomendasi

| Bagian | Rekomendasi | Cadangan | Alasan utama |
|---|---|---|---|
| TTS | `gTTS` | `pyttsx3` | Pelafalan bahasa Indonesia jelas; cadangan luring agar demo tidak mati |
| ASR | `SpeechRecognition` + Google (`id-ID`) | Whisper `base` (luring) | Instalasi ringan, kode pendek, respons cepat |
| UI | Streamlit | Tkinter | Rekaman mikrofon lewat peramban tanpa PyAudio di sisi pengguna |

Pemasangan untuk pilihan di atas:

```bash
pip install gTTS pyttsx3 SpeechRecognition PyAudio
# UI (mulai minggu 2): pip install streamlit
```

## 5. Keputusan akhir kelompok

> Diisi setelah kelompok berdiskusi. Contoh format: "Kami memilih gTTS + Google
> ASR + Streamlit karena ... (alasan)."

- TTS: [KEPUTUSAN KELOMPOK]
- ASR: [KEPUTUSAN KELOMPOK]
- UI: [KEPUTUSAN KELOMPOK]