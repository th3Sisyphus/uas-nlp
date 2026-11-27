/* Komponen mikrofon anak: rekam, deteksi suara, berhenti otomatis, kirim WAV.
   Kontrak DOM: akar .mik[data-status], #mik-tombol, #mik-label, 5 x .mik-bar,
   #mik-progres > i. Kejadian ke Python: rekaman, hening, izin_ditolak. */

import { rms, encodeWav, turunkanLaju, keBase64 } from "./mikrofon-inti.js";

const LABEL = {
  siap: "TEKAN, LALU BICARA",
  mendengarkan: "AKU MENDENGARKAN...",
  memproses: "SEDANG MEMPROSES...",
  nonaktif: "TUNGGU, KIKO SEDANG BICARA",
};

const LAJU_TARGET = 16000;
const KALIBRASI_MS = 300;
const MULAI_MINIMAL = 0.02;

export default function (component) {
  const { data, parentElement } = component;
  const kirim = component.setTriggerValue;
  const akar = parentElement.querySelector(".mik");
  if (!akar) return;

  const tombol = akar.querySelector("#mik-tombol");
  const label = akar.querySelector("#mik-label");
  const progres = akar.querySelector("#mik-progres");
  const isiProgres = progres.querySelector("i");
  const batang = [...akar.querySelectorAll(".mik-bar")];

  const idleDetik = Number(data?.idle_detik ?? 10);
  const heningDetik = Number(data?.hening_detik ?? 1.6);
  const maksDetik = Number(data?.maks_detik ?? 10);
  const tundaDetik = Number(data?.tunda_detik ?? 0);
  const statusPython = data?.status;

  let status = "siap";
  let sesi = null;
  let tunda = null;

  const pasang = (baru) => {
    status = baru;
    akar.dataset.status = baru;
    label.textContent = LABEL[baru];
    tombol.setAttribute("aria-label", LABEL[baru]);
    if (baru !== "mendengarkan") batang.forEach((b) => { b.style.transform = "scaleY(0.3)"; });
    if (baru === "siap" || baru === "nonaktif") aturProgres(0);
  };

  const aturProgres = (persen) => {
    const nilai = Math.max(0, Math.min(100, Math.round(persen)));
    isiProgres.style.width = `${nilai}%`;
    progres.setAttribute("aria-valuenow", String(nilai));
  };

  // Status awal: nonaktif dulu sampai tunda_detik lewat, kecuali Python bilang memproses.
  // tundaDetik negatif berarti nonaktif tanpa batas (menunggu narasi selesai).
  if (statusPython === "memproses") {
    pasang("memproses");
  } else if (statusPython === "nonaktif" || tundaDetik !== 0) {
    pasang("nonaktif");
    if (tundaDetik > 0) {
      tunda = setTimeout(() => { if (status === "nonaktif") pasang("siap"); }, tundaDetik * 1000);
    }
  } else {
    pasang("siap");
  }

  const bersihkan = () => {
    if (!sesi) return;
    const s = sesi;
    sesi = null;
    cancelAnimationFrame(s.reff);
    try { s.node?.disconnect(); } catch (_) {}
    try { s.sumber?.disconnect(); } catch (_) {}
    try { s.analisa?.disconnect(); } catch (_) {}
    s.stream?.getTracks().forEach((t) => t.stop());
    if (s.ctx && s.ctx.state !== "closed") s.ctx.close().catch(() => {});
  };

  const kirimRekaman = () => {
    if (!sesi) return;
    const s = sesi;
    const durasiDetik = s.potongan.reduce((n, p) => n + p.length, 0) / s.ctx.sampleRate;
    const gabung = new Float32Array(s.potongan.reduce((n, p) => n + p.length, 0));
    let pos = 0;
    s.potongan.forEach((p) => { gabung.set(p, pos); pos += p.length; });
    const pcm16 = turunkanLaju(gabung, s.ctx.sampleRate, LAJU_TARGET);
    bersihkan();
    pasang("memproses");
    aturProgres(100);
    kirim("rekaman", { wav_base64: keBase64(encodeWav(pcm16, LAJU_TARGET)), durasi_detik: durasiDetik });
  };

  const kirimHening = () => {
    bersihkan();
    pasang("memproses");
    aturProgres(100);
    kirim("hening", {});
  };

  const berhenti = () => {
    if (sesi?.sudahUcap) kirimRekaman();
    else if (sesi) kirimHening();
  };

  const mulai = async () => {
    if (sesi || status !== "siap") return;
    pasang("memproses");

    let stream;
    try {
      stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    } catch (_) {
      pasang("siap");
      kirim("izin_ditolak", {});
      return;
    }

    const ctx = new AudioContext();
    const sumber = ctx.createMediaStreamSource(stream);
    const analisa = ctx.createAnalyser();
    analisa.fftSize = 2048;
    sumber.connect(analisa);

    sesi = {
      stream, ctx, sumber, analisa,
      buf: new Float32Array(analisa.fftSize),
      potongan: [],
      mulai: performance.now(),
      sudahUcap: false,
      mulaiUcap: 0,
      heningSejak: 0,
      kebisingan: 0,
      jumlahKalibrasi: 0,
      kalibrasiSelesai: false,
      reff: 0,
    };
    const s = sesi;

    // Keluaran suara: AudioWorklet, cadangan ScriptProcessor. Keduanya tanpa ffmpeg.
    try {
      const url = URL.createObjectURL(new Blob([`
        class Perekam extends AudioWorkletProcessor {
          process(inputs) {
            const ch = inputs[0] && inputs[0][0];
            if (ch) this.port.postMessage(ch.slice(0));
            return true;
          }
        }
        registerProcessor("perekam-mik", Perekam);
      `], { type: "text/javascript" }));
      await ctx.audioWorklet.addModule(url);
      URL.revokeObjectURL(url);
      const node = new AudioWorkletNode(ctx, "perekam-mik");
      node.port.onmessage = (e) => { if (sesi === s) s.potongan.push(e.data); };
      sumber.connect(node);
      const bisu = ctx.createGain();
      bisu.gain.value = 0;
      node.connect(bisu).connect(ctx.destination);
      s.node = node;
    } catch (_) {
      const node = ctx.createScriptProcessor(4096, 1, 1);
      node.onaudioprocess = (e) => {
        if (sesi === s) s.potongan.push(new Float32Array(e.inputBuffer.getChannelData(0)));
      };
      sumber.connect(node);
      const bisu = ctx.createGain();
      bisu.gain.value = 0;
      node.connect(bisu).connect(ctx.destination);
      s.node = node;
    }

    pasang("mendengarkan");

    const detak = () => {
      if (sesi !== s) return;
      const sekarang = performance.now();
      analisa.getFloatTimeDomainData(s.buf);
      const energi = rms(s.buf);

      // Kalibrasi kebisingan 300 ms pertama.
      if (!s.kalibrasiSelesai) {
        s.kebisingan += energi;
        s.jumlahKalibrasi += 1;
        if (sekarang - s.mulai >= KALIBRASI_MS) {
          s.kebisingan /= Math.max(1, s.jumlahKalibrasi);
          s.kalibrasiSelesai = true;
        }
      }

      const ambang = Math.max(3 * s.kebisingan, MULAI_MINIMAL);
      if (energi > ambang) {
        if (!s.sudahUcap) {
          s.sudahUcap = true;
          s.mulaiUcap = sekarang;
        }
        s.heningSejak = 0;
      } else if (s.sudahUcap && !s.heningSejak) {
        s.heningSejak = sekarang;
      }

      // Meter: 5 batang, tinggi 8-28 px.
      const skala = Math.min(1, energi / Math.max(MULAI_MINIMAL, ambang));
      batang.forEach((b, i) => {
        const goyang = 0.55 + 0.45 * Math.abs(Math.sin((i + 1) * 1.1 + sekarang / 180));
        const tinggi = 8 + 20 * skala * goyang;
        b.style.transform = `scaleY(${(tinggi / 44).toFixed(3)})`;
      });

      // Progres: waktu idle sebelum ucapan, lalu waktu maksimum setelah ucapan mulai.
      if (s.sudahUcap) aturProgres(((sekarang - s.mulaiUcap) / 1000 / maksDetik) * 100);
      else aturProgres(((sekarang - s.mulai) / 1000 / idleDetik) * 100);

      // Berhenti otomatis.
      if (s.sudahUcap) {
        if (sekarang - s.mulaiUcap >= maksDetik * 1000) return kirimRekaman();
        if (s.heningSejak && sekarang - s.heningSejak >= heningDetik * 1000) return kirimRekaman();
      } else if (sekarang - s.mulai >= idleDetik * 1000) {
        return kirimHening();
      }
      s.reff = requestAnimationFrame(detak);
    };
    s.reff = requestAnimationFrame(detak);
  };

  tombol.addEventListener("click", () => {
    if (status === "siap") mulai();
    else if (status === "mendengarkan") berhenti();
  });

  return () => {
    clearTimeout(tunda);
    bersihkan();
  };
}
