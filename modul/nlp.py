# -*- coding: utf-8 -*-
"""Modul NLP: menilai jawaban anak dengan TF-IDF dan cosine similarity, bukan exact match.
"""

from __future__ import annotations

import re
from difflib import get_close_matches
from functools import lru_cache

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from modul.konfigurasi import AMBANG_LULUS, BATAS_EJAAN, BOBOT_KATA, RASIO_HAMPIR
from modul.korpus import CERITA, LEKSIKON


# =============================================================================
# MODUL NLP: PENCOCOKAN JAWABAN TANPA EXACT MATCH
#
# Masalah yang diselesaikan:
#   Kunci jawaban: "sungai".
#   Anak bisa berkata: "kancil melompat ke sungainya", "sunge", "ke sungai kak".
#   Exact match menolak semua contoh ini, padahal anak paham ceritanya.
#
# Tahapan (tiap langkah dibahas di fungsinya masing-masing):
#   1. Normalisasi     huruf kecil, buang tanda baca, seragamkan kata lisan
#   2. Tokenisasi      memecah kalimat menjadi kata
#   3. Tanda negasi    "bukan sungai" menjadi satu token khusus
#   4. Stopword        membuang kata yang tidak membawa isi
#   5. Stemming        "melompat" menjadi "lompat", "sungainya" menjadi "sungai"
#   6. Question demoting  membuang kata yang sudah ada di pertanyaan
#   7. Koreksi ejaan   "boaya" didekatkan ke kata kunci "buaya"
#   8. Pembobotan TF-IDF  kata langka di korpus mendapat bobot lebih besar
#   9. Cosine similarity  mengukur kedekatan vektor jawaban dan vektor kunci
#  10. Keputusan       skor dibandingkan dengan ambang kelulusan
# =============================================================================

# Sumber bahasa dibaca dari korpus/leksikon.json (penjelasan tiap daftar ada di sana).
# Stopword dibuat sendiri karena daftar umum sering ikut membuang kata negasi.
KAMUS_NORMALISASI: dict[str, str] = LEKSIKON["normalisasi"]   # gak -> tidak, bunda -> ibu
KATA_PERTENTANGAN = set(LEKSIKON["pertentangan"])             # tapi, namun: negasi berhenti
STOPWORD = set(LEKSIKON["stopword"])
KATA_PENGISI = set(LEKSIKON["pengisi"])                       # eh, hmm, menurut, mungkin
# Kata dasar untuk stemmer ringan. Stemmer hanya menerima hasil yang ada di daftar ini,
# jadi kata seperti "makan" tidak akan rusak menjadi "mak".
KATA_DASAR = set(LEKSIKON["kata_dasar"])

AKHIRAN_PARTIKEL = ("nya", "lah", "kah", "ku", "mu")
AKHIRAN_TURUNAN = ("kan", "an", "i")
# (awalan, huruf pengganti): "menyeberang" -> "s" + "eberang", "memeluk" -> "p" + "eluk".
ATURAN_AWALAN = [
    ("meny", "s"), ("peny", "s"), ("meng", "k"), ("meng", ""), ("peng", "k"), ("peng", ""),
    ("mem", "p"), ("mem", ""), ("pem", "p"), ("pem", ""),
    ("men", "t"), ("men", ""), ("pen", "t"), ("pen", ""),
    ("me", ""), ("pe", ""), ("ber", ""), ("be", ""), ("ter", ""), ("per", ""),
    ("di", ""), ("ke", ""), ("se", ""),
]


def normalisasi(teks: str) -> str:
    """Mengubah ke huruf kecil, membuang tanda baca, dan memisah kata ulang."""
    teks = teks.lower().replace("-", " ")
    teks = re.sub(r"[^a-z0-9\s]", " ", teks)
    return re.sub(r"\s+", " ", teks).strip()


