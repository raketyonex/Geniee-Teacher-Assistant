import os
from dotenv import load_dotenv

import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from pytubefix import YouTube

from llama_index.core import (
    Settings,
    SimpleDirectoryReader,
    VectorStoreIndex,
    StorageContext,
    load_index_from_storage
)

from llama_index.llms.groq import Groq
from llama_index.embeddings.huggingface import HuggingFaceEmbedding


load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

Settings.llm = Groq(
    api_key=api_key,
    # model="llama-3.1-70b-versatile",
    model="gemma2-9b-it",
    temperature=0.6,
    max_tokens=4096,
    streaming=True,
)
Settings.embed_model = HuggingFaceEmbedding(
    model_name='sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2',
    cache_folder='./embedding',
    device="cpu"
)
Settings.context_window = 8192


def create_pdf(soal_data):
    pdf_buffer = io.BytesIO()
    c = canvas.Canvas(pdf_buffer, pagesize=letter)

    c.setFont("Helvetica", 12)
    y_position = 750

    for nomor, soal in enumerate(soal_data, start=1):
        c.drawString(100, y_position, f"**{nomor}.** {soal['pertanyaan']}")
        y_position -= 20
        for opsi in soal["opsi"]:
            c.drawString(120, y_position, opsi)
            y_position -= 15
        y_position -= 10

    c.save()
    pdf_buffer.seek(0)
    return pdf_buffer


def create_txt(soal_data):
    txt_buffer = io.StringIO()
    for nomor, soal in enumerate(soal_data, start=1):
        txt_buffer.write(f"Jawaban {nomor}: {soal['kunci_jawaban']}\n")
    return txt_buffer.getvalue()


def youtube_dl(url):
    yt = YouTube(url)
    ys = yt.streams
    audio = ys.get_audio_only().download("temp/", filename="audio.mp3")

    return audio


def Geniee(materi, pelajaran, jumlah, tipe):
    temp_dir = './temp/'
    data_dir = './data/'

    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)

    if not os.listdir(temp_dir):
        if materi:
            for file in materi:
                with open(os.path.join(temp_dir, file.name), "wb") as f:
                    f.write(file.getbuffer())

    if not os.path.exists(data_dir):
        documents = SimpleDirectoryReader(input_dir=temp_dir).load_data()
        store = VectorStoreIndex.from_documents(documents)
        store.storage_context.persist(persist_dir=data_dir)

    context = StorageContext.from_defaults(persist_dir=data_dir)
    index = load_index_from_storage(context)

    query = f'''
        Buatkan soal ujian untuk pelajaran {pelajaran} sebanyak {jumlah} soal dengan tipe soal {tipe}.
        Hanya berikan hasil generate berupa JSON.
        Format JSON untuk tipe soal Pilihan Ganda:
        {{
            "soal": [
                {{
                    "pertanyaan": "",
                    "opsi": [
                        "A.",
                        "B.",
                        "C.",
                        "D.",
                        "E."
                    ],
                    "kunci_jawaban": "(kunci jawaban untuk koreksi)"
                }}
            ]
        }}.
        Format JSON untuk tipe soal Essay:
        {{
            "soal": [
                {{
                    "pertanyaan": "",
                    "kunci_jawaban": "(kucni jawaban untuk koreksi. Tanpa penjelasan lanjutan!)"
                }}
            ]
        }}.
    '''

    engine = index.as_query_engine(similarity_top_k=20)
    resp = engine.query(query)
    return resp