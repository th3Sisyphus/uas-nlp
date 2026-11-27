/* Narator video: memutar klip MP4 berlatar hijau dan menghapus latarnya di canvas.
   Kontrak DOM: akar .nar-vid > canvas. Data: {"src", "ulang"}.
   Latar hijau dibuang per piksel, jadi karakter tampil di atas warna dunia apa pun
   tanpa perlu mengekspor ulang video dengan alfa. */

export default function (component) {
  const { data, parentElement } = component;
  const akar = parentElement.querySelector(".nar-vid");
  if (!akar) return;

  const kanvas = akar.querySelector("canvas");
  const konteks = kanvas.getContext("2d", { willReadFrequently: true });
  if (!konteks) return;

  const video = document.createElement("video");
  video.src = data?.src ?? "";
  video.muted = true;
  video.playsInline = true;
  video.preload = "auto";
  // Autoplay hanya boleh untuk video tanpa suara; atribut ini yang membuat peramban mau.
  video.setAttribute("muted", "");
  video.setAttribute("playsinline", "");
  video.loop = data?.ulang !== false;

  let reff = 0;
  let jalan = false;

  // Ambang chroma key. Hijau latar video kira-kira #28A02F; selisih kanal hijau
  // terhadap kanal merah dan biru dipakai supaya bagian hangat karakter tidak ikut hilang.
  const AMBANG = 34;
  const LEMBUT = 40;

  const gambar = () => {
    if (!jalan) return;
    if (video.readyState >= 2) {
      const w = video.videoWidth;
      const h = video.videoHeight;
      if (w && h) {
        if (kanvas.width !== w || kanvas.height !== h) {
          kanvas.width = w;
          kanvas.height = h;
        }
        konteks.drawImage(video, 0, 0, w, h);
        const data = konteks.getImageData(0, 0, w, h);
        const piksel = data.data;
        for (let i = 0; i < piksel.length; i += 4) {
          const r = piksel[i];
          const g = piksel[i + 1];
          const b = piksel[i + 2];
          // Seberapa "hijau" piksel ini dibanding kedua kanal lain.
          const kehijauan = g - Math.max(r, b);
          if (kehijauan <= AMBANG) continue;
          if (kehijauan >= AMBANG + LEMBUT) {
            piksel[i + 3] = 0;
          } else {
            // Tepi lembut supaya garis karakter tidak bergerigi.
            piksel[i + 3] = Math.round(255 * (1 - (kehijauan - AMBANG) / LEMBUT));
            // Kurangi tumpahan hijau pada piksel semi-transparan.
            piksel[i + 1] = Math.round(Math.max(r, b) + (g - Math.max(r, b)) * 0.25);
          }
        }
        konteks.putImageData(data, 0, 0);
      }
    }
    reff = requestAnimationFrame(gambar);
  };

  const mulai = () => {
    if (jalan) return;
    jalan = true;
    const janji = video.play();
    if (janji && typeof janji.catch === "function") {
      // Autoplay diblokir: tampilkan bingkai pertama saja supaya gelembung tetap terbaca.
      janji.catch(() => { jalan = false; });
    }
    reff = requestAnimationFrame(gambar);
  };

  video.addEventListener("loadeddata", mulai);
  video.addEventListener("error", () => {
    akar.dataset.gagal = "1";
  });

  if (video.readyState >= 2) mulai();
  else video.load();

  return () => {
    if (reff) cancelAnimationFrame(reff);
    jalan = false;
    video.pause();
    video.removeAttribute("src");
    video.load();
  };
}
