**Alur utama**
1. Halaman awal: menu tema (**Cerita Rakyat**, **Hewan**, **Buah**).
2. Anak memilih tema, lalu masuk mode yang sesuai.

**Tema 1: Cerita Rakyat**
- Banyak pilihan cerita (Kancil, Timun Mas, Malin Kundang, dan tambahan).
- Interaksi **tidak diubah**: TTS bercerita, TTS bertanya, anak menjawab lewat ASR, sistem mencocokkan.
- Tampilan seperti buku bacaan anak. Pindah halaman dengan animasi balik halaman.

**Tema 2 dan 3: Hewan dan Buah (mode flashcard)**
- Satu kartu menampilkan gambar (misalnya apel), tulisan "apel", dan suara TTS "apel".
- Anak diminta menyebutkan kata ke mikrofon.
- ASR mencocokkan ucapan dengan kata target, lalu TTS memberi umpan balik.
- Lanjut ke kartu berikutnya.

**Penanganan kesalahan (bonus 3 poin)**
- Suara kurang jelas, terpotong, atau tidak dimengerti: TTS menjawab "Wah, suaranya kurang terdengar, coba bilang sekali lagi yuk!"
- Berlaku di mode cerita dan flashcard.

## Catatan agar realistis

- **Inti nilai tetap cerita + TTS + ASR.** Flashcard memakai komponen yang sama, jadi murah dibuat. Kerjakan setelah alur cerita stabil.
- **Korpus flashcard terpisah:** `korpus/flashcard/hewan.json` dan `buah.json`, berisi kata, berkas gambar, variasi ucapan, dan hint. Mulai kecil, misalnya 5–8 kartu per tema.
- **ASR untuk satu kata paling rawan.** Kata pendek ("apel") sering salah dikenali pada suara anak. Pakai fuzzy match dan daftar variasi ejaan, dan siapkan tombol "lanjut" bila gagal 3 kali.
- **Gambar:** pakai gambar buatan sendiri atau berlisensi bebas (CC0), dan catat sumbernya di dokumen.
- **Animasi buku** cukup dengan CSS (efek putar halaman). Ini poles, jadi terakhir.
- Perbarui `docs/sketsa-ui.md`: tambah layar menu tema dan layar flashcard.

Urutan kerja yang saya sarankan: menu tema, lalu mode flashcard, lalu pesan kesalahan, lalu animasi buku.