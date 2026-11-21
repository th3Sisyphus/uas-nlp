Semua angka kontras di bawah saya hitung dengan rumus WCAG. Ukuran dan durasi adalah patokan praktis, bukan aturan baku, jadi uji dengan anak sungguhan jika bisa.

## 1. Bentuk tulisan

| Aturan | Nilai |
|---|---|
| Huruf | Bulat, terbuka, mudah dibedakan. Judul: Fredoka atau Baloo 2. Teks cerita: Nunito atau Andika (setahu saya Andika dirancang untuk belajar membaca; cek sendiri). Cadangan: Verdana, sans-serif |
| Ukuran | Teks cerita ≥ 24 px, judul 36–48 px, label tombol ≥ 20 px. Tidak ada teks di bawah 16 px, kecuali panel guru |
| Tinggi baris | 1,5–1,6 |
| Lebar baris | Maksimal 40–45 karakter, rata kiri, tidak rata kiri-kanan |
| Penekanan | Pakai warna latar atau sorot kata, bukan huruf miring, garis bawah, atau SEMUA KAPITAL |
| Panjang | Satu layar 2–3 kalimat, tiap kalimat 8–10 kata |

Font Google butuh internet, jadi selalu pasang cadangan.

## 2. Perpaduan warna

| Peran | Warna | Dipakai untuk | Kontras |
|---|---|---|---|
| Teks | `#2B2250` | Semua teks utama | 14,5:1 di atas putih |
| Latar | `#FFF8E7` (krem) | Latar halaman | teks 13,7:1 |
| Utama | `#6B3FD4` (ungu) | Tombol utama, judul | teks putih 6,4:1 |
| Aksen | `#FFD23F` (kuning) | Bintang, sorotan | teks gelap 10:1 |
| Benar | `#8FE3B4` (hijau muda) | Umpan balik benar | teks gelap 9,5:1 |
| Petunjuk | `#FFB74D` (oranye muda) | Hint dan hampir benar | teks gelap 8,4:1 |
| Ulang | `#FFC9DE` (merah muda) | "Coba lagi" | teks gelap 10,1:1 |
| Info | `#CFE8FF` (biru muda) | Penjelasan | teks gelap 11,5:1 |

- Maksimal 3–4 warna dominan per layar, latar terang, warna cerah tapi tidak neon.
- Teks biasa butuh kontras ≥ 4,5:1, teks besar ≥ 3:1.
- Jangan pakai teks putih di atas hijau `#1E8E5A` (4,1), oranye `#E8590C` (3,6), atau biru `#2B7DE9` (4,0). Semua di bawah 4,5.
- Jangan pernah teks putih di atas kuning.
- Jangan hanya mengandalkan warna. Benar dan salah ditandai juga dengan ikon (bintang, tepuk tangan) dan suara.
- Jawaban salah: tidak pakai merah murni atau tanda silang. Warna lembut dan kalimat positif.

## 3. Ukuran komponen

- Target sentuh minimal **64×64 px** (patokan orang dewasa 44–48 px, anak butuh lebih besar). Tombol utama 80–96 px. Tombol mikrofon bulat 96–120 px.
- Jarak antar tombol ≥ 16 px. Satu tombol utama per layar, tombol sekunder lebih kecil dan jauh darinya, supaya tidak tertekan tak sengaja.
- Sudut membulat 16–24 px, garis tepi 3–4 px, tidak ada elemen tipis.
- Ikon ≥ 32 px dan diberi label pendek.
- Gambar flashcard minimal 40% tinggi layar.
- Beranda maksimal 3 pilihan (tiga tema). Aksi utama tidak boleh butuh scroll. Jangan bergantung pada hover.

## 4. Sedikit teks, banyak gambar, animasi, dan suara

- Satu layar satu ide, teks maksimal sekitar 20–25 kata.
- Urutan petunjuk: gambar, lalu suara, lalu teks. Instruksi lewat suara dan ikon (mikrofon berdenyut berarti "ayo bicara").
- Semua teks penting punya tombol "dengar lagi".
- Umpan balik berupa bintang atau stiker plus suara pujian. Skor angka hanya di panel guru.
- Efek suara benar pendek (kurang dari 1 detik). Tidak ada bunyi buzzer atau suara kecewa. Sediakan tombol bisu.
- Narator tidak berbicara bersamaan dengan mikrofon aktif.
- Kesalahan teknis bukan salah anak: "Wah, suaranya kurang terdengar..." dan tidak mengurangi percobaan. Tidak ada penghitung waktu yang menekan.

## 5. Animasi secukupnya

- Animasi punya tujuan: menunjukkan yang bisa ditekan, memperlihatkan hasil, atau transisi. Bukan hiasan.
- Durasi: umpan balik tombol 150–250 ms, pergantian elemen 300–400 ms, balik halaman 500–700 ms.
- Maksimal satu animasi aktif sekaligus, dan satu elemen yang bergerak terus (denyut mikrofon, berhenti saat selesai).
- Gerak lembut (ease-out). Tanpa memantul berlebihan, getar, atau kilat. Tidak ada kedipan lebih dari 3 kali per detik.
- Hormati `prefers-reduced-motion` (ganti jadi fade atau instan), dan beri tombol "Kurangi gerak" di panel guru.
- Animasikan hanya `transform` dan `opacity` agar ringan di laptop demo.
- Mulai TTS setelah animasi selesai (sekitar 0,5–0,8 detik).
- Three.js: satu objek, model di bawah 2 MB, dengan cadangan 2D.

## Token CSS siap pakai
```css
:root {
  --teks: #2B2250;   --latar: #FFF8E7;
  --utama: #6B3FD4;  --aksen: #FFD23F;
  --benar: #8FE3B4;  --petunjuk: #FFB74D;
  --ulang: #FFC9DE;  --info: #CFE8FF;
  --target-min: 64px; --tombol-utama: 88px; --jarak: 16px;
  --radius: 20px;    --garis: 3px;
  --fs-cerita: 1.5rem; --fs-judul: 2.5rem; --lh: 1.6;
  --dur-tombol: 200ms; --dur-ganti: 350ms; --dur-halaman: 600ms;
}
@media (prefers-reduced-motion: reduce) {
  * { animation: none !important; transition-duration: 1ms !important; }
}
```

Mau saya simpan sebagai `docs/aturan-desain.md` (siap ditempel ke prompt AI), atau jadikan daftar centang untuk menilai tiap layar?