def stem_ringan(kata: str) -> str:
    """Stemmer Indonesia ringan berbasis kamus.

    Memangkas akhiran lalu awalan, dan hanya menerima hasil yang ada di KATA_DASAR.
    Pendekatannya konservatif: lebih baik tidak memotong daripada merusak kata.
    Kata di luar kamus tetap diproses untuk partikel -nya, -lah, -ku, -mu.
    """
    if kata in KATA_DASAR or len(kata) < 4:
        return kata

    # Langkah 1: siapkan calon bentuk tanpa akhiran.
    calon = [kata]
    for akhiran in AKHIRAN_PARTIKEL:
        if kata.endswith(akhiran) and len(kata) - len(akhiran) >= 3:
            calon.append(kata[: -len(akhiran)])
    tanpa_partikel = calon[-1]
    for bentuk in list(calon):
        for akhiran in AKHIRAN_TURUNAN:
            if bentuk.endswith(akhiran) and len(bentuk) - len(akhiran) >= 3:
                calon.append(bentuk[: -len(akhiran)])

    # Langkah 2: tiap calon dicoba tanpa awalan, termasuk perubahan bunyi (nasal).
    for bentuk in calon:
        if bentuk in KATA_DASAR:
            return bentuk
        for awalan, ganti in ATURAN_AWALAN:
            if bentuk.startswith(awalan) and ganti + bentuk[len(awalan):] in KATA_DASAR:
                return ganti + bentuk[len(awalan):]

    # Langkah 3: kata tak dikenal hanya dilepas partikelnya ("kerbaunya" -> "kerbau").
    return tanpa_partikel


def praproses(teks: str, kata_pertanyaan: frozenset[str] = frozenset()) -> list[str]:
    """Pipeline praproses NLP. Hasilnya daftar token bersih.

    Contoh dengan pertanyaan "Ke mana Kancil melompat?":
        "Kancil melompat ke sungainya, bukan ke hutan"
        -> token normal  : kancil melompat ke sungainya bukan ke hutan
        -> negasi        : "bukan hutan" ditandai menjadi "tidak_hutan"
        -> stopword      : kancil melompat sungainya tidak_hutan
        -> stemming      : kancil lompat sungai tidak_hutan
        -> demoting      : sungai tidak_hutan
    """
    token_seragam = [KAMUS_NORMALISASI.get(t, t) for t in normalisasi(teks).split()]

    # Penanda negasi (negation tagging): token setelah "tidak" menjadi tidak_X sampai ada
    # kata pertentangan. Tanpa ini, "bukan sungai" akan cocok dengan kunci "sungai".
    hasil: list[str] = []
    negasi_aktif = False
    for token in token_seragam:
        if token == "tidak":
            negasi_aktif = True
        elif token in KATA_PERTENTANGAN:  # "bukan hutan tapi sungai": negasi berhenti di sini
            negasi_aktif = False
        elif token not in STOPWORD and token not in KATA_PENGISI:
            dasar = stem_ringan(token)
            hasil.append(f"tidak_{dasar}" if negasi_aktif else dasar)

    # Question demoting (Mohler dkk., 2011): kata yang sudah muncul di pertanyaan tidak
    # bisa membuktikan pemahaman anak, karena anak hanya mengulang pertanyaan.
    if kata_pertanyaan:
        tanpa_kata_soal = [t for t in hasil if t not in kata_pertanyaan]
        if tanpa_kata_soal:      # jika semua terbuang, pertahankan token aslinya
            hasil = tanpa_kata_soal
    return hasil


