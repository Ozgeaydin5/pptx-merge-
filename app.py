import os
import time
import gc
import requests
import io
from flask import Flask, request, jsonify, send_from_directory
import aspose.slides as slides

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
os.makedirs(STATIC_DIR, exist_ok=True)

@app.route("/")
def home():
    return "Aspose PPTX Merger Online!"

@app.route("/merge", methods=["POST"])
def merge_pptx():
    main_pres = None
    try:
        # NocoBase'den gelen JSON verisini alıyoruz
        data = request.get_json()
        urls = data.get('urls', [])

        if not urls or len(urls) < 1:
            return jsonify({"error": "Birleştirilecek dosya bulunamadı"}), 400

        # 1. İLK DOSYAYI İNDİR VE ANA SUNUMU OLUŞTUR
        first_resp = requests.get(urls[0])
        if first_resp.status_code != 200:
            return jsonify({"error": "İlk dosya indirilemedi"}), 400
        
        # Bellek üzerinden Aspose Presentation objesini oluştur
        first_stream = io.BytesIO(first_resp.content)
        main_pres = slides.Presentation(first_stream)

        # 2. DİĞER TÜM URL'LERİ DÖNGÜYLE EKLE
        for url in urls[1:]:
            resp = requests.get(url)
            if resp.status_code == 200:
                with slides.Presentation(io.BytesIO(resp.content)) as src_pres:
                    for slide in src_pres.slides:
                        # Aspose'un meşhur add_clone metodu (Bozulma yapmaz)
                        main_pres.slides.add_clone(slide)
            else:
                print(f"Uyarı: {url} indirilemedi, atlanıyor.")

        # 3. KAYDETME
        output_name = f"birlesmis_hafta_{int(time.time())}.pptx"
        save_path = os.path.join(STATIC_DIR, output_name)
        main_pres.save(save_path, slides.export.SaveFormat.PPTX)

        # NocoBase'in 'Update Record' düğümü için linki döndür
        return jsonify({
            "status": "success",
            "output_url": f"https://{request.host}/static/{output_name}"
        }), 200

    except Exception as e:
        print(f"Hata olustu: {str(e)}")
        return jsonify({"error": str(e)}), 500
    finally:
        # Bellek temizliği (GC ve silme)
        if main_pres:
            del main_pres
        gc.collect()

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory(STATIC_DIR, path)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
