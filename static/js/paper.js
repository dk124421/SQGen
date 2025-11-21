document.getElementById("paper-form").addEventListener("submit", async function (e) {
    e.preventDefault();

    const btn = document.getElementById("generate-btn");
    const iframe = document.getElementById("pdf-viewer");
    const container = document.getElementById("output-container");

    btn.classList.add("loading");

    const formData = new FormData(this);

    const response = await fetch("{% url 'paper_generator' %}", {
        method: "POST",
        body: formData
    });

    const blob = await response.blob();
    const pdfURL = URL.createObjectURL(blob);

    iframe.src = pdfURL;

    // ✔ FIX — make visible
    container.style.display = "block";
    container.style.opacity = "1";
    container.style.transform = "translateY(0)";

    // Download button
    document.getElementById("download-btn").onclick = () => {
        const a = document.createElement("a");
        a.href = pdfURL;
        a.download = "Question_Paper.pdf";
        a.click();
    };

    btn.classList.remove("loading");
});