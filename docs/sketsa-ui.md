# Sketsa Antarmuka Kuis Suara (4 Layar)

Sketsa ini adalah rancangan untuk minggu 2–3. Minggu 1 hanya membuktikan TTS
dan ASR berjalan sendiri-sendiri lewat `tts_demo.py` dan `asr_demo.py`.
Ukuran gambar 960 × 480 dipakai untuk ilustrasi adegan, dan tombol utama
memakai ukuran minimal lebar 240 px dengan tinggi 72 px.

Prinsip umum (lihat `docs/riset.md`):

- **Satu aksi utama per layar**, dengan tombol paling besar untuk aksi itu.
- **Kalimat pendek**, maksimal dua baris di layar.
- **Umpan balik positif lebih dulu**, tidak ada kata "salah" atau hukuman.
- **Warna cerah tetapi tidak ramai**, satu warna dunia per cerita.

---

## Layar 1 — Pilih cerita

```
+--------------------------------------------------------------+
|                                                              |
|      (  )            Panggung Dongeng Nusantara              |
|      (__)     "Ayo pilih cerita hari ini!"  [DENGAR]         |
|                                                              |
|  +----------------+  +----------------+  +----------------+  |
|  |                |  |                |  |                |  |
|  |      [GAMBAR   |  |      [GAMBAR   |  |      [GAMBAR   |  |
|  |       KANCIL]  |  |       TIMUN]   |  |       KAPAL]   |  |
|  |                |  |                |  |                |  |
|  | Si Kancil dan  |  |    Timun Mas   |  |  Malin Kundang |  |
|  |     Buaya      |  |                |  |                |  |
|  | 3 pertanyaan   |  | 3 pertanyaan   |  | 3 pertanyaan   |  |
|  |  [ PILIH ]     |  |  [ PILIH ]     |  |  [ PILIH ]     |  |
|  +----------------+  +----------------+  +----------------+  |
|        (warna tosca)   (warna kuning)     (warna biru laut)  |
+--------------------------------------------------------------+
```

**Alasan desain**

- Tiga kartu besar sekaligus, tanpa menu bertingkat: anak 4–6 tahun mudah
  bingung jika harus membuka banyak halaman.
- Isi kartu berupa gambar besar, bukan teks panjang, karena anak mungkin
  belum lancar membaca. Judul cerita tetap ada supaya orang tua bisa membantu.
- Tombol **DENGAR** di atas ikut membacakan instruksi, jadi anak yang belum
  bisa membaca tetap tahu harus melakukan apa.

---

## Layar 2 — Baca/dengar cerita

```
+--------------------------------------------------------------+
|  [< Kembali]                          Cerita 1 dari 3        |
|                                                              |
|  +--------------------------------------------------------+  |
|  |                                                        |  |
|  |                  [ GAMBAR ADEGAN 960x480 ]             |  |
|  |                     Kancil di tepi sungai              |  |
|  |                                                        |  |
|  +--------------------------------------------------------+  |
|                                                              |
|      "Si Kancil lapar sekali. Ia berjalan ke tepi sungai."   |
|                                                              |
|      ( (o))  DENGAR LAGI     (>>)  Aku siap menjawab         |
|      tombol besar, warna cerah                               |
+--------------------------------------------------------------+
```

**Alasan desain**

- Narasi tampil sebagai **teks sekaligus suara**, supaya anak mendengar dan
  melihat kata yang sama (mendengar + melihat memperkuat kosakata).
- **Dengarkan lagi** selalu tersedia: anak boleh mengulang sebanyak apa pun
  tanpa kehilangan poin. Ini wujud prinsip "tidak ada hukuman".
- Tombol "Aku siap menjawab" baru muncul setelah narator selesai, agar anak
  tidak terburu-buru.

---

## Layar 3 — Jawab pertanyaan

