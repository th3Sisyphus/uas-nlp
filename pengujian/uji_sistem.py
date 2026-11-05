# -*- coding: utf-8 -*-
"""
Pengujian aplikasi Panggung Dongeng Nusantara.

    python pengujian/uji_sistem.py              uji NLP dan penanganan error, tanpa internet
    python pengujian/uji_sistem.py --langsung   tambah uji sungguhan: Streamlit, gTTS, Google ASR

Set data berisi jawaban buatan penulis, bukan rekaman anak sungguhan.
"""

from __future__ import annotations

import argparse
import io
import json
import random
import sys
import tempfile
import wave
from pathlib import Path
from unittest import mock

import numpy as np

# Folder proyek dimasukkan ke sys.path agar "modul" bisa diimpor saat berkas ini dijalankan
# dari folder mana pun, misalnya: python pengujian/uji_sistem.py
FOLDER_PROYEK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(FOLDER_PROYEK))

from modul import asr, ilustrasi, konfigurasi, korpus, kuis, nlp, status, tts  # noqa: E402

# (kode cerita, indeks adegan, jawaban benar, jawaban salah)
# Baris ke-0, 2, 4, ... tiap kelompok masuk data pengembangan.
# Baris ke-1, 3, 5, ... masuk data uji yang tidak dipakai saat penyetelan.
DATA = [
    ("kancil", 0,
     ["rambutan", "buah rambutan", "si kancil melihat buah rambutan", "rambutannya", "itu rambutan kak",
      "rambutan yang merah", "rambutan manis banget", "rambutang"],
     ["mangga", "pisang", "apel", "buah jeruk", "aku tidak tahu", "bukan rambutan", "pohon mangga"]),
    ("kancil", 1,
     ["buaya", "ada buaya", "banyak buaya", "buayanya", "di sungai ada buaya yang lapar", "buaya buaya",
      "boaya", "hewan buaya"],
     ["ikan", "kucing", "harimau", "kancil", "katak", "tidak tahu", "gajah"]),
    ("kancil", 2,
     ["jembatan", "seperti jembatan", "kayak jembatan", "buayanya berbaris seperti jembatan", "jembatannya",
      "jambatan", "seperti jembatan panjang", "jembatan kak"],
     ["kereta", "seperti ular", "rumah", "sungai", "tidak tahu", "berbaris", "bukan jembatan"]),
    ("kancil", 3,
     ["punggung buaya", "ke punggung buaya", "kancil melompat ke punggung buaya", "ke atas buaya",
      "di punggung buaya", "ke punggungnya buaya", "ke buaya", "atas punggung buaya"],
     ["ke sungai", "ke hutan", "ke rumah", "ke pohon", "tidak tahu", "kancil melompat", "ke langit"]),
    ("kancil", 4,
     ["maaf", "minta maaf", "kancil bilang maaf", "maafkan aku", "kancil minta maaf kepada buaya",
      "maaf ya buaya", "aku minta maaf", "mohon maaf"],
     ["terima kasih", "halo", "selamat pagi", "ayo makan", "tidak tahu", "rambutan", "hai buaya"]),
    ("timun", 0,
     ["biji timun", "biji", "timun", "raksasa memberi biji timun", "bijinya", "biji mentimun",
      "dikasih biji timun", "biji ketimun"],
     ["uang", "emas", "permen", "bunga", "batu", "tidak tahu", "jarum"]),
    ("timun", 1,
     ["emas", "warna emas", "warnanya emas", "kuning", "kuning emas", "timunnya berwarna emas",
      "warna kuning", "mas"],
     ["hijau", "merah", "biru", "putih", "warna hitam", "tidak tahu", "ungu"]),
    ("timun", 2,
     ["raksasa", "raksasa hijau", "si raksasa", "raksasanya", "buto ijo", "raksasa yang besar",
      "yang datang raksasa", "raksasa datang"],
     ["ibu", "mbok srini", "kancil", "ayah", "harimau", "tidak tahu", "teman"]),
    ("timun", 3,
     ["hutan bambu", "bambu", "jadi hutan bambu", "berubah menjadi hutan bambu", "pohon bambu", "jadi bambu",
      "bambu bambu", "hutan bambu yang tinggi"],
     ["laut", "lumpur", "batu", "jarum", "hutan", "tidak tahu", "garam"]),
    ("timun", 4,
     ["ibu", "ibunya", "kepada ibunya", "pulang ke ibu", "mbok srini", "ke mbok srini", "mama", "ibu nya"],
     ["ayah", "raksasa", "teman", "rumah", "kakek", "tidak tahu", "kancil"]),
    ("malin", 0,
     ["ibu", "ibunya", "bersama ibu", "sama ibunya", "dengan ibu", "mama", "emak", "malin tinggal bersama ibunya"],
     ["ayah", "kakek", "sendiri", "teman", "adik", "tidak tahu", "raja"]),
    ("malin", 1,
     ["kapal", "naik kapal", "kapal besar", "kapalnya", "perahu", "naik kapal laut", "malin pergi naik kapal",
      "kapal yang besar"],
     ["pesawat", "mobil", "kereta", "sepeda", "motor", "tidak tahu", "jalan kaki"]),
    ("malin", 2,
     ["senang", "gembira", "bahagia", "sangat senang", "ibu senang", "ibu senang sekali", "seneng", "gembira sekali"],
     ["sedih", "marah", "takut", "menangis", "kaget", "tidak tahu", "tidak senang"]),
    ("malin", 3,
     ["sombong", "anak sombong", "jadi sombong", "sombong sekali", "anak yang sombong", "durhaka", "jahat", "tidak baik"],
     ["baik", "rajin", "pintar", "kaya", "tidak sombong", "tidak tahu", "sedih"]),
    ("malin", 4,
     ["batu", "menjadi batu", "jadi batu", "berubah menjadi batu", "batu besar", "malin jadi batu", "batuu", "batunya"],
     ["kayu", "pasir", "ikan", "kapal", "tidak tahu", "bukan batu", "patung"]),
]