def koreksi_ejaan(token_jawaban: list[str], kosakata_kunci: set[str]) -> list[str]:
    """Mendekatkan kata hasil ASR yang mirip kata kunci ("boaya" -> "buaya").

    TF-IDF per kata menganggap "boaya" dan "buaya" dua dimensi yang sama sekali berbeda.
    N-gram huruf juga lemah di sini: satu huruf berbeda pada kata pendek merusak banyak
    n-gram. Karena itu kata yang tidak dikenal dibandingkan dulu dengan kosakata kunci.
    Kata yang ada di KATA_DASAR dibiarkan, agar "baju" tidak dipaksa menjadi "batu".
    """
    hasil = []
    for token in token_jawaban:
        awalan = "tidak_" if token.startswith("tidak_") else ""
        kata = token[len(awalan):]
        if len(kata) >= 3 and kata not in KATA_DASAR and kata not in kosakata_kunci:
            cocok = get_close_matches(kata, kosakata_kunci, n=1, cutoff=BATAS_EJAAN)
            kata = cocok[0] if cocok else kata
        hasil.append(awalan + kata)
    return hasil


def token_pertanyaan(pertanyaan: str) -> frozenset[str]:
    """Token kata isi dari kalimat pertanyaan, dipakai untuk question demoting."""
    return frozenset(praproses(pertanyaan))


@lru_cache(maxsize=16)
def korpus_cerita(kode_cerita: str) -> tuple[str, ...]:
    """Dokumen acuan untuk menghitung IDF: satu dokumen per kalimat cerita.

    IDF butuh banyak dokumen agar bisa membedakan kata umum di cerita
    (misalnya "kancil") dari kata yang lebih khas (misalnya "jembatan").
    """
    dokumen = []
    for adegan in CERITA[kode_cerita]["adegan"]:
        for kalimat in re.split(r"[.!?]", adegan["narasi"]):
            token = praproses(kalimat)
            if token:
                dokumen.append(" ".join(token))
    return tuple(dokumen)


def hasil_nlp(jawaban: str = "", token: list[str] | None = None) -> dict:
    """Wadah hasil penilaian satu jawaban, dipakai untuk umpan balik dan panel guru.

    skor, cos_kata, cos_huruf : nilai 0 sampai 1
    lulus, hampir             : keputusan setelah skor dibandingkan dengan ambang
    kunci_terdekat            : kunci jawaban dengan skor tertinggi
    token                     : token bersih jawaban setelah praproses
    jawaban                   : teks jawaban asli (hipotesis ASR yang dipilih)
    """
    return {"skor": 0.0, "cos_kata": 0.0, "cos_huruf": 0.0, "lulus": False, "hampir": False,
            "kunci_terdekat": "", "token": token or [], "jawaban": jawaban}


