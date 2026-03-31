self.addEventListener("install", event => {
  console.log("Service Worker instalado");
});

self.addEventListener("fetch", event => {
  event.respondWith(fetch(event.request));
});
new Chart(document.getElementById("grafico"), {
    type: "pie",
    data: {
        labels: labels,
        datasets: [{
            data: valores
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false
    }
});
function capturar() {
    let canvas = document.getElementById("canvas");
    let video = document.getElementById("video");

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    canvas.getContext("2d").drawImage(video, 0, 0);

    let imagem = canvas.toDataURL("image/png");
    document.getElementById("foto").value = imagem;
}