def pecah_data() -> tuple[list[tuple], list[tuple]]:
    pengembangan, uji = [], []
    for kode, indeks, benar, salah in DATA:
        for label, kelompok in ((True, benar), (False, salah)):
            for urutan, jawaban in enumerate(kelompok):
                (pengembangan if urutan % 2 == 0 else uji).append((kode, indeks, jawaban, label))
    return pengembangan, uji


POLA_KALIMAT = ["{k}", "jawabannya {k}", "emm {k} kak", "{k} ya", "menurut aku {k}", "yang itu {k}"]
JAWABAN_UMUM_SALAH = ["aku tidak tahu", "eee apa ya", "lupa"]


def rusak_satu_huruf(teks: str, acak: random.Random) -> str:
    """Meniru salah dengar ASR: satu huruf pada tiap kata sepanjang 4+ huruf diganti atau dibuang."""
    kata_baru = []
    for kata in teks.split():
        if len(kata) >= 4:
            i = acak.randrange(1, len(kata) - 1)
            ganti = acak.choice("aiueobdgkmnprst")
            kata = kata[:i] + (ganti if acak.random() < 0.7 else "") + kata[i + 1:]
        kata_baru.append(kata)
    return " ".join(kata_baru)


def buat_set_b(benih: int = 2026) -> dict[str, list[tuple]]:
    """Set uji B dibuat otomatis dari kunci jawaban, bukan ditulis tangan per soal.

    Positif: tiap kunci dimasukkan ke pola kalimat.
    Negatif: kunci utama dari pertanyaan lain, jawaban negasi, dan jawaban "tidak tahu".
    Set berderau merusak satu huruf per kata, meniru salah dengar ASR.
    """
    acak = random.Random(benih)
    soal = [(k, i) for k, c in korpus.CERITA.items() for i in range(len(c["adegan"]))]
    bersih, berderau = [], []
    for kode, indeks in soal:
        a = adegan(kode, indeks)
        kata_kunci = {t for k in a["kunci"] for t in nlp.praproses(k)}
        pengecoh = []
        for kode2, indeks2 in soal:
            lain = adegan(kode2, indeks2)["utama"]
            if not (set(nlp.praproses(lain)) & kata_kunci) and lain not in pengecoh:
                pengecoh.append(lain)
        for kunci in a["kunci"]:
            if nlp.praproses(kunci) and "tidak" not in kunci:
                for pola in POLA_KALIMAT:
                    bersih.append((kode, indeks, pola.format(k=kunci), True))
                    berderau.append((kode, indeks, pola.format(k=rusak_satu_huruf(kunci, acak)), True))
        for lain in acak.sample(pengecoh, 6):
            pola = acak.choice(POLA_KALIMAT)
            bersih.append((kode, indeks, pola.format(k=lain), False))
            berderau.append((kode, indeks, pola.format(k=rusak_satu_huruf(lain, acak)), False))
        bersih.append((kode, indeks, f"bukan {a['utama']}", False))
        for umum in JAWABAN_UMUM_SALAH:
            bersih.append((kode, indeks, umum, False))
    return {"bersih": bersih, "berderau": berderau}


