"""Modul pendukung Panggung Dongeng Nusantara. Titik masuk aplikasi: dongeng_nusantara.py.

Modul dasar dipakai oleh modul di atasnya:
    konfigurasi                    tanpa ketergantungan
    korpus, tts, asr               memakai konfigurasi
    nlp, ilustrasi, komponen, kuis memakai korpus atau asr
    status                         memakai nlp, asr, dan kuis
    halaman                        memakai status, komponen, ilustrasi, dan tts
"""
