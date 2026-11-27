/* Komponen pemutar suara narator: putar, jeda, progres, berhenti di akhir.
   Kontrak DOM: akar .spk[data-status], #spk-tombol, #spk-label, 5 x .spk-bar,
   #spk-progres > i. Data: {"audio_base64", "mime", "autoplay", "status"}.
   Kejadian ke Python: selesai, setelah audio benar-benar habis. */

const LABEL = {
  siap: "PUTAR SUARA",
  memutar: "SEDANG BERBICARA...",
  nonaktif: "SUARA BELUM TERSEDIA",
};

export default function (component) {
  const { data, parentElement } = component;
  const kirim = component.setTriggerValue;
  const akar = parentElement.querySelector(".spk");
  if (!akar) return;

  const tombol = akar.querySelector("#spk-tombol");
  const label = akar.querySelector("#spk-label");
  const progres = akar.querySelector("#spk-progres");
  const isiProgres = progres.querySelector("i");

  const dasar64 = data?.audio_base64;
  const mime = data?.mime || "audio/mpeg";
  const autoplay = data?.autoplay !== false;
  const statusAwal = data?.status;

  let status = "siap";
  let audio = null;
  let reff = 0;
  let dikirim = false;

  const pasang = (baru) => {
    status = baru;
    akar.dataset.status = baru;
    label.textContent = LABEL[baru] || LABEL.siap;
    tombol.setAttribute("aria-label", LABEL[baru] || LABEL.siap);
  };

  const aturProgres = (persen) => {
    const nilai = Math.max(0, Math.min(100, Math.round(persen)));
    isiProgres.style.width = `${nilai}%`;
    progres.setAttribute("aria-valuenow", String(nilai));
  };

  const hentikanDetak = () => {
    if (reff) cancelAnimationFrame(reff);
    reff = 0;
  };

  const detak = () => {
    if (!audio) return;
    const lama = Number.isFinite(audio.duration) && audio.duration > 0 ? audio.duration : 0;
    aturProgres(lama ? (audio.currentTime / lama) * 100 : 0);
    reff = requestAnimationFrame(detak);
  };

  const mulaiDetak = () => {
    hentikanDetak();
    reff = requestAnimationFrame(detak);
  };

  // Tanpa audio: kirim "selesai" sekali supaya Python tidak menunggu selamanya.
  const laporSelesai = () => {
    if (dikirim) return;
    dikirim = true;
    kirim("selesai", {});
  };

  if (!dasar64 || statusAwal === "nonaktif") {
    pasang("nonaktif");
    laporSelesai();
    return () => { hentikanDetak(); };
  }

  audio = new Audio(`data:${mime};base64,${dasar64}`);
  audio.preload = "auto";

  audio.addEventListener("ended", () => {
    hentikanDetak();
    aturProgres(100);
    pasang("siap");
    laporSelesai();
  });

  audio.addEventListener("pause", () => {
    if (status === "memutar" && !audio.ended) {
      hentikanDetak();
      pasang("siap");
    }
  });

  pasang("siap");

  tombol.addEventListener("click", () => {
    if (status === "memutar") {
      audio.pause();
      return;
    }
    if (status !== "siap") return;
    if (audio.ended || audio.currentTime >= (audio.duration || 0)) {
      audio.currentTime = 0;
      aturProgres(0);
    }
    pasang("memutar");
    mulaiDetak();
    const janji = audio.play();
    if (janji && typeof janji.catch === "function") {
      janji.catch(() => {
        hentikanDetak();
        pasang("siap");
      });
    }
  });

  if (autoplay) {
    pasang("memutar");
    mulaiDetak();
    const janji = audio.play();
    if (janji && typeof janji.catch === "function") {
      janji.catch(() => {
        // Autoplay diblokir: jangan kunci halaman, biarkan anak menekan tombol.
        hentikanDetak();
        pasang("siap");
        laporSelesai();
      });
    }
  }

  return () => {
    hentikanDetak();
    if (audio) {
      audio.pause();
      audio.removeAttribute("src");
      audio.load();
      audio = null;
    }
  };
}
