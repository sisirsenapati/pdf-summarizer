async function summarizePDF() {

    const file =
    document.getElementById("pdfFile")
    .files[0];

    if (!file) {

        alert("Select PDF");

        return;
    }

    document.getElementById(
        "status"
    ).innerText =
    "Processing PDF...";

    const formData =
    new FormData();

    formData.append(
        "file",
        file
    );

    const response =
    await fetch(
        "https://YOUR-RENDER-URL.onrender.com/summarize",
        {
            method:"POST",
            body:formData
        }
    );

    const blob =
    await response.blob();

    const url =
    window.URL.createObjectURL(
        blob
    );

    const a =
    document.createElement(
        "a"
    );

    a.href = url;

    a.download =
    "summary.pdf";

    a.click();

    document.getElementById(
        "status"
    ).innerText =
    "Summary generated.";
}