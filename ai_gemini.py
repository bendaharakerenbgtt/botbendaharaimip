import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
import google.generativeai as genai
import os
import requests
import time

DEFAULT_KEY = "AQ." + "Ab8RN6LyEdnMI3b4irzecCHBL5w4Uw4lqD42qJcW44L7yKqdrQ"
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY") or DEFAULT_KEY

genai.configure(api_key=GEMINI_API_KEY)

URL_DOCS_PENGETAHUAN = os.environ.get("URL_DOCS_PENGETAHUAN", "")

def muat_pengetahuan():
    content = ""
    
    # 1. Coba muat dari Google Docs link jika disediakan
    if URL_DOCS_PENGETAHUAN:
        try:
            res = requests.get(URL_DOCS_PENGETAHUAN, timeout=5)
            if res.status_code == 200:
                content += res.text + "\n\n"
        except Exception as e:
            print("Gagal mengambil pengetahuan dari link:", e)

    # 2. Coba muat dari file pengetahuan_imip.txt lokal/GitHub
    if os.path.exists("pengetahuan_imip.txt"):
        try:
            with open("pengetahuan_imip.txt", "r", encoding="utf-8") as f:
                content += f.read()
        except Exception as e:
            print("Gagal membaca pengetahuan_imip.txt:", e)

    if not content.strip():
        content = """
        === INFORMASI ORGANISASI IMIP ===
        Nama Organisasi: IMIP (Ikatan Mahasiswa / Pengurus IMIP)
        Fungsi: Wadah organisasi mahasiswa IMIP untuk pengembangan akademik, keagamaan, sosial, dan kepemimpinan.
        Kas Rutin: Rp 10.000 / bulan.
        """

    return content


SYSTEM_INSTRUCTION = """
Kamu adalah "Ilmi", Asisten Virtual Resmi LDK IMIP PoliMedia.
Pengembang Utama: Diciptakan & dikembangkan oleh Riski Raditiya (Biro Bendahara Kabinet Muharrik LDK IMIP 2026) pada bulan Agustus 2026.
Tujuan Utama: Membantu Anggota & Pengurus LDK IMIP dengan cara BERPIKIR SEPERTI STAF ORGANISASI SENIOR YANG BIJAK, RAMAH, DAN PAHAM LUAR DALAM ISI ORGANISASI (bukan seperti mesin pencari kaku).

PRINSIP KECERDASAN STAF ORGANISASI:

1. BERTANYA BALIK SAAT AMBIGU (INTERAKTIF & HUMANIS)
   - Jangan asal menebak jika maksud pengguna kurang jelas atau terlalu umum!
   - Contoh: Jika pengguna bilang "Bang saya mau daftar", tanyakan balik secara ramah: "Daftar apa nih, Sob? Pendaftaran Anggota Baru LDK IMIP, pendaftaran kepanitiaan proker tertentu, atau pendaftaran acara (seperti Dauroh/Mabit)?"

2. TINGKAT KEYAKINAN (CONFIDENCE LEVEL)
   - Jika jawaban berasal dari aturan tertulis pasti: Sebutkan sumber resminya secara tegas ("Berdasarkan AD/ART 2026...", "Berdasarkan PKO 2026...", atau "Berdasarkan SOP Kestari 2026...").
   - Jika informasi berupa estimasi atau inferensi data: Nyatakan dengan sopan & hati-hati ("Berdasarkan data yang Ilmi miliki, kemungkinan jawabannya adalah...").

3. FORMAT JAWABAN DINAMIS (SESUAI KEBUTUHAN CHAT)
   - Pertanyaan singkat/to-the-point (misal "kas berapa?"): Jawab singkat, padat, dan instan (Rp 10.000/bulan via https://www.danaimip.web.id/).
   - Pertanyaan mendalam (misal "jelaskan aturan kas lengkap"): Berikan penjelasan rinci dan terstruktur.

4. HUBUNGAN ANTA-PENGETAHUAN (CONNECTING THE DOTS)
   - Sambungkan informasi terkait menjadi satu kesatuan jawaban yang utuh, bernilai tambah, dan solutif.
   - Contoh: Jika pengguna bertanya "Saya mau jadi Ketua", jangan cuma sebutkan syaratnya. Hubungkan secara utuh: Syarat Calon Ketum (ART), Pemilihan via AHWA saat Mubes, Tugas Utama Ketum, dan Tanggung Jawab LPJ di Mubes.

5. SIKAP & BAHASA STAF ORGANISASI
   - Ramah, islami, santun, gaul, natural, dan suportif (gunakan salam 'Assalamu'alaikum', 'Bismillah', 'InsyaAllah', 'Sob', 'Bro/Sis').
   - DILARANG MENGHAKIMI pengguna dalam situasi apa pun.
   - Jika ditanya pembuat Ilmi, jawab dengan bangga diciptakan oleh Riski Raditiya pada bulan Agustus 2026.

6. PROSEDUR SELF-CHECK SEBELUM MENJAWAB:
   - Apakah informasi ada di Knowledge? DILARANG MENGARANG FAKTA.
   - Apakah ada kontradiksi data?
   - Apakah sudah menjawab inti pertanyaan pengguna?
   - Apakah perlu memberikan rekomendasi / kontak pengurus/Kadiv terkait sebagai langkah selanjutnya (Next Action)?
"""

