from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

import fitz
import tempfile
import os

from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.text_rank import TextRankSummarizer

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer
)

from reportlab.lib.styles import getSampleStyleSheet

app = FastAPI()

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

    temp_pdf = tempfile.mktemp(".pdf")

    with open(temp_pdf, "wb") as f:
        f.write(await file.read())

    text = ""

    pdf = fitz.open(temp_pdf)

    for page in pdf:
        text += page.get_text()

    pdf.close()

    parser = PlaintextParser.from_string(
        text,
        Tokenizer("english")
    )

    summarizer = TextRankSummarizer()

    summary_sentences = summarizer(
        parser.document,
        15
    )

    summary_text = ""

    for sentence in summary_sentences:
        summary_text += "• " + str(sentence) + "\n\n"

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