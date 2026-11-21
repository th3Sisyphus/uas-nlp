"""Validasi korpus cerita rakyat. Jalankan: python docs/cerita-rakyat/validasi.py [folder]
Kode keluar 0 jika tidak ada GALAT. PERINGATAN tidak menggagalkan."""
import json, re, sys
from pathlib import Path

LATAR = {"sungai", "senja", "ladang", "bambu", "lumpur", "pantai", "dermaga", "badai", "polos"}
GAMBAR = {"batu", "pohon", "kancil", "rambutan"}
WAJIB_CERITA = {"judul", "asal", "ajaran", "warna", "adegan"}
WAJIB_ADEGAN = {"narasi", "tanya", "kunci", "utama", "petunjuk", "stiker", "gambar"}
HEX = re.compile(r"^#[0-9A-Fa-f]{6}$")
# GALAT bila muncul; PERINGATAN bila muncul
KERAS = re.compile(r"\b(membunuh|bunuh|mati|meninggal|tewas|dikubur|dibakar|disiksa|"
                   r"mengintip|judi|merampok|korban|dendam|durhaka)\b", re.I)
LUNAK = re.compile(r"\b(kutukan|mengutuk|dikutuk|dikutuk|terkena kutukan|perang)\b", re.I)

def norm(s): return re.sub(r"[^a-z0-9 ]", "", s.lower().replace("'", ""))

def periksa(f, kode_dipakai, galat, peringatan):
    def G(m): galat.append(f"{f.name}: {m}")
    def P(m): peringatan.append(f"{f.name}: {m}")
    try: d = json.loads(f.read_text(encoding="utf-8"))
    except Exception as e: return G(f"JSON tidak valid ({e})")
    kode = re.sub(r"^\d+_", "", f.stem)
    if not re.fullmatch(r"[a-z0-9]+", kode): G(f"kode '{kode}' harus huruf kecil tanpa spasi")
    if kode in kode_dipakai: G(f"kode '{kode}' bentrok dengan {kode_dipakai[kode]}")
    kode_dipakai[kode] = f.name
    if (k := WAJIB_CERITA - d.keys()): return G(f"kolom cerita kurang: {sorted(k)}")
    w = d["warna"]
    if not (isinstance(w, dict) and {"dunia", "aksen", "kartu"} <= w.keys() and all(HEX.match(str(v)) for v in w.values())):
        G("warna harus berisi dunia, aksen, kartu berformat #RRGGBB")
    ad = d["adegan"]
    if not 3 <= len(ad) <= 5: G(f"jumlah adegan {len(ad)} (harus 3-5)")
    for n, a in enumerate(ad, 1):
        t = f"adegan {n}"
        if (k := WAJIB_ADEGAN - a.keys()): G(f"{t}: kolom kurang {sorted(k)}"); continue
        kal = [x for x in re.split(r"(?<=[.!?])\s+", a["narasi"].strip()) if x]
        if not 3 <= len(kal) <= 4: G(f"{t}: narasi {len(kal)} kalimat (harus 3-4)")
        for x in kal:
            if len(x.split()) > 10: G(f"{t}: kalimat > 10 kata: '{x[:40]}...'")
        if not (isinstance(a["kunci"], list) and 1 <= len(a["kunci"]) <= 4): G(f"{t}: kunci harus 1-4 item")
        elif a["utama"] != a["kunci"][0]: G(f"{t}: utama harus sama dengan kunci[0]")
        elif any(x != x.lower() for x in a["kunci"]): G(f"{t}: kunci harus huruf kecil")
        else:
            nar = norm(a["narasi"])
            if not any(norm(x) in nar for x in a["kunci"]):
                G(f"{t}: jawaban tidak tertulis di narasi")
        if len(a["petunjuk"].split()) > 10: G(f"{t}: petunjuk > 10 kata")
        if not a["stiker"] or len(a["stiker"]) > 8: G(f"{t}: stiker harus satu emoji")
        g = a["gambar"]
        if g.get("latar") not in LATAR: G(f"{t}: latar '{g.get('latar')}' tidak tersedia")
        ob = g.get("objek", [])
        if not 1 <= len(ob) <= 5: G(f"{t}: objek harus 1-5")
        for o in ob:
            if "emoji" in o and not {"x", "y", "ukuran"} <= o.keys(): G(f"{t}: objek emoji butuh x,y,ukuran")
            elif "emoji" not in o and o.get("gambar") not in GAMBAR: G(f"{t}: gambar '{o.get('gambar')}' tidak ada")
            if not (60 <= o.get("x", 0) <= 900 and 60 <= o.get("y", 0) <= 440): G(f"{t}: koordinat di luar kanvas")
        isi = " ".join([a["narasi"], a["tanya"], a["petunjuk"], d["ajaran"]])
        if (m := KERAS.search(isi)): G(f"{t}: kata terlarang '{m.group(0)}'")
        if (m := LUNAK.search(isi)): P(f"{t}: sebaiknya hindari '{m.group(0)}'")

def main():
    folder = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent
    berkas = sorted(p for p in folder.glob("*.json") if re.match(r"\d+_", p.name))
    galat, peringatan, kode = [], [], {}
    for f in berkas: periksa(f, kode, galat, peringatan)
    print(f"{len(berkas)} berkas diperiksa | {len(galat)} GALAT | {len(peringatan)} peringatan")
    for x in galat: print("GALAT      ", x)
    for x in peringatan: print("peringatan ", x)
    sys.exit(1 if galat else 0)

if __name__ == "__main__":
    main()