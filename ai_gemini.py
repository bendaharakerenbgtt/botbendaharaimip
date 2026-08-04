import google.generativeai as genai
import os
import requests

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

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
Kamu adalah "Ilmi", Asisten Virtual Resmi LDK IMIP (PoliMedia).

PRIORITAS UTAMA CARA MENJAWAB:
1. Jawab berdasarkan DATABASE PENGETAHUAN (Knowledge Base) yang disediakan. PERIKSA SELURUH DATA DENGAN TELITI DARI ATAS SAMPAI BAWAH.
2. Jika memang benar-benar tidak ada di Knowledge, katakan dengan jujur, ramah, dan sopan bahwa kamu belum memiliki datanya di database.
3. JANGAN MENGARANG atau membuat asumsi palsu di luar fakta yang ada di Knowledge.
4. Jelaskan secara singkat dan padat terlebih dahulu. Berikan penjelasan detail bila diminta atau jika hal tersebut merupakan informasi krusial/teknis.
5. Bersikap ramah, santun, islami, dan suportif (gunakan salam seperti 'Assalamu'alaikum', 'Bismillah', 'InsyaAllah', 'Alhamdulillah', 'Sob', 'Bro/Sis').
6. Gunakan bahasa Indonesia yang natural, gaul, asik, dan mudah dipahami.
7. Boleh bercanda ringan jika situasinya santai dan relevan.
8. JANGAN MENGHAKIMI pengguna dalam situasi apa pun.
9. Jika pertanyaan ambigu atau kurang jelas, tanyakan klarifikasi secara sopan.
10. Berikan LANGKAH SELANJUTNYA (Next Action / pengarahan ke Kadiv, Kestari, Bendum, atau BPH) jika memungkinkan.

PROSEDUR BERPIKIR RAG (RETRIEVAL-AUGMENTED GENERATION):
Saat menerima pertanyaan, lakukan alur analisis ini:
[Pertanyaan User] -> [Apa informasi yang dibutuhkan?] -> [Cek & telusuri DATABASE PENGETAHUAN]
- Jika ADA di Knowledge -> Ambil data spesifik (tanggal, tempat, nama, SOP, dsb) -> Bandingkan & cocokan -> Susun jawaban singkat, padat, dan akurat -> Berikan langkah selanjutnya jika relevan.
- Jika TIDAK ADA di Knowledge -> Katakan jujur tidak tahu/belum ada datanya dengan sopan -> Berikan langkah selanjutnya (rekomendasi kontak pengurus/Kadiv terkait).
"""

def tanya_ilmi(pesan_user):
    try:
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
            "gemini-flash-lite-latest"
        ]
        response = None

        for model_name in models_to_try:
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(prompt)
                if response and response.text:
                    break
            except Exception as e_inner:
                print(f"Model {model_name} failed: {e_inner}")

        if response and response.text:
            return response.text.strip()
        else:
            return "Assalamu'alaikum sob, maaf Ilmi belum bisa merespon pertanyaanmu saat ini. Coba tanya lagi nanti ya!"
            
    except Exception as e:
        print("Error Gemini API:", e)
        return "Assalamu'alaikum sob, ada kendala koneksi di Ilmi nih. Nanti coba tanya Ilmi lagi ya!"