def nilai_jawaban(
    jawaban: str,
    pertanyaan: str,
    daftar_kunci: list[str],
    kode_cerita: str,
    ambang: float = AMBANG_LULUS,
    bobot_kata: float = BOBOT_KATA,
) -> dict:
    """INTI NLP: menilai jawaban dengan pembobotan TF-IDF dan cosine similarity.

    Rumus yang dipakai scikit-learn (smooth_idf=True, sublinear_tf=True):
        tf(t, d)    = 1 + log(frekuensi t di d)
        idf(t)      = log((1 + n) / (1 + df(t))) + 1
        tfidf(t, d) = tf(t, d) * idf(t), lalu vektor dinormalisasi L2
        cosine(a, b) = (a . b) / (|a| |b|)

    Skor akhir menggabungkan dua sudut pandang:
        skor = bobot_kata * cos_kata + (1 - bobot_kata) * cos_huruf

    cos_kata  : TF-IDF per kata, menangkap kecocokan makna antarkata utuh.
    cos_huruf : TF-IDF n-gram huruf (2 sampai 4), menangkap kemiripan bentuk kata
                yang lolos dari koreksi ejaan, misalnya kata gabungan atau potongan kata.
    """
    kata_soal = token_pertanyaan(pertanyaan)
    token_jawab = praproses(jawaban, kata_soal)
    if not token_jawab:
        return hasil_nlp(jawaban)  # hanya berisi kata pengisi atau mengulang pertanyaan

    # Kunci jawaban diproses dengan pipeline yang sama dengan jawaban anak.
    kunci_bersih = {k: praproses(k, kata_soal) for k in daftar_kunci}
    kosakata_kunci = {t for token in kunci_bersih.values() for t in token}
    token_jawab = koreksi_ejaan(token_jawab, kosakata_kunci)
    hasil = hasil_nlp(jawaban, token_jawab)
    teks_jawaban = " ".join(token_jawab)

    # Korpus untuk fit = kalimat cerita + kunci jawaban + jawaban anak.
    # Jawaban anak ikut di-fit supaya kata di luar kosakata cerita tetap menjadi
    # dimensi vektor dan menurunkan kemiripan, bukan diam-diam diabaikan.
    korpus = [*korpus_cerita(kode_cerita), *(" ".join(t) for t in kunci_bersih.values()), teks_jawaban]
    vektor_kata = TfidfVectorizer(analyzer="word", token_pattern=r"\S+", lowercase=False, sublinear_tf=True)
    vektor_huruf = TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 4), lowercase=False, sublinear_tf=True)
    vektor_kata.fit(korpus)
    vektor_huruf.fit(korpus)

    for kunci_asli, token_kunci in kunci_bersih.items():
        # Aturan negasi: "bukan batu" tidak boleh lulus untuk kunci "batu".
        if any(f"tidak_{t}" in token_jawab for t in token_kunci):
            continue

        # Jendela kata: selain seluruh kalimat, tiap potongan sepanjang kunci ikut dinilai.
        # Tanpa ini, jawaban panjang yang benar ("rambutan merah manis banget")
        # akan mendapat skor rendah hanya karena kalimatnya panjang.
        panjang = max(1, len(token_kunci))
        jendela = [teks_jawaban] + [
            " ".join(token_jawab[i: i + panjang])
            for i in range(max(1, len(token_jawab) - panjang + 1))
        ]
        teks_kunci = [" ".join(token_kunci)]

        # transform() menghasilkan matriks TF-IDF; cosine_similarity() menghitung sudutnya.
        cos_kata = cosine_similarity(vektor_kata.transform(jendela), vektor_kata.transform(teks_kunci)).ravel()
        cos_huruf = cosine_similarity(vektor_huruf.transform(jendela), vektor_huruf.transform(teks_kunci)).ravel()
        skor_jendela = bobot_kata * cos_kata + (1 - bobot_kata) * cos_huruf

        terbaik = int(np.argmax(skor_jendela))
        if skor_jendela[terbaik] > hasil["skor"]:
            hasil.update(skor=float(skor_jendela[terbaik]), cos_kata=float(cos_kata[terbaik]),
                         cos_huruf=float(cos_huruf[terbaik]), kunci_terdekat=kunci_asli)

    # Keputusan akhir: membandingkan skor dengan ambang, bukan mencari kata yang sama persis.
    hasil["lulus"] = hasil["skor"] >= ambang
    hasil["hampir"] = not hasil["lulus"] and hasil["skor"] >= ambang * RASIO_HAMPIR
    return hasil


def nilai_alternatif(
    alternatif: list[str],
    pertanyaan: str,
    daftar_kunci: list[str],
    kode_cerita: str,
    ambang: float = AMBANG_LULUS,
) -> dict:
    """Menilai semua hipotesis ASR (n-best) lalu mengambil skor tertinggi.

    Hipotesis pertama ASR tidak selalu yang benar. Contoh nyata dari Google ASR untuk
    "Ke mana Kancil melompat?": pada satu percobaan hipotesis pertama "kemana kancil melo",
    yang benar baru di urutan ke-3. Hasil ASR bisa berbeda antarpercobaan.
    """
    semua = [nilai_jawaban(teks, pertanyaan, daftar_kunci, kode_cerita, ambang) for teks in alternatif]
    return max(semua, key=lambda hasil: hasil["skor"], default=hasil_nlp())  # seri: hipotesis paling awal
