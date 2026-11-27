/* Fungsi murni komponen mikrofon, dipisah agar bisa diuji tanpa peramban.

   Uji dengan node:
     node --input-type=module -e "import('./aset/mikrofon/mikrofon-inti.js').then(m=>{
       const wav = m.encodeWav(new Float32Array(16000), 16000);
       const v = new DataView(wav.buffer);
       console.log(String.fromCharCode(...wav.slice(0,4)), v.getUint32(24,true), v.getUint16(22,true), v.getUint16(34,true));
     })"
   Keluaran yang diharapkan: "RIFF 16000 1 16". */

export function rms(buffer) {
  if (!buffer || buffer.length === 0) return 0;
  let jumlah = 0;
  for (let i = 0; i < buffer.length; i += 1) jumlah += buffer[i] * buffer[i];
  return Math.sqrt(jumlah / buffer.length);
}

/** PCM float32 (rentang -1..1) menjadi WAV 16 bit mono. sampleRate dipakai di header. */
export function encodeWav(pcm, sampleRate) {
  const jumlah = pcm.length;
  const buffer = new ArrayBuffer(44 + jumlah * 2);
  const lihat = new DataView(buffer);
  const tulisan = (pos, teks) => {
    for (let i = 0; i < teks.length; i += 1) lihat.setUint8(pos + i, teks.charCodeAt(i));
  };
  tulisan(0, "RIFF");
  lihat.setUint32(4, 36 + jumlah * 2, true);
  tulisan(8, "WAVE");
  tulisan(12, "fmt ");
  lihat.setUint32(16, 16, true);
  lihat.setUint16(20, 1, true);
  lihat.setUint16(22, 1, true);
  lihat.setUint32(24, sampleRate, true);
  lihat.setUint32(28, sampleRate * 2, true);
  lihat.setUint16(32, 2, true);
  lihat.setUint16(34, 16, true);
  tulisan(36, "data");
  lihat.setUint32(40, jumlah * 2, true);
  for (let i = 0; i < jumlah; i += 1) {
    const s = Math.max(-1, Math.min(1, pcm[i]));
    lihat.setInt16(44 + i * 2, s < 0 ? s * 0x8000 : s * 0x7fff, true);
  }
  return new Uint8Array(buffer);
}

/** Menurunkan laju sampel ke 16 kHz dengan rata-rata antar-sampel (tanpa pustaka). */
export function turunkanLaju(data, dari, ke) {
  if (dari === ke) return data;
  const rasio = dari / ke;
  const keluar = new Float32Array(Math.floor(data.length / rasio));
  for (let i = 0; i < keluar.length; i += 1) {
    const awal = Math.floor(i * rasio);
    const akhir = Math.min(Math.floor((i + 1) * rasio), data.length);
    let jumlah = 0;
    for (let j = awal; j < akhir; j += 1) jumlah += data[j];
    keluar[i] = jumlah / Math.max(1, akhir - awal);
  }
  return keluar;
}

export function keBase64(bytes) {
  let biner = "";
  const potong = 0x8000;
  for (let i = 0; i < bytes.length; i += potong) {
    biner += String.fromCharCode.apply(null, bytes.subarray(i, i + potong));
  }
  return btoa(biner);
}