def metrik(pasangan: list[tuple[bool, bool]]) -> dict:
    tp = sum(1 for prediksi, label in pasangan if prediksi and label)
    fp = sum(1 for prediksi, label in pasangan if prediksi and not label)
    fn = sum(1 for prediksi, label in pasangan if not prediksi and label)
    tn = sum(1 for prediksi, label in pasangan if not prediksi and not label)
    presisi = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * presisi * recall / (presisi + recall) if presisi + recall else 0.0
    akurasi = (tp + tn) / max(1, len(pasangan))
    return {"tp": tp, "fp": fp, "fn": fn, "tn": tn, "presisi": presisi, "recall": recall, "f1": f1, "akurasi": akurasi}


def adegan(kode: str, indeks: int) -> dict:
    return korpus.CERITA[kode]["adegan"][indeks]


def dasar_exact(baris: tuple) -> bool:
    kode, indeks, jawaban, _ = baris
    return nlp.normalisasi(jawaban) in {nlp.normalisasi(k) for k in adegan(kode, indeks)["kunci"]}


def dasar_jaccard(baris: tuple, ambang: float = 0.5) -> bool:
    kode, indeks, jawaban, _ = baris
    a = set(nlp.normalisasi(jawaban).split())
    return any(
        len(a & set(nlp.normalisasi(k).split())) / max(1, len(a | set(nlp.normalisasi(k).split()))) >= ambang
        for k in adegan(kode, indeks)["kunci"]
    )


def skor_sistem(baris: tuple, ambang: float, bobot: float) -> dict:
    kode, indeks, jawaban, _ = baris
    a = adegan(kode, indeks)
    return nlp.nilai_jawaban(jawaban, a["tanya"], a["kunci"], kode, ambang, bobot)


def setel(pengembangan: list[tuple]) -> list[dict]:
    """Pencarian grid ambang dan bobot. Hanya melihat data pengembangan."""
    hasil = []
    for bobot in (0.0, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0):
        skor = [(skor_sistem(b, 0, bobot)["skor"], b[3]) for b in pengembangan]
        for ambang in np.arange(0.30, 0.91, 0.05):
            m = metrik([(s >= ambang, label) for s, label in skor])
            hasil.append({"bobot": bobot, "ambang": round(float(ambang), 2), **m})
    return sorted(hasil, key=lambda h: (-round(h["f1"], 3), -h["presisi"], -h["ambang"], -h["bobot"]))


