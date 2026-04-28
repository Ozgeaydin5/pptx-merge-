import os
import time
from flask import Flask, request, jsonify, send_from_directory
import aspose.slides as slides

app = Flask(__name__)

# Klasör yolları - Render'ın izin verdiği geçici klasörleri kullanalım
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
PROJECT_DIR = os.path.join(BASE_DIR, "project")

# Gerekli klasörleri otomatik oluştur
os.makedirs(STATIC_DIR, exist_ok=True)
os.makedirs(PROJECT_DIR, exist_ok=True)

@app.route("/")
def home():
    return "PPTX Merger API Render Üzerinde Başarıyla Çalışıyor!"

@app.route("/merge", methods=["POST"])
def merge_pptx():
    try:
        # Form-data üzerinden gelen dosyaları al
        files = request.files.getlist("files")
        if not files or len(files) < 2:
            return jsonify({"error": "Lütfen en az 2 dosya yükleyin"}), 400

        # İlk dosyayı ana sunum (base) olarak belirle ve kaydet
        first_file = files[0]
        first_path = os.path.join(PROJECT_DIR, first_file.filename)
        first_file.save(first_path)
        
        # Aspose ile ana sunumu aç
        with slides.Presentation(first_path) as main_pres:
            for f in files[1:]:
                if f.filename:
                    # Diğer dosyaları geçici olarak kaydet ve aç
                    temp_path = os.path.join(PROJECT_DIR, f.filename)
                    f.save(temp_path)
                    
                    with slides.Presentation(temp_path) as src_pres:
                        # Her slaytı ana sunuma "kaynak biçimlendirmesini koruyarak" ekle
                        for slide in src_pres.slides:
                            main_pres.slides.add_clone(slide)
                    
                    # İşlem bitince geçici dosyayı temizle (Opsiyonel)
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
            
            # Sonuç dosyasını oluştur
            output_name = f"birlesmis_sunum_{int(time.time())}.pptx"
            save_path = os.path.join(STATIC_DIR, output_name)
            
            # PPTX olarak kaydet
            main_pres.save(save_path, slides.export.SaveFormat.PPTX)

        # İndirme linkini döndür
        return jsonify({
            "status": "success",
            "indir": f"https://{request.host}/static/{output_name}"
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Statik dosyaları (indirilecek sunumları) dışarıya aç
@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory(STATIC_DIR, path)

if __name__ == "__main__":
    # Render'ın atadığı portu kullan, yoksa 5000'den aç
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
