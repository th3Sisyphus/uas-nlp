# -*- coding: utf-8 -*-
"""Penyaringan dan pembagian daftar cerita, tanpa Streamlit."""


def wilayah_dari_asal(asal: str) -> str:
    for wilayah, kata_kunci in (
        ("Jawa", ("jawa", "betawi")),
        ("Sumatera", ("sumatera", "riau")),
        ("Kalimantan", ("kalimantan",)),
        ("Sulawesi", ("sulawesi",)),
        ("Bali dan Nusa Tenggara", ("bali", "nusa tenggara")),
    ):
        if any(kata in asal.casefold() for kata in kata_kunci):
            return wilayah
    return "Nusantara"


def saring(daftar: list, wilayah: str, kata: str) -> list:
    kata = kata.casefold().strip()
    return [
        (kode, cerita) for kode, cerita in daftar
        if (wilayah == "Semua" or wilayah_dari_asal(cerita["asal"]) == wilayah)
        and kata in cerita["judul"].casefold()
    ]


def potong_halaman(daftar: list, nomor: int, per_halaman: int) -> tuple[list, int]:
    total = max(1, (len(daftar) + per_halaman - 1) // per_halaman)
    nomor = min(max(1, nomor), total)
    awal = (nomor - 1) * per_halaman
    return daftar[awal:awal + per_halaman], total
