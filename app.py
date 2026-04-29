import os
import io
import requests
import uuid
from flask import Flask, request, jsonify, send_from_directory
from pptx import Presentation

app = Flask(__name__)

# Dosyaların geçici olarak tutulacağı klasör
UPLOAD_FOLDER = 'merged_files'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def copy_slides(src_pres, dest_pres):
    """Eski sistemdeki slayt kopyalama mantığını koruyoruz."""
    for slide in src_pres.slides:
        slide_layout = dest_pres.slide_layouts[0] # Basitlik için ilk layout seçildi
        new_slide = dest_pres.slides.add_slide(slide_layout)
        for shape in slide.shapes:
            if shape.has_text_frame:
                new_shape = new_slide.shapes.add_textbox(shape.left, shape.top, shape.width, shape.height)
                new_shape.text = shape.text
            # Resim kopyalama vb. özellikler buraya eklenebilir

@app.route('/merge', methods=['POST'])
def merge_pptx():
    try:
        data = request.get_json()
        urls = data.get('urls', [])

        if not urls:
            return jsonify({"error": "Dosya listesi gelmedi"}), 400

        # Birleştirme işlemini başlat
        merged_pres = Presentation()
        # Boş başlatılan sunumun ilk slaytını temizle
        xml_slides = merged_pres.slides._slim_elements
        if len(xml_slides) > 0:
            del xml_slides[0]

        for url in urls:
            resp = requests.get(url)
            if resp.status_code == 200:
                current_pres = Presentation(io.BytesIO(resp.content))
                copy_slides(current_pres, merged_pres)

        # Benzersiz bir dosya adı oluştur
        file_name = f"merged_{uuid.uuid4().hex}.pptx"
        file_path = os.path.join(UPLOAD_FOLDER, file_name)
        merged_pres.save(file_path)

        # NocoBase'in bu dosyayı indirebilmesi için Render URL'ini dönüyoruz
        # Render linkini (https://projeniz.onrender.com) çevre değişkeninden al veya manuel yaz
        base_url = request.host_url.rstrip('/') 
        output_url = f"{base_url}/download/{file_name}"

        return jsonify({"output_url": output_url}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