def wav_dari(sinyal: np.ndarray, laju: int = 16000) -> bytes:
    wadah = io.BytesIO()
    with wave.open(wadah, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(laju)
        wav.writeframes((np.clip(sinyal, -1, 1) * 32767).astype(np.int16).tobytes())
    return wadah.getvalue()


def sinyal_ucapan(detik: float = 1.5, amplitudo: float = 0.3, laju: int = 16000) -> np.ndarray:
    """Nada dengan selubung naik-turun, menyerupai energi ucapan yang selesai dengan wajar."""
    t = np.linspace(0, detik, int(detik * laju), endpoint=False)
    return amplitudo * np.sin(2 * np.pi * 220 * t) * np.sin(np.pi * t / detik) ** 2


# ---- Uji unit -------------------------------------------------------------------
# Tiap fungsi berawalan "uji_" adalah satu uji. jalankan_uji() mencari dan menjalankannya.


def nilai(kode: str, indeks: int, jawaban: str) -> dict:
    a = adegan(kode, indeks)
    return nlp.nilai_jawaban(jawaban, a["tanya"], a["kunci"], kode)


# Praproses dan penilaian NLP


def uji_stemmer_imbuhan():
    contoh = {
        "melompat": "lompat", "sungainya": "sungai", "menyeberang": "seberang", "menangis": "tangis",
        "memeluk": "peluk", "mengejar": "kejar", "berbaris": "baris", "ibunya": "ibu",
        "rambutannya": "rambutan", "makan": "makan", "dibohongi": "bohong",
    }
    for kata, dasar in contoh.items():
        assert nlp.stem_ringan(kata) == dasar, kata


def uji_negasi_ditandai():
    assert nlp.praproses("bukan batu") == ["tidak_batu"]


def uji_negasi_gagal_walau_kata_kunci_muncul():
    assert not nilai("malin", 4, "bukan batu")["lulus"]


def uji_negasi_frasa_dua_kata():
    assert not nilai("kancil", 3, "bukan punggung buaya")["lulus"]


def uji_negasi_berhenti_di_kata_tapi():
    assert nilai("malin", 4, "bukan kayu tapi batu")["lulus"]


def uji_mengulang_pertanyaan_tidak_lulus():
    assert not nilai("kancil", 3, "kancil melompat")["lulus"]


def uji_contoh_soal_tugas():
    hasil = nlp.nilai_jawaban("Kancil melompat ke sungai", "Ke mana Kancil melompat?", ["sungai"], "kancil")
    assert hasil["lulus"]
    assert hasil["token"] == ["sungai"]


def uji_jawaban_kosong():
    assert nilai("kancil", 1, "")["skor"] == 0.0
    assert not nilai("kancil", 1, "eee anu")["lulus"]


def uji_n_best_memilih_hipotesis_terbaik():
    a = adegan("kancil", 1)
    hasil = nlp.nilai_alternatif(["boneka", "buaya"], a["tanya"], a["kunci"], "kancil")
    assert hasil["lulus"]
    assert hasil["jawaban"] == "buaya"


# Korpus (korpus/cerita/*.json), terutama setelah menambah cerita baru


def uji_korpus_gambar_dan_kunci_bisa_dipakai():
    for kode, cerita in korpus.CERITA.items():
        for nomor, a in enumerate(cerita["adegan"], 1):
            tempat = f"{kode} adegan {nomor}"
            assert a["gambar"]["latar"] in ilustrasi.LATAR, tempat
            for objek in a["gambar"]["objek"]:
                assert "emoji" in objek or objek.get("gambar") in ilustrasi.PENGGAMBAR, tempat
            assert "data:image/svg+xml;base64," in ilustrasi.gambar_adegan(kode, nomor - 1)
            # Kunci yang habis terbuang praproses tidak akan pernah bisa dicocokkan.
            for kunci in a["kunci"]:
                assert nlp.praproses(kunci, nlp.token_pertanyaan(a["tanya"])), f"{tempat}: {kunci}"


def uji_korpus_tidak_lengkap_dilaporkan():
    with tempfile.TemporaryDirectory() as folder:
        data = {"judul": "Uji", "asal": "-", "ajaran": "-", "warna": {}, "adegan": [{"narasi": "Halo."}]}
        Path(folder, "01_uji.json").write_text(json.dumps(data), encoding="utf-8")
        try:
            korpus.muat_cerita(Path(folder))
        except ValueError as galat:
            assert "adegan 1: tanya" in str(galat)
        else:
            raise AssertionError("korpus tidak lengkap seharusnya ditolak")


# Pemeriksaan audio


def kategori_audio(data: bytes) -> str | None:
    return asr.periksa_audio(data)["gangguan"]


def uji_audio_berkas_bukan_wav():
    assert kategori_audio(b"ini bukan audio") == "rusak"


def uji_audio_berkas_kosong():
    assert kategori_audio(b"") == "rusak"


def uji_audio_wav_tanpa_bingkai():
    assert kategori_audio(wav_dari(np.zeros(0))) == "terpotong"


def uji_audio_rekaman_terlalu_pendek():
    assert kategori_audio(wav_dari(sinyal_ucapan(0.2))) == "terpotong"


def uji_audio_hening():
    assert kategori_audio(wav_dari(np.zeros(16000))) == "kosong"


def uji_audio_derau_sangat_kecil():
    assert kategori_audio(wav_dari(np.random.default_rng(1).normal(0, 0.001, 16000))) == "kosong"


def uji_audio_header_wav_terpotong_di_tengah():
    assert kategori_audio(wav_dari(sinyal_ucapan())[:30]) == "rusak"


def uji_audio_rekaman_32_bit_tetap_dibaca():
    wadah = io.BytesIO()
    with wave.open(wadah, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(4)
        wav.setframerate(16000)
        wav.writeframes((sinyal_ucapan() * 2**31 * 0.9).astype(np.int32).tobytes())
    assert asr.periksa_audio(wadah.getvalue())["rms"] > konfigurasi.RMS_MINIMUM


def uji_audio_ucapan_normal_lolos():
    info = asr.periksa_audio(wav_dari(sinyal_ucapan()))
    assert info["gangguan"] is None
    assert not info["ujung_terpotong"]
    assert info["rms"] > konfigurasi.RMS_MINIMUM


def uji_audio_ucapan_terhenti_mendadak_ditandai():
    t = np.linspace(0, 1.5, 24000, endpoint=False)
    assert asr.periksa_audio(wav_dari(0.3 * np.sin(2 * np.pi * 220 * t)))["ujung_terpotong"]


# Transkripsi. Kelas error yang dilempar tiruan di sini sama dengan pustaka aslinya.


def transkripsi_dengan(**kwargs) -> dict:
    with mock.patch.object(asr.sr.Recognizer, "recognize_google", **kwargs):
        return asr.transkripsi(wav_dari(sinyal_ucapan()))


def uji_asr_tidak_dimengerti():
    assert transkripsi_dengan(side_effect=asr.sr.UnknownValueError())["gangguan"] == "tidak_jelas"


def uji_asr_internet_putus():
    assert transkripsi_dengan(side_effect=asr.sr.RequestError("tidak ada koneksi"))["gangguan"] == "internet"


def uji_asr_timeout():
    assert transkripsi_dengan(side_effect=TimeoutError())["gangguan"] == "internet"


def uji_asr_flac_tidak_tersedia():
    assert transkripsi_dengan(side_effect=OSError("FLAC conversion utility not available"))["gangguan"] == "pustaka"


def uji_asr_hasil_daftar_kosong():
    assert transkripsi_dengan(return_value=[])["gangguan"] == "tidak_jelas"


def uji_asr_hasil_alternatif_kosong():
    assert transkripsi_dengan(return_value={"alternative": []})["gangguan"] == "tidak_jelas"


def uji_asr_format_n_best():
    balasan = {"alternative": [{"transcript": "buaya", "confidence": 0.9}, {"transcript": "boaya"}]}
    hasil = transkripsi_dengan(return_value=balasan)
    assert hasil["gangguan"] is None
    assert hasil["alternatif"] == ["buaya", "boaya"]
    assert abs(hasil["keyakinan"] - 0.9) < 1e-9


def uji_asr_error_tak_terduga_tetap_ramah():
    with mock.patch.object(status, "transkripsi", side_effect=RuntimeError("galat aneh")), \
            mock.patch.object(status, "tetapkan_gangguan") as tetapkan:
        status.tangani_rekaman(b"")
    tetapkan.assert_called_once_with("rusak")


# Logika kuis

ADEGAN_BUAYA = adegan("kancil", 1)
BENAR = {**nlp.hasil_nlp(), "skor": 0.9, "lulus": True}


def putuskan(hasil: dict, percobaan: int = 0, **kwargs) -> dict:
    return kuis.putuskan(hasil, ADEGAN_BUAYA, percobaan, **kwargs)


def uji_kuis_benar_lanjut():
    k = putuskan(BENAR)
    assert (k["jenis"], k["lanjut"], k["hitung_percobaan"]) == ("benar", True, False)


def uji_kuis_salah_pertama_memberi_petunjuk():
    k = putuskan(nlp.hasil_nlp())
    assert k["jenis"] == "salah"
    assert ADEGAN_BUAYA["petunjuk"] in k["pesan"]


def uji_kuis_salah_kedua_memberi_huruf_awal():
    assert "huruf B" in putuskan(nlp.hasil_nlp(), 1)["pesan"]


def uji_kuis_salah_ketiga_memberi_kunci():
    k = putuskan(nlp.hasil_nlp(), 2)
    assert (k["jenis"], k["lanjut"]) == ("kunci", True)
    assert "buaya" in k["pesan"]


def uji_kuis_ujung_terpotong_tidak_mengurangi_kesempatan():
    k = putuskan(nlp.hasil_nlp(), ujung_terpotong=True)
    assert (k["jenis"], k["hitung_percobaan"]) == ("ulang", False)


def uji_kuis_keyakinan_rendah_tidak_mengurangi_kesempatan():
    k = putuskan(nlp.hasil_nlp(), keyakinan=0.2)
    assert (k["jenis"], k["hitung_percobaan"]) == ("ulang", False)


def uji_kuis_jawaban_benar_menang_atas_tanda_terpotong():
    assert putuskan(BENAR, keyakinan=0.2, ujung_terpotong=True)["jenis"] == "benar"


def jalankan_uji() -> bool:
    """Menjalankan semua fungsi uji_* di berkas ini dan mencetak ringkasannya."""
    daftar = [(nama, f) for nama, f in globals().items() if nama.startswith("uji_") and callable(f)]
    gagal = []
    for nama, fungsi in daftar:
        try:
            fungsi()
        except Exception as galat:  # AssertionError atau error lain: uji dianggap gagal
            gagal.append(nama)
            print(f"  GAGAL {nama}: {type(galat).__name__} {galat}")
    print(f"  {len(daftar) - len(gagal)} dari {len(daftar)} uji lulus")
    return not gagal


def jalankan_evaluasi(keluaran: str | None, hanya_pengembangan: bool = False) -> None:
    pengembangan, uji = pecah_data()
    grid = setel(pengembangan)
    print(f"Data: {len(pengembangan)} pengembangan, {len(uji)} uji")
    print("Lima pengaturan teratas pada data pengembangan:")
    for g in grid[:5]:
        print(f"  bobot={g['bobot']:.1f} ambang={g['ambang']:.2f} F1={g['f1']:.3f} P={g['presisi']:.3f} R={g['recall']:.3f}")

    ambang, bobot = konfigurasi.AMBANG_LULUS, konfigurasi.BOBOT_KATA
    laporan = {"ambang": ambang, "bobot": bobot, "jumlah": {"pengembangan": len(pengembangan), "uji": len(uji)}, "grid": grid[:5]}
    print(f"\nPengaturan aplikasi: ambang={ambang}, bobot={bobot}")
    for nama, data in (("pengembangan", pengembangan),) + ((("uji", uji),) if not hanya_pengembangan else ()):
        rincian = [(b, skor_sistem(b, ambang, bobot)) for b in data]
        laporan[nama] = {
            "exact": metrik([(dasar_exact(b), b[3]) for b in data]),
            "jaccard": metrik([(dasar_jaccard(b), b[3]) for b in data]),
            "sistem": metrik([(h["lulus"], b[3]) for b, h in rincian]),
            "keliru": [
                {"cerita": b[0], "adegan": b[1] + 1, "tanya": adegan(b[0], b[1])["tanya"], "jawaban": b[2],
                 "harapan": b[3], "sistem": h["lulus"], "skor": round(h["skor"], 3), "token": h["token"]}
                for b, h in rincian if h["lulus"] != b[3]
            ],
        }
        print(f"[{nama}]")
        for metode in ("exact", "jaccard", "sistem"):
            m = laporan[nama][metode]
            print(f"  {metode:8s} F1={m['f1']:.3f} presisi={m['presisi']:.3f} recall={m['recall']:.3f} akurasi={m['akurasi']:.3f}"
                  f" (TP={m['tp']} FP={m['fp']} FN={m['fn']} TN={m['tn']})")
        for k in laporan[nama]["keliru"]:
            print(f"    keliru: {k['jawaban']!r} pada {k['tanya']!r} harapan={k['harapan']} skor={k['skor']} token={k['token']}")
    if not hanya_pengembangan:
        for nama, data in buat_set_b().items():
            rincian = [(b, skor_sistem(b, ambang, bobot)) for b in data]
            hasil_b = {
                "jumlah": len(data),
                "exact": metrik([(dasar_exact(b), b[3]) for b in data]),
                "jaccard": metrik([(dasar_jaccard(b), b[3]) for b in data]),
                "sistem": metrik([(h["lulus"], b[3]) for b, h in rincian]),
                "keliru": [
                    {"tanya": adegan(b[0], b[1])["tanya"], "jawaban": b[2], "harapan": b[3],
                     "skor": round(h["skor"], 3), "token": h["token"]}
                    for b, h in rincian if h["lulus"] != b[3]
                ],
            }
            laporan[f"b_{nama}"] = hasil_b
            print(f"[set B {nama}, {len(data)} butir]")
            for metode in ("exact", "jaccard", "sistem"):
                m = hasil_b[metode]
                print(f"  {metode:8s} F1={m['f1']:.3f} presisi={m['presisi']:.3f} recall={m['recall']:.3f} akurasi={m['akurasi']:.3f}"
                      f" (TP={m['tp']} FP={m['fp']} FN={m['fn']} TN={m['tn']})")
    if keluaran:
        with open(keluaran, "w", encoding="utf-8") as berkas:
            json.dump(laporan, berkas, ensure_ascii=False, indent=1)


def cek_langsung() -> None:
    """Uji komponen sungguhan. Butuh Streamlit asli dan internet."""
    from streamlit.testing.v1 import AppTest

    print("1. Menjalankan aplikasi lewat AppTest Streamlit...")
    at = AppTest.from_file(str(FOLDER_PROYEK / "dongeng_nusantara.py"), default_timeout=30).run()
    assert not at.exception, at.exception
    at.button(key="pilih_kancil").click().run()
    assert not at.exception, at.exception
    at.button(key="tombol_siap").click().run()
    assert not at.exception, at.exception
    print("   Beranda, adegan, dan pertanyaan terbuka tanpa error.")

    print("2. gTTS: membuat suara...")
    mp3 = tts._suara_gtts("Ke mana Kancil melompat?", False)
    print(f"   Berhasil, {len(mp3)} byte MP3.")

    print("3. Google ASR: mengirim rekaman hasil gTTS...")
    try:
        import subprocess

        wav = subprocess.run(
            ["ffmpeg", "-loglevel", "error", "-i", "pipe:0", "-ar", "16000", "-ac", "1", "-f", "wav", "pipe:1"],
            input=mp3, capture_output=True, check=True,
        ).stdout
    except (OSError, subprocess.CalledProcessError):
        print("   Dilewati: ffmpeg tidak ditemukan untuk mengubah MP3 ke WAV.")
        return
    hasil = asr.transkripsi(wav)
    print(f"   Teks terbaca: {hasil.get('alternatif')}, keyakinan {hasil.get('keyakinan')}, gangguan {hasil['gangguan']}")


def main() -> int:
    pengurai = argparse.ArgumentParser()
    pengurai.add_argument("--langsung", action="store_true", help="uji Streamlit, gTTS, dan Google ASR sungguhan")
    pengurai.add_argument("--json", help="simpan hasil evaluasi ke berkas JSON")
    pengurai.add_argument("--setel", action="store_true", help="hanya lihat data pengembangan saat menyetel")
    argumen = pengurai.parse_args()

    jalankan_evaluasi(argumen.json, argumen.setel)
    print("\nUji unit:")
    lulus = jalankan_uji()
    if argumen.langsung:
        cek_langsung()
    return 0 if lulus else 1


if __name__ == "__main__":
    sys.exit(main())
