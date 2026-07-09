// Shared loader: fetch generated JSON from raw.githubusercontent (CDN, no API rate limits).
const REPO = "harsha-moparthy/placement-prep";
const RAW = `https://raw.githubusercontent.com/${REPO}/main/data/generated/`;
const PEOPLE = { harsha: "harsha-moparthy", akanksh: "AvAkanksh" };

async function loadData(file, fallbackMsg) {
  try {
    const r = await fetch(RAW + file, { cache: "no-cache" });
    if (!r.ok) throw new Error(r.status);
    const data = await r.json();
    const ageH = (Date.now() - new Date(data.generated)) / 36e5;
    if (ageH > 30) showBanner(`Data is ${Math.round(ageH)}h old — the refresh Action may have failed.`);
    return data;
  } catch (e) {
    showBanner(fallbackMsg || `No data yet (${e.message}). It appears after the first Action run.`);
    return null;
  }
}
function showBanner(msg) {
  const b = document.getElementById("banner");
  if (b) { b.textContent = msg; b.style.display = "block"; }
}
function el(tag, cls, text) {
  const e = document.createElement(tag);
  if (cls) e.className = cls;
  if (text != null) e.textContent = text;
  return e;
}