```
+--------------------------------------------------------------+
|  [< Kembali]                          Pertanyaan 1 dari 3    |
|                                                              |
|      "Buah apa yang ada di seberang sungai?"                 |
|      (kalimat pendek, maksimal dua baris)                    |
|                                                              |
|                    ( ( (  MIKROFON  ) ) )                    |
|                    |        O         |                      |
|                    |   TEKAN & BICARA |   <- tombol 240x240 |
|                    |                  |                      |
|                    ~~~ gelombang suara bergerak ~~~          |
|                [ MEREKAM... tekan untuk selesai ]            |
|                                                              |
|      (?) BERI PETUNJUK        ( ) DENGAR LAGI                |
+--------------------------------------------------------------+
```

Saat anak menekan mikrofon:

```
+--------------------------------------------------------------+
|            [ MENDENGARKAN...  o o o o o ]                    |
|            Anak bicara. Lingkaran berdenyut lembut.          |
|                                                              |
|            [ Selesai ]  (tombol berhenti, besar)             |
+--------------------------------------------------------------+
```

**Alasan desain**

- Satu tombol raksasa di tengah: aksi utama layar ini hanya satu, yaitu
  menjawab. Tombol kecil seperti ikon mikrofon kecil sulit ditekan anak.
- **Indikator merekam** berupa lingkaran berdenyut dan tulisan "MENDENGARKAN",
  supaya anak tahu kapan harus bicara dan kapan harus berhenti.
- Tombol **PETUNJUK** memakai ikon tanda tanya dan warna lembut, bukan merah,
  agar tidak terkesan "kesalahan". Petunjuk dibacakan dengan suara.
- Jika suara tidak jelas, pesannya ramah ("Maaf, suaramu belum terdengar jelas,
  yuk coba ucapkan lagi!") dan **jumlah percobaan tidak berkurang**.

---

## Layar 4 — Hasil dan skor

```
+--------------------------------------------------------------+
|                                                              |
|      ( )  HEBAT! Kamu sudah menjawab semua pertanyaan!       |
|                                                              |
|      +--------------------------------------------+          |
|      |           BINTANG KAMU                     |          |
|      |      *   *   *      (3 pertanyaan)         |          |
|      |   (kartu besar, warna cerah, berkilau)     |          |
|      +--------------------------------------------+          |
|                                                              |
|      Pertanyaan 1   Buah rambutan            (v)             |
|      Pertanyaan 2   Buaya                    (v)             |
|      Pertanyaan 3   Seperti jembatan         (v)             |
|                                                              |
|      ( (o)) DENGAR LAGI      (<<) Pilih cerita lain          |
+--------------------------------------------------------------+
```

**Alasan desain**

- Umpan balik dibuka dengan **pujian**, tanpa kata "salah". Skor ditampilkan
  sebagai **bintang/kartu**, bukan nilai angka, karena angka mudah
  dibandingkan dan bisa membuat anak kecewa.
- Hasil tiap pertanyaan ditampilkan hanya sebagai centang. Jawaban yang butuh
  bantuan tetap mendapat centang, karena anak sudah berusaha.
- Seluruh hasil **dibacakan** agar anak yang belum bisa membaca tetap tahu
  hasilnya, dan ada tombol untuk pindah cerita tanpa merasa gagal.

---

## Catatan teknis untuk minggu 2–3

| Bagian | Rencana penerapan |
|---|---|
| Narasi + TTS | `modul/tts.py` → `gTTS`, diputar dengan `st.audio` |
| Rekaman anak | `st.audio_input`, tidak perlu PyAudio di sisi anak |
| Indikator merekam | Ikon 🔴 dan tulisan "MENDENGARKAN" selama proses rekaman |
| Tombol hint | Ambil `hint` dari `korpus/cerita.json` lalu bacakan dengan TTS |
| Umpan balik | Pujian + petunjuk bertingkat, lalu kunci jawaban dibacakan |
| Uji pada anak | Minta 1–2 anak mencoba; amati apakah tombol mudah ditekan |