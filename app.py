import os, requests, uuid, time
from flask import Flask, request, jsonify, send_from_directory
import aspose.slides as slides  # Import şeklini değiştirdik

app = Flask(__name__)
UPLOAD_FOLDER = "static"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route("/merge", methods=["POST"])
def merge_pptx():
    temp_files = []
    main_pres = None
    try:
        data = request.json 
        urls = []

        if isinstance(data, list):
            for record in data:
                sunumlar = record.get('sunumlar', [])
                if isinstance(sunumlar, list):
                    for s in sunumlar:
                        if isinstance(s, dict) and s.get('url'):
                            urls.append(s['url'])
        
        if len(urls) < 2:
            return jsonify({"error": f"En az 2 dosya lazım. Sistem {len(urls)} dosya bulabildi."}), 400

        for url in urls:
            r = requests.get(url.strip())
            if r.status_code == 200:
                p = os.path.join(UPLOAD_FOLDER, f"{uuid.uuid4()}.pptx")
                with open(p, 'wb') as f:
                    f.write(r.content)
                temp_files.append(p)

        # Birleştirme işlemi - Yeni kütüphane formatına göre düzenlendi
        main_pres = slides.Presentation(temp_files[0])
        for i in range(1, len(temp_files)):
            with slides.Presentation(temp_files[i]) as sub:
                for slide in sub.slides:
                    main_pres.slides.add_clone(slide)

        out_name = f"sunum_{int(time.time())}.pptx"
        out_path = os.path.join(UPLOAD_FOLDER, out_name)
        # SaveFormat'ı slides modülü üzerinden çağırdık
        main_pres.save(out_path, slides.export.SaveFormat.PPTX)

        return jsonify({
            "message": "Başarılı",
            "indir": f"{request.host_url.rstrip('/')}/static/{out_name}"
        }), 200

    except Exception as e:
        return jsonify({"error": f"Sunucu hatası: {str(e)}"}), 500
    finally:
        if main_pres:
            main_pres.dispose()
        for f in temp_files:
            if os.path.exists(f):
                os.remove(f)

@app.route('/static/<path:filename>')
def download(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
