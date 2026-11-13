
1. Korpus ganda. tts_demo.py membaca korpus/cerita.json (9 pertanyaan). Aplikasi membaca korpus/cerita/*.json (format berbeda, 15 adegan). Dua sumber ini bisa tidak sinkron. Pilih satu sumber kebenaran, atau jelaskan di ReadMe mana yang dipakai untuk apa.
2. requirements.txt tidak lengkap. PyAudio tidak ada, padahal asr_demo.py memerlukannya. Daftar pip di ReadMe.txt juga tidak memuat streamlit, scikit-learn, dan numpy.
3. asr_demo.py punya tiga masalah:
    - Opsi --durasi tidak berpengaruh. Fungsi menerima durasi tapi tidak memakainya, dan transkripsi() selalu memakai konstanta DURASI_MAKS.
    - pengenal.energy_threshold = ambang dijalankan setelah adjust_for_ambient_noise, jadi hasil pengukuran kebisingan ruangan langsung ditimpa. Pengukuran 1 detik itu sia-sia.
    - --berkas memakai listen(). Untuk berkas WAV, record() lebih tepat.
4. buatkan file baru pada folder /laporan-ai berupa laporan progres. Isikan catatan progres sungguhan: apa selesai, apa belum, masalah yang ditemui. Atau hapus.
5. docs/keputusan-teknis.md bagian 5 masih [KEPUTUSAN KELOMPOK]. Isi keputusan akhir. docs/riset.md: buka semua tautan, ganti beranda generik (cmch.tv, openlibrary.org) dengan halaman spesifik, lalu hapus tanda [perlu diverifikasi] hanya pada yang sudah dicek. (*JANGAN DI EKSEKUSI DAHULU*)