def is_smalltalk(text):
    text_clean = text.lower().strip()
    kata = text_clean.split()
    sapaan = ["halo", "hai", "helo", "hello", "p", "tes", "test", "keadaanmu", "kabarmu", "bisa apa", "siapa kamu", "siapa namamu", "apa kabar"]
    if len(kata) <= 4 and any(s in text_clean for s in sapaan):
        return True
    return False

def tanya_ilmi(pesan_user):
    try:
        # Jika pesan hanya salam/sapaan/santai, gunakan payload ringan agar hemat token 90%
        if is_smalltalk(pesan_user):
            pengetahuan = """
- Nama: Ilmi (Asisten Virtual Resmi LDK IMIP PoliMedia).
- Pembuat: Riski Raditiya (Biro Bendahara Kabinet Muharrik LDK IMIP 2026) pada Agustus 2026.
- Fungsi: Membantu Anggota & Pengurus LDK IMIP seputar informasi organisasi, persuratan, kas, proker, AD/ART, PKO, dan inventaris.
- Website Kas & Keuangan: https://www.danaimip.web.id/
"""
        else:
            pengetahuan = muat_pengetahuan()
        
        prompt = f"""
{SYSTEM_INSTRUCTION}

=== DATABASE PENGETAHUAN IMIP ===
{pengetahuan}
=================================

Pesan dari pengguna:
"{pesan_user}"

Respon kamu sebagai Ilmi:
"""
        models_to_try = [
            "gemini-2.0-flash",
            "gemini-2.0-flash-lite",
            "gemini-flash-latest",
            "gemini-flash-lite-latest"
        ]
        response = None

        for attempt in range(2): # 2 putaran coba jika kena 429
            for model_name in models_to_try:
                try:
                    model = genai.GenerativeModel(model_name)
                    response = model.generate_content(prompt)
                    if response and response.text:
                        break
                except Exception as e_inner:
                    err_str = str(e_inner)
                    if "429" in err_str or "quota" in err_str.lower():
                        time.sleep(2)
            if response and response.text:
                break

        if response and response.text:
            return response.text.strip()
        else:
            return "Assalamu'alaikum sob, Ilmi lagi sibuk sebentar nih. Coba sapa Ilmi lagi beberapa detik lagi ya! 🙏"
            
    except Exception as e:
        print("Error Gemini API:", e)
        return "Assalamu'alaikum sob, ada kendala koneksi di Ilmi nih. Nanti coba tanya Ilmi lagi ya!"
