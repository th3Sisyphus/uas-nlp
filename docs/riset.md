# Riset Singkat: Belajar Bahasa Anak Usia Dini

Dokumen ini menjadi dasar desain kuis suara untuk anak. Dua aturan penulisan:

1. Sumber hanya dicantumkan jika kami yakin sumber itu nyata.
2. Sumber atau angka yang belum kami periksa sendiri ditandai **[perlu diverifikasi]**.

## 1. Siapa sasaran kita, dan bagaimana anak belajar bahasa

**Rentang usia sasaran: 4–7 tahun.** Pada usia ini anak sudah bisa berbicara
dalam kalimat sederhana, tetapi kosakata dan struktur kalimatnya masih
berkembang. Karena itu narasi dan pertanyaan kita dibuat 1–3 kalimat pendek
(lihat `korpus/cerita.json`). [perlu diverifikasi]

Anak belajar bahasa terutama melalui dua hal:

- **Mendengar orang dewasa berbicara.** Kosakata baru masuk dari percakapan
  dan cerita yang dibacakan, bukan dari hafalan daftar kata. [perlu diverifikasi]
- **Berbicara dan mendapat tanggapan.** Ketika anak mengucapkan sesuatu dan
  orang dewasa merespons, anak belajar bahwa bicaranya punya arti. Inilah alasan
  kuis ini memakai **jawaban lisan**, bukan tombol pilihan ganda.
  [perlu diverifikasi]

## 2. Peran cerita dalam belajar bahasa anak

Cerita membantu anak belajar bahasa karena:

- **Kata baru muncul berulang** dalam konteks yang mudah dibayangkan
  ("Kancil melompat ke punggung buaya"), sehingga lebih mudah diingat.
  [perlu diverifikasi]
- **Alur cerita memberi urutan peristiwa.** Anak berlatih kata urutan dan
  hubungan sebab-akibat (lalu, karena, sesudah). [perlu diverifikasi]
- **Cerita rakyat memberi nilai moral** yang mudah ditangkap anak, misalnya
  minta maaf (Kancil) atau kasih sayang ibu (Malin Kundang, Timun Mas).
  [perlu diverifikasi]
- **Cerita mengundang pertanyaan.** Bertanya "apa yang terjadi selanjutnya?"
  atau "siapa yang menolong?" adalah cara alami melatih daya ingat dan bicara.
  [perlu diverifikasi]

## 3. Prinsip desain aplikasi untuk anak (dan wujudnya di sistem ini)

| Prinsip | Alasan | Wujud di proyek |
|---|---|---|
| Kalimat pendek, satu ide per kalimat | Anak mudah kehilangan inti kalimat panjang | Tiap segmen 2–3 kalimat; tiap segmen satu pertanyaan |
| Suara jelas, pelan, bisa diulang | Anak butuh mendengar ulang tanpa rasa malu | Tombol "Dengar lagi"; opsi narator lebih pelan |
| Umpan balik positif | Anak belajar lebih berani kalau usahanya dihargai | Pujian lebih dulu, petunjuk sesudahnya |
| Tombol besar dan sedikit | Jari anak belum presisi; layar penuh pilihan membingungkan | Satu tombol mikrofon besar per layar |
| Tidak ada hukuman untuk jawaban salah | Rasa takut membuat anak berhenti mencoba | Tidak ada "salah"; hanya petunjuk, lalu kunci dibacakan |
| Warna cerah, gambar ramah | Menarik perhatian tanpa membuat tepi layar ramai | Warna cerah tema tiap cerita, ilustrasi adegan |

Prinsip-prinsip di atas adalah rangkuman praktik umum desain aplikasi anak.
Setiap baris tetap berstatus **[perlu diverifikasi]** sebelum dipakai sebagai
klaim dalam laporan. [perlu diverifikasi]

Prinsip "tidak ada hukuman" sejalan dengan pandangan bahwa anak belajar bahasa
tanpa takut salah; pembetulan lebih efektif jika diberikan sambil berlatih.
[perlu diverifikasi]

## 4. Daftar sumber

Tautan di bawah ini **belum kami buka dan periksa satu per satu**. Sesuai
aturan tugas, semua baris ditandai `[perlu diverifikasi]` sampai kelompok
memeriksanya sendiri (ketersediaan halaman, penulis, tahun, dan halaman yang dikutip).

| No | Sumber (judul, penulis/lembaga) | Tautan | Untuk klaim | Status |
|---|---|---|---|---|
| 1 | *Fondasi Pengembangan Anak Usia Dini*, Kementerian Pendidikan (Direktorat PAUD) | https://paudpedia.kemdikbud.go.id/ | Rentang usia, cara anak belajar | [perlu diverifikasi] |
| 2 | *Handbook of Early Literacy Research* (Vol. 1), Susan B. Neuman & David K. Dickinson (eds.) | Perpustakaan, ISBN 978-1572306530 | Cerita dan kosakata anak | [perlu diverifikasi] |
| 3 | *Reading Magic: Why Reading Aloud to Our Children Will Change Their Lives Forever*, Mem Fox | Perpustakaan, ISBN 978-0156012096 | Membacakan cerita untuk anak | [perlu diverifikasi] |
| 4 | *Language Development* (bab dalam *Child Development*), Laura E. Berk | https://openlibrary.org/ | Perkembangan bahasa 4–7 tahun | [perlu diverifikasi] |
| 5 | *Designing for Children: Best Practices in Child-Centered Design*, Center on Media and Child Health | https://cmch.tv/ | Tombol besar, kalimat pendek | [perlu diverifikasi] |
| 6 | *Children and Media: Tips for Parents*, American Academy of Pediatrics (HealthyChildren.org) | https://www.healthychildren.org/ | Batas waktu layar, pendampingan orang tua | [perlu diverifikasi] |

### Sumber yang kami yakini memang ada, tetapi belum dikutip langsung

- **Badannya belum dibaca ulang.** Tidak ada sumber di tabel di atas yang kami
  baca utuh. Karena itu semua klaim di bagian 1–3 hanya boleh dipakai setelah
  kelompok mengutip halaman yang tepat. Sumber di tabel di atas adalah
  **judul yang kami kira nyata**, bukan hasil pencarian lengkap.
- Jika suatu judul ternyata tidak ada, hapus barisnya atau ganti dengan sumber
  lain. Jangan menambah tautan tanpa dibuka.

## 5. Yang belum tercakup

- Belum ada rujukan khusus tentang **anak Indonesia** atau **dwibahasa Indonesia–daerah**.
- Belum ada rujukan tentang **pemrosesan suara anak (ASR untuk suara anak)**,
  padahal ini kendala utama sistem. Perlu dicari di minggu 2–3.