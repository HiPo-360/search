from flask import Flask, request, jsonify
import fitz  # PyMuPDF
import os
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

# Initialize Flask app
app = Flask(__name__)

# MongoDB connection setup
uri = "mongodb+srv://hipo:hipo@hipo.ia7ctsa.mongodb.net/?retryWrites=true&w=majority&appName=HiPo"
client = MongoClient(uri, server_api=ServerApi('1'))

# Check connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

# Database and collection
db = client['pdf_extraction']
collection = db['summaries']

# Function to extract summary paragraph from PDF
def find_summary_paragraph(pdf_path, summary_keywords):
    pdf_document = fitz.open(pdf_path)
    summary_paragraph = None
    
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        text = page.get_text()
        
        paragraphs = text.split('\n\n')
        
        for para in paragraphs:
            if any(keyword in para.lower() for keyword in summary_keywords):
                summary_paragraph = para
                break
        if summary_paragraph:
            break
    
    pdf_document.close()
    
    return summary_paragraph

# Define the API endpoint for PDF extraction
@app.route('/extract', methods=['POST'])
def extract():
    if 'pdf' not in request.files:
        return jsonify({"error": "No PDF file provided"}), 400

    pdf_file = request.files['pdf']
    summary_keywords = ["summary", "conclusion", "abstract", "concluding remarks"]

    # Ensure the temporary directory exists
    tmp_dir = "/tmp"
    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir)

    # Save the uploaded PDF to a temporary file
    pdf_path = os.path.join(tmp_dir, pdf_file.filename)
    pdf_file.save(pdf_path)

    # Extract the summary paragraph
    summary_paragraph = find_summary_paragraph(pdf_path, summary_keywords)

    # Remove the temporary file
    os.remove(pdf_path)

    if summary_paragraph:
        # Save the summary paragraph to MongoDB
        result = collection.insert_one({"summary_paragraph": summary_paragraph})
        
        # Return the result including the MongoDB document ID
        return jsonify({
            "summary_paragraph": summary_paragraph,
            "mongo_id": str(result.inserted_id)
        })
    else:
        return jsonify({"error": "No summary paragraph found"}), 404

# Run the Flask app with Waitress
if __name__ == '__main__':
    from waitress import serve
    serve(app, host='0.0.0.0', port=5000)
