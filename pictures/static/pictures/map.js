// Show every picture as a marker. Titles and descriptions are user input, so the popup is built from
// DOM nodes with textContent, never from HTML strings.
document.addEventListener("DOMContentLoaded", () => {
  const element = document.getElementById("map");
  const filter = document.getElementById("user-filter");
  const map = L.map(element).setView([20, 0], 2);
  L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 19,
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
  }).addTo(map);
  const layer = L.layerGroup().addTo(map);

  const popup = (picture) => {
    const box = document.createElement("div");
    box.className = "popup";
    const title = document.createElement("strong");
    title.textContent = picture.title;
    const image = document.createElement("img");
    image.src = picture.image;
    image.alt = picture.title;
    const by = document.createElement("small");
    by.textContent = `${picture.owner}, ${new Date(picture.created).toLocaleDateString()}`;
    box.append(title, image);
    if (picture.description) {
      const text = document.createElement("p");
      text.textContent = picture.description;
      box.append(text);
    }
    box.append(by);
    return box;
  };

  const load = async () => {
    const url = new URL(element.dataset.url, window.location.href);
    if (filter.value) url.searchParams.set("user", filter.value);
    const response = await fetch(url, { credentials: "same-origin" });
    if (!response.ok) return;
    const { pictures } = await response.json();
    layer.clearLayers();
    const points = [];
    for (const picture of pictures) {
      const point = [picture.latitude, picture.longitude];
      points.push(point);
      L.marker(point).bindPopup(popup(picture), { minWidth: 220 }).addTo(layer);
    }
    if (points.length) map.fitBounds(points, { maxZoom: 10, padding: [30, 30] });
  };
  filter.addEventListener("change", load);
  load();
});
