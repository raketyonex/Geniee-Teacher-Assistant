import json
import shutil
import streamlit as st
from geniee import youtube_dl, create_pdf, create_txt, Geniee


st.set_page_config("GENIEE | Generate Exam", page_icon=':🪄:', initial_sidebar_state="expanded")


_, tengah, _ = st.columns([1, 2, 1])
with tengah:
    st.image('./logo/logo.png', use_container_width=True)

st.write("----")
kiri, kanan = st.columns(2)
with kiri:
    mode = st.selectbox("**Sumber Materi**", ["Files", "YouTube"])
    if mode == "Files":
        materi = st.file_uploader("**Unggah Files**", type=['pdf', 'docx', 'pptx', 'txt', 'mp3', 'mp4'], accept_multiple_files=True)

    elif mode == "YouTube":
        url = st.text_input("**URL YouTube**", placeholder="https://", help="Masukan URL YouTube")
        st.error("Fitur masih dalam tahap pengembangan. Gunakan sumber materi files!!", icon="🚨")
        if url:
            with st.spinner("Bentar ya, video lagi di download!"):
                materi = youtube_dl(url)

with kanan:
    pelajaran = st.text_input("**Pelajaran**", placeholder="Matematika")
    c1, c2 = st.columns(2)
    with c1:
        tipe = st.selectbox("**Tipe Soal**", options=['Pilihan Ganda', 'Essay'])

    with c2:
        jumlah = st.number_input("**Jumlah**", min_value=1, max_value=15, help="Soal tidak boleh lebih dari 15")
        st.write("")
        button = st.button("**Generate Soal**", type='primary', use_container_width=True)
st.write("----")


if button:
    if materi and pelajaran:
        with st.spinner("**Agak lama nih, bentar ya!!**"):
            soal = Geniee(materi, pelajaran, jumlah, tipe)

            clean_json = soal.response.replace('```json', '').replace('```', '').strip()
            data = json.loads(clean_json)

            if tipe == 'Pilihan Ganda':
                for nomor, soal in enumerate(data["soal"], start=1):
                    st.write(f"{nomor}.", soal["pertanyaan"])
                    for opsi in soal["opsi"]:
                        st.write(opsi)

                    st.write(f"{nomor}.", soal["kunci_jawaban"])
                    st.write("---")

            elif tipe == 'Essay':
                for nomor, soal in enumerate(data["soal"], start=1):
                    st.write(f"{nomor}.", soal["pertanyaan"])

                    st.write(f"{nomor}.", soal["kunci_jawaban"])
                    st.write("---")

            pdf_buffer = create_pdf(data['soal'])
            txt_data = create_txt(data['soal'])

            st.download_button(
                label="Unduh Soal",
                data=pdf_buffer,
                file_name="soal.pdf",
                mime="application/pdf",
                type="primary"
            )

            st.download_button(
                label="Unduh Kunci Jawaban",
                data=txt_data,
                file_name="kunci_jawaban.txt",
                mime="text/plain",
                type="primary"
            )

            shutil.rmtree('data', ignore_errors=True)
            shutil.rmtree('temp', ignore_errors=True)
    else:
        with kiri:
            st.error("Sepertinya Anda lupa mengunggah materi dan menginput pelajaran.", icon="🚨")