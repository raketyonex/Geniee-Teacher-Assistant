import json
import shutil
import streamlit as st
from geniee import youtube_dl, unduh_soal, unduh_jawaban, Geniee


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
        url = st.text_input("**URL YouTube**", placeholder="https://www.youtube.com/", help="Masukan URL YouTube")
        if url:
            materi = youtube_dl(url)
        st.error("Fitur masih dalam tahap pengembangan. Gunakan **Sumber Materi Files**!!", icon="🚨")

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


if 'soal_data' not in st.session_state:
    st.session_state.soal_data = None

if button:
    if materi and pelajaran:
        try:
            with st.spinner("**Agak lama nih, bentar ya!!**"):
                soal = Geniee(materi, pelajaran, jumlah, tipe)

                clean_json = soal.response.replace('```json', '').replace('```', '').strip()
                data = json.loads(clean_json)

                st.session_state.soal_data = data

        except (ImportError, NameError, ModuleNotFoundError):
            st.error("Sudah dibilang fitur masih dalam tahap pengembangan. Gunakan **Sumber Materi Files**!!")

    else:
        with kiri:
            st.error("Sepertinya Anda lupa mengunggah materi dan menginput pelajaran.", icon="🚨")

if st.session_state.soal_data:
    data = st.session_state.soal_data

    b1, b2 = st.columns(2)
    with b1:
        pdf_buffer = unduh_soal(data['soal'])
        st.download_button(
            label="Unduh Soal",
            data=pdf_buffer,
            file_name="soal.pdf",
            mime="application/pdf",
            type="primary",
            use_container_width=True
        )

    with b2:
        txt_data = unduh_jawaban(data['soal'])
        st.download_button(
            label="Unduh Kunci Jawaban",
            data=txt_data,
            file_name="kunci_jawaban.txt",
            mime="text/plain",
            type="primary",
            use_container_width=True
        )

    if tipe == 'Pilihan Ganda':
        for nomor, soal in enumerate(data["soal"], start=1):
            st.write(f"{nomor}.", soal["pertanyaan"])
            for opsi in soal["opsi"]:
                st.write(opsi)

            st.write("**Kunci Jawaban:**", soal["kunci_jawaban"])
            st.write("---")

    elif tipe == 'Essay':
        for nomor, soal in enumerate(data["soal"], start=1):
            st.write(f"{nomor}.", soal["pertanyaan"])

            st.write("**Kunci Jawaban:**", soal["kunci_jawaban"])
            st.write("---")

    shutil.rmtree('data', ignore_errors=True)
    shutil.rmtree('temp', ignore_errors=True)