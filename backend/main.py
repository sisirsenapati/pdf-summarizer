from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

import pymupdf  # PyMuPDF
import tempfile
import re

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer
)
from reportlab.lib.styles import getSampleStyleSheet

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"status": "running"}


@app.post("/summarize")
async def summarize_pdf(file: UploadFile = File(...)):

    # Save uploaded PDF temporarily
    temp_pdf = tempfile.mktemp(".pdf")

    with open(temp_pdf, "wb") as f:
        f.write(await file.read())

    # Extract text from PDF
    text = ""

    pdf = pymupdf.open(temp_pdf)

    for page in pdf:
        text += page.get_text()

    pdf.close()

    # Clean text
    text = text.replace("\n", " ")
    text = re.sub(r"\s+", " ", text)

    # Split into sentences
    sentences = re.split(r'(?<=[.!?])\s+', text)

    # Take first 15 meaningful sentences
    summary_sentences = []

    for sentence in sentences:
        sentence = sentence.strip()

        if len(sentence) > 30:
            summary_sentences.append(sentence)

        if len(summary_sentences) >= 15:
            break

    # Build bullet summary
    summary_text = ""

    for sentence in summary_sentences:
        summary_text += f"• {sentence}\n\n"

    # Generate summary PDF
    output_pdf = tempfile.mktemp(".pdf")

    doc = SimpleDocTemplate(output_pdf)

    styles = getSampleStyleSheet()

    elements = []

    elements.append(
        Paragraph(
            "PDF Summary",
            styles["Title"]
        )
    )

    elements.append(Spacer(1, 12))

    for line in summary_text.split("\n\n"):

        if line.strip():

            elements.append(
                Paragraph(
                    line,
                    styles["BodyText"]
                )
            )

            elements.append(
                Spacer(1, 6)
            )

    doc.build(elements)

    return FileResponse(
        output_pdf,
        media_type="application/pdf",
        filename="summary.pdf"
    )