from flask import Flask, request, jsonify
import fitz  # PyMuPDF
from gensim.summarization import summarize
import os

app = Flask(__name__)

def summarize_pdf(pdf_path):
    pdf_document = fitz.open(pdf_path)
    full_text = ""
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        full_text += page.get_text() + "\n"
    pdf_document.close()
    
    # Ensure there is enough content for summarization
    if len(full_text.split()) < 50:  # Gensim may need more content to generate a summary
        return "Not enough content for summarization."

    summary = summarize(full_text, ratio=0.1)  # Adjust ratio for desired summary length
    return summary if summary else "Summary could not be generated."

@app.route('/summarize', methods=['POST'])
def upload_and_summarize():
    if 'pdf' not in request.files:
        return jsonify({"error": "No PDF file uploaded."}), 400

    file = request.files['pdf']
    if file.filename == '':
        return jsonify({"error": "Empty filename provided."}), 400

    # Create a temporary file path to save the PDF
    temp_dir = '/tmp'  # For Azure, use os.environ.get('TEMP', '/tmp') if unsure
    pdf_path = os.path.join(temp_dir, file.filename)
    file.save(pdf_path)

    try:
        summary_text = summarize_pdf(pdf_path)
        return jsonify({"summary": summary_text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        # Remove the temporary file to avoid clutter
        if os.path.exists(pdf_path):
            os.remove(pdf_path)

if __name__ == "__main__":
    # Use '0.0.0.0' to ensure the app runs on the server's IP
    app.run(host='0.0.0.0', port=8080, debug=True)
