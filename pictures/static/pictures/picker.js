// Click the map to fill in the latitude and longitude fields.
document.addEventListener("DOMContentLoaded", () => {
  const lat = document.getElementById("id_latitude");
  const lon = document.getElementById("id_longitude");
  const map = L.map("picker").setView([20, 0], 2);
  L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 19,
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
  }).addTo(map);

  let marker = null;
  const place = (latlng) => {
    if (marker) marker.setLatLng(latlng);
    else marker = L.marker(latlng).addTo(map);
  };
  const fromFields = () => {
    const a = parseFloat(lat.value);
    const b = parseFloat(lon.value);
    if (!Number.isNaN(a) && !Number.isNaN(b)) {
      place([a, b]);
      map.setView([a, b], 8);
    }
  };
  map.on("click", (event) => {
    const point = event.latlng.wrap();
    lat.value = point.lat.toFixed(6);
    lon.value = point.lng.toFixed(6);
    place(point);
  });
  lat.addEventListener("change", fromFields);
  lon.addEventListener("change", fromFields);
  fromFields();
});
