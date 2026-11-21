# Aturan Korpus Cerita Rakyat

Dipakai semua prompt di folder `prompt-cerita/`. Letakkan di `docs/cerita-rakyat/ATURAN.md`, bersama `validasi.py`.

Proyek: aplikasi kuis cerita berbasis suara untuk anak **usia 4-6 tahun**. Satu berkas JSON = satu cerita. Berkas disimpan di `docs/cerita-rakyat/` (draf). Aplikasi baru memuatnya setelah disalin ke `korpus/cerita/`.

## Nama berkas
`NN_kode.json` (contoh `14_sangkuriang.json`). Kode: huruf kecil, tanpa spasi, unik.

## Format (UTF-8, indentasi 1 spasi, `ensure_ascii=False`)
```json
{
 "judul": "Bawang Merah dan Bawang Putih",
 "asal": "Cerita rakyat Nusantara",
 "ajaran": "Rajin dan baik hati itu menyenangkan.",
 "warna": {"dunia": "#E0559C", "aksen": "#FFE14D", "kartu": "#FFB3D1"},
 "adegan": [
  {
   "narasi": "Suatu hari, Bawang Putih mendapat hadiah. Hadiahnya sebuah labu. Dia membawa labu itu pulang dengan senang.",
   "tanya": "Apa hadiah untuk Bawang Putih?",
   "kunci": ["labu", "sebuah labu"],
   "utama": "labu",
   "petunjuk": "Buahnya besar, berwarna jingga, dan sering dibuat sup.",
   "stiker": "🎃",
   "gambar": {"latar": "ladang", "objek": [
     {"emoji": "👧", "x": 260, "y": 330, "ukuran": 150},
     {"emoji": "🎃", "x": 640, "y": 360, "ukuran": 170}]}
  }
 ]
}
```

## Aturan isi
- **Adegan:** 4 (boleh 3-5), sesuai urutan kejadian di `isi` korpus.
- **`narasi`:** 3-4 kalimat, **maksimal 10 kata per kalimat**, kata sehari-hari.
- **`tanya`:** satu per adegan. Jawabannya 1-3 kata dan **tertulis di `narasi` adegan itu**.
- **`kunci`:** 1-4 jawaban (disarankan 2-4), huruf kecil, tanpa tanda baca. `utama` = `kunci[0]`.
- **`petunjuk`:** maksimal 10 kata, memberi ciri tanpa menyebut jawaban.
- **`stiker`:** satu emoji. Hindari emoji baru (lebih baru dari 2020) dan senjata tajam.
- **`ajaran`:** 1-2 kalimat positif.
- **`asal`:** isi hanya jika yakin. Jika ragu, tulis "Cerita rakyat Nusantara". Semua `asal` yang kamu isi dicatat sebagai "perlu diverifikasi".
- **`warna`:** tiga kode HEX. `dunia` jenuh, `aksen` terang, `kartu` versi muda.

## Aturan gambar (kanvas 960 x 480)
- **`latar`:** `sungai`, `senja`, `ladang`, `bambu` (hutan), `lumpur`, `pantai`, `dermaga`, `badai`, `polos`. Tidak ada latar malam atau gunung, pakai yang terdekat.
- **Objek emoji:** `{"emoji": "🐍", "x": 740, "y": 340, "ukuran": 170}`; `"cermin": true` membalik gambar. `x` 60-900, `y` 60-440.
- **Objek bawaan:** `{"gambar": "batu", "x": 480, "y": 380, "skala": 1.3}`. Pilihan: `batu`, `pohon`, `kancil`, `rambutan`.
- Tokoh utama `ukuran` 130-160 di `y` sekitar 330, tokoh kanan memakai `"cermin": true`. Simbol kecil `ukuran` 70-110 di `y` 100-250. Maksimal 5 objek per adegan.

## Aturan ramah anak
- **Terlarang** (validator menggagalkan): membunuh, mati, meninggal, tewas, dikubur, dibakar, disiksa, mengintip, judi, merampok, korban, dendam, durhaka.
- **Hindari** (validator memberi peringatan): kutukan, perang.
- Hilangkan juga: kekerasan, hubungan romantis dengan ibu, mengorbankan anak, adu hewan, bunuh diri atau melompat untuk mengakhiri hidup. Ganti dengan akibat lembut: berubah menjadi batu, patung, burung, pulau, danau, gunung; pergi; menyesal; kecewa.
- Pertahankan inti cerita dan nama asal-usul tempat. Tutup dengan pelajaran positif.
- **Maksimal satu penyesuaian per cerita**, wajib dicatat.
- Jika tidak bisa dilunakkan tanpa merusak alur, **jangan buat berkasnya**. Catat sebagai "dilewati" beserta alasannya.

## Catatan kerja (`docs/cerita-rakyat/catatan.md`)
Tambahkan di akhir (jangan hapus isi lama), satu blok per cerita:
```
## <judul> (<berkas>)
- Status: dibuat | dilewati
- Penyesuaian: <apa yang dihilangkan atau diganti, atau alasan dilewati>
- Asal: <isi kolom asal> (perlu diverifikasi)
```

## Cara kerja hemat token
- Baca berkas ini **satu kali**. Jangan membaca ulang berkas hasil tulisanmu sendiri.
- Tulis semua berkas satu batch dengan **satu skrip Python generator** (`json.dump`).
- Validasi: `python docs/cerita-rakyat/validasi.py`. Jika ada GALAT, perbaiki dengan satu skrip lalu jalankan ulang **satu kali**.
- Jangan mengubah kode aplikasi atau `korpus/cerita/`. Hanya bekerja di `docs/cerita-rakyat/`.