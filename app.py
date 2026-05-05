import os
import requests
from flask import Flask, request, jsonify, send_from_directory
from aspose.slides import Presentation, SaveFormat
import uuid
import time

app = Flask(__name__)

# Geçici dosyalar için klasör
UPLOAD_FOLDER = "static"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route("/merge", methods=["POST"])
def merge_pptx():
    temp_files = []
    main_pres = None
    
    try:
        # 1. DOSYALARI YAKALAMA (En sağlam yöntem)
        files = []
        for key in request.files:
            files.extend(request.files.getlist(key))
        
        # Log: Gelen dosya sayısını kontrol et
        print(f"DEBUG: Gelen dosya sayısı: {len(files)}")

        if len(files) < 2:
            return jsonify({
                "error": f"En az 2 dosya gerekli. Sunucuya ulaşan dosya sayısı: {len(files)}",
                "debug_info": "Eğer 0 ise Query Record sonucunu kontrol edin."
            }), 400

        # 2. DOSYALARI KAYDETME
        for file in files:
            if file.filename == '': continue
            path = os.path.join(UPLOAD_FOLDER, f"{uuid.uuid4()}_{file.filename}")
            file.save(path)
            temp_files.append(path)

        # 3. BİRLEŞTİRME İŞLEMİ
        main_pres = Presentation(temp_files[0])
        
        for i in range(1, len(temp_files)):
            with Presentation(temp_files[i]) as sub_pres:
                for slide in sub_pres.slides:
                    main_pres.slides.add_clone(slide)

        # 4. KAYDETME
        output_name = f"sunum_{int(time.time())}.pptx"
        output_path = os.path.join(UPLOAD_FOLDER, output_name)
        main_pres.save(output_path, SaveFormat.PPTX)

        # Temiz bir URL oluştur (Render URL'sine göre)
        # request.host_url otomatik olarak https://uygulama-adi.onrender.com/ verir
        download_url = f"{request.host_url.rstrip('/')}/static/{output_name}"

        return jsonify({
            "message": "Başarılı",
            "indir": download_url,
            "dosya_sayisi": len(temp_files)
        }), 200

    except Exception as e:
        print(f"HATA: {str(e)}")
        return jsonify({"error": f"Sunucu hatası: {str(e)}"}), 500

    finally:
        # Bellek Temizliği (Dispose çok önemli!)
        if main_pres:
            main_pres.dispose()
        # Geçici indirilen dosyaları sil (Output hariç)
        for f in temp_files:
            if os.path.exists(f):
                os.remove(f)

@app.route('/static/<path:filename>')
def download_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
