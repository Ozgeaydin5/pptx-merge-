import os
import time
import gc
from flask import Flask, request, jsonify, send_from_directory
import aspose.slides as slides

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
PROJECT_DIR = os.path.join(BASE_DIR, "project")

os.makedirs(STATIC_DIR, exist_ok=True)
os.makedirs(PROJECT_DIR, exist_ok=True)

@app.route("/")
def home():
    return "API Online ve Calisiyor!"

@app.route("/merge", methods=["POST"])
def merge_pptx():
    main_pres = None
    try:
        files = request.files.getlist("files")
        if not files or len(files) < 2:
            return jsonify({"error": "En az 2 dosya gerekli"}), 400

        first_file = files[0]
        first_path = os.path.join(PROJECT_DIR, first_file.filename)
        first_file.save(first_path)
        
        # Ana sunumu aç
        main_pres = slides.Presentation(first_path)
        
        for f in files[1:]:
            if f.filename:
                temp_path = os.path.join(PROJECT_DIR, f.filename)
                f.save(temp_path)
                
                with slides.Presentation(temp_path) as src_pres:
                    for slide in src_pres.slides:
                        main_pres.slides.add_clone(slide)
                
                if os.path.exists(temp_path):
                    os.remove(temp_path)
        
        output_name = f"sunum_{int(time.time())}.pptx"
        save_path = os.path.join(STATIC_DIR, output_name)
        main_pres.save(save_path, slides.export.SaveFormat.PPTX)

        return jsonify({
            "status": "success",
            "indir": f"https://{request.host}/static/{output_name}"
        }), 200

    except Exception as e:
        print(f"Hata olustu: {str(e)}")
        return jsonify({"error": str(e)}), 500
    finally:
        # Hatalı olan .dispose() yerine nesneyi siliyoruz
        if main_pres:
            del main_pres
        gc.collect() 

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory(STATIC_DIR, path)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
