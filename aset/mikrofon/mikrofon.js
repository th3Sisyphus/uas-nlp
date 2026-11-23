/* Stub komponen mikrofon: membaca status dari data Python dan memasangnya di DOM.
   Perekaman suara belum ada di tugas ini; perilaku tombol menyusul. */

const LABEL = {
  siap: "TEKAN, LALU BICARA",
  mendengarkan: "AKU MENDENGARKAN...",
  memproses: "SEDANG MEMPROSES...",
  nonaktif: "TUNGGU, KIKO SEDANG BICARA",
};

const STATUS_SAH = Object.keys(LABEL);

export default function (component) {
  const { data, parentElement, setStateValue } = component;
  const akar = parentElement.querySelector(".mik");
  if (!akar) return;

  const tombol = akar.querySelector("#mik-tombol");
  const label = akar.querySelector("#mik-label");
  const progres = akar.querySelector("#mik-progres");
  const isiProgres = progres.querySelector("i");

  const status = STATUS_SAH.includes(data?.status) ? data.status : "siap";

  akar.dataset.status = status;
  label.textContent = LABEL[status];
  tombol.disabled = status === "nonaktif";
  tombol.setAttribute("aria-label", LABEL[status]);

  // Pratinjau tanpa perekaman: progres hanya contoh visual (60% saat mendengarkan).
  const persen = status === "mendengarkan" ? 60 : 0;
  isiProgres.style.width = `${persen}%`;
  progres.setAttribute("aria-valuenow", String(persen));

  if (typeof setStateValue === "function") {
    setStateValue("status_terpasang", status);
  }
}
