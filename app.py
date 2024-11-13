# # # # from flask import Flask, request, jsonify
# # # # import fitz  # PyMuPDF
# # # # import os
# # # # from pymongo.mongo_client import MongoClient
# # # # from pymongo.server_api import ServerApi

# # # # # Initialize Flask app
# # # # app = Flask(__name__)

# # # # # MongoDB connection setup
# # # # uri = "mongodb+srv://hipo:hipo@hipo.ia7ctsa.mongodb.net/?retryWrites=true&w=majority&appName=HiPo"
# # # # client = MongoClient(uri, server_api=ServerApi('1'))

# # # # # Check connection
# # # # try:
# # # #     client.admin.command('ping')
# # # #     print("Pinged your deployment. You successfully connected to MongoDB!")
# # # # except Exception as e:
# # # #     print(e)

# # # # # Database and collection
# # # # db = client['pdf_extraction']
# # # # collection = db['summaries']

# # # # # Function to extract summary paragraph from PDF
# # # # def find_summary_paragraph(pdf_path, summary_keywords):
# # # #     pdf_document = fitz.open(pdf_path)
# # # #     summary_paragraph = None
    
# # # #     for page_num in range(len(pdf_document)):
# # # #         page = pdf_document.load_page(page_num)
# # # #         text = page.get_text()
        
# # # #         paragraphs = text.split('\n\n')
        
# # # #         for para in paragraphs:
# # # #             if any(keyword in para.lower() for keyword in summary_keywords):
# # # #                 summary_paragraph = para
# # # #                 break
# # # #         if summary_paragraph:
# # # #             break
    
# # # #     pdf_document.close()
    
# # # #     return summary_paragraph

# # # # # Define the API endpoint for PDF extraction
# # # # @app.route('/extract', methods=['POST'])
# # # # def extract():
# # # #     if 'pdf' not in request.files:
# # # #         return jsonify({"error": "No PDF file provided"}), 400

# # # #     pdf_file = request.files['pdf']
# # # #     summary_keywords = ["summary", "conclusion", "abstract", "concluding remarks"]

# # # #     # Ensure the temporary directory exists
# # # #     tmp_dir = "/tmp"
# # # #     if not os.path.exists(tmp_dir):
# # # #         os.makedirs(tmp_dir)

# # # #     # Save the uploaded PDF to a temporary file
# # # #     pdf_path = os.path.join(tmp_dir, pdf_file.filename)
# # # #     pdf_file.save(pdf_path)

# # # #     # Extract the summary paragraph
# # # #     summary_paragraph = find_summary_paragraph(pdf_path, summary_keywords)

# # # #     # Remove the temporary file
# # # #     os.remove(pdf_path)

# # # #     if summary_paragraph:
# # # #         # Save the summary paragraph to MongoDB
# # # #         result = collection.insert_one({"summary_paragraph": summary_paragraph})
        
# # # #         # Return the result including the MongoDB document ID
# # # #         return jsonify({
# # # #             "summary_paragraph": summary_paragraph,
# # # #             "mongo_id": str(result.inserted_id)
# # # #         })
# # # #     else:
# # # #         return jsonify({"error": "No summary paragraph found"}), 404
              
# # # # # Run the Flask app with Waitress
# # # # if __name__ == '__main__':
# # # #     from waitress import serve
# # # #     serve(app, host='0.0.0.0', port=5000)

# # # from flask import Flask, request, jsonify
# # # import fitz  # PyMuPDF
# # # import os
# # # from pymongo.mongo_client import MongoClient
# # # from pymongo.server_api import ServerApi
# # # from azure.ai.textanalytics import TextAnalyticsClient, ExtractiveSummaryAction
# # # from azure.core.credentials import AzureKeyCredential

# # # # Initialize Flask app
# # # app = Flask(__name__)

# # # # MongoDB connection setup
# # # uri = "mongodb+srv://hipo:hipo@hipo.ia7ctsa.mongodb.net/?retryWrites=true&w=majority&appName=HiPo"
# # # client = MongoClient(uri, server_api=ServerApi('1'))

# # # # Check connection
# # # try:
# # #     client.admin.command('ping')
# # #     print("Pinged your deployment. You successfully connected to MongoDB!")
# # # except Exception as e:
# # #     print(e)

# # # # Database and collection
# # # db = client['pdf_extraction']
# # # collection = db['summaries']

# # # # Azure Text Analytics setup
# # # key = 'fed5dbd18382414381b07dbd04af5b1d'
# # # endpoint = 'https://hipo.cognitiveservices.azure.com/'

# # # # Authenticate the client using your key and endpoint 
# # # def authenticate_client():
# # #     ta_credential = AzureKeyCredential(key)
# # #     text_analytics_client = TextAnalyticsClient(endpoint=endpoint, credential=ta_credential)
# # #     return text_analytics_client

# # # text_analytics_client = authenticate_client()

# # # def sample_extractive_summarization(client, document):
# # #     poller = client.begin_analyze_actions(
# # #         document,
# # #         actions=[ExtractiveSummaryAction(max_sentence_count=10)],
# # #     )

# # #     document_results = poller.result()
# # #     for result in document_results:
# # #         extract_summary_result = result[0] 
# # #         if extract_summary_result.is_error:
# # #             print(f"...Is an error with code '{extract_summary_result.code}' and message '{extract_summary_result.message}'")
# # #             return None
# # #         else:
# # #             return " ".join([sentence.text for sentence in extract_summary_result.sentences])

# # # # Function to extract relevant sentences from text
# # # def extract_relevant_sentences(text, summary_keywords):
# # #     sentences = text.split('.')
# # #     relevant_sentences = [sentence for sentence in sentences if any(keyword in sentence.lower() for keyword in summary_keywords)]
# # #     return relevant_sentences

# # # # Define the API endpoint for PDF extraction
# # # @app.route('/extract', methods=['POST'])
# # # def extract():
# # #     if 'pdf' not in request.files:
# # #         return jsonify({"error": "No PDF file provided"}), 400

# # #     pdf_file = request.files['pdf']
# # #     summary_keywords = ["summary", "conclusion", "abstract", "concluding remarks"]

# # #     # Ensure the temporary directory exists
# # #     tmp_dir = "/tmp"
# # #     if not os.path.exists(tmp_dir):
# # #         os.makedirs(tmp_dir)

# # #     # Save the uploaded PDF to a temporary file
# # #     pdf_path = os.path.join(tmp_dir, pdf_file.filename)
# # #     pdf_file.save(pdf_path)

# # #     # Extract text from the PDF
# # #     pdf_document = fitz.open(pdf_path)
# # #     pdf_text = ""
# # #     for page_num in range(len(pdf_document)):
# # #         page = pdf_document.load_page(page_num)
# # #         pdf_text += page.get_text()
# # #     pdf_document.close()

# # #     # Remove the temporary file
# # #     os.remove(pdf_path)

# # #     # Extract relevant sentences
# # #     relevant_sentences = extract_relevant_sentences(pdf_text, summary_keywords)
# # #     if relevant_sentences:
# # #         # Summarize the relevant sentences using Azure Text Analytics
# # #         summarized_text = sample_extractive_summarization(text_analytics_client, [" ".join(relevant_sentences)])
# # #         if not summarized_text:
# # #             return jsonify({"error": "Failed to generate summary"}), 500

# # #         # Save the summary paragraph to MongoDB
# # #         result = collection.insert_one({
# # #             "summary_paragraph": " ".join(relevant_sentences),
# # #             "summarized_text": summarized_text
# # #         })
        
# # #         # Return the result including the MongoDB document ID
# # #         return jsonify({
# # #             "summary_paragraph": " ".join(relevant_sentences),
# # #             "summarized_text": summarized_text,
# # #             "mongo_id": str(result.inserted_id)
# # #         })
# # #     else:
# # #         return jsonify({"error": "No relevant sentences found"}), 404

# # # # Run the Flask app with Waitress
# # # if __name__ == '__main__':
# # #     from waitress import serve
# # #     serve(app, host='0.0.0.0', port=5000)


# # from flask import Flask, request, jsonify
# # import fitz  # PyMuPDF
# # import os
# # from pymongo.mongo_client import MongoClient
# # from pymongo.server_api import ServerApi
# # from azure.ai.textanalytics import TextAnalyticsClient, ExtractiveSummaryAction
# # from azure.core.credentials import AzureKeyCredential

# # # Initialize Flask app
# # app = Flask(__name__)

# # # MongoDB connection setup
# # uri = "mongodb+srv://hipo:hipo@hipo.ia7ctsa.mongodb.net/?retryWrites=true&w=majority&appName=HiPo"
# # client = MongoClient(uri, server_api=ServerApi('1'))

# # # Check connection
# # try:
# #     client.admin.command('ping')
# #     print("Pinged your deployment. You successfully connected to MongoDB!")
# # except Exception as e:
# #     print(e)

# # # Database and collection
# # db = client['pdf_extraction']
# # collection = db['summaries']

# # # Azure Text Analytics setup
# # key = 'fed5dbd18382414381b07dbd04af5b1d'
# # endpoint = 'https://hipo.cognitiveservices.azure.com/'

# # # Authenticate the client using your key and endpoint 
# # def authenticate_client():
# #     ta_credential = AzureKeyCredential(key)
# #     text_analytics_client = TextAnalyticsClient(endpoint=endpoint, credential=ta_credential)
# #     return text_analytics_client

# # text_analytics_client = authenticate_client()

# # def sample_extractive_summarization(client, document, max_sentences):
# #     poller = client.begin_analyze_actions(
# #         document,
# #         actions=[ExtractiveSummaryAction(max_sentence_count=max_sentences)],
# #     )

# #     document_results = poller.result()
# #     for result in document_results:
# #         extract_summary_result = result[0] 
# #         if extract_summary_result.is_error:
# #             error_message = f"Error code: {extract_summary_result.code}, Message: {extract_summary_result.message}"
# #             print(error_message)
# #             return None
# #         else:
# #             return " ".join([sentence.text for sentence in extract_summary_result.sentences])

# # # Function to extract summary paragraph from PDF
# # def find_summary_paragraph(pdf_path, summary_keywords):
# #     pdf_document = fitz.open(pdf_path)
# #     summary_paragraph = None
    
# #     for page_num in range(len(pdf_document)):
# #         page = pdf_document.load_page(page_num)
# #         text = page.get_text()
        
# #         paragraphs = text.split('\n\n')
        
# #         for para in paragraphs:
# #             if any(keyword in para.lower() for keyword in summary_keywords):
# #                 summary_paragraph = para
# #                 break
# #         if summary_paragraph:
# #             break
    
# #     pdf_document.close()
    
# #     return summary_paragraph

# # # Define the API endpoint for PDF extraction
# # @app.route('/extract', methods=['POST'])
# # def extract():
# #     if 'pdf' not in request.files:
# #         return jsonify({"error": "No PDF file provided"}), 400

# #     pdf_file = request.files['pdf']
# #     summary_keywords = ["summary", "conclusion", "abstract", "concluding remarks"]

# #     # Ensure the temporary directory exists
# #     tmp_dir = "/tmp"
# #     if not os.path.exists(tmp_dir):
# #         os.makedirs(tmp_dir)

# #     # Save the uploaded PDF to a temporary file
# #     pdf_path = os.path.join(tmp_dir, pdf_file.filename)
# #     pdf_file.save(pdf_path)

# #     # Extract the summary paragraph
# #     summary_paragraph = find_summary_paragraph(pdf_path, summary_keywords)

# #     # Remove the temporary file
# #     os.remove(pdf_path)

# #     if summary_paragraph:
# #         # Get the desired number of sentences for the summary
# #         max_sentences = 20
        
# #         # Summarize the relevant sentences using Azure Text Analytics
# #         summarized_text = sample_extractive_summarization(text_analytics_client, [summary_paragraph], max_sentences)
# #         if not summarized_text:
# #             summarized_text = summary_paragraph

# #         # Save the summary paragraph to MongoDB
# #         result = collection.insert_one({
# #             "summary_paragraph": summary_paragraph,
# #             "summarized_text": summarized_text
# #         })
        
# #         # Return the result including the MongoDB document ID
# #         return jsonify({
# #             "summary_paragraph": summary_paragraph,
# #             "summarized_text": summarized_text,
# #             "mongo_id": str(result.inserted_id)
# #         })
# #     else:
# #         return jsonify({"error": "No summary paragraph found"}), 404

# # # Run the Flask app with Waitress
# # if __name__ == '__main__':
# #     from waitress import serve
# #     serve(app, host='0.0.0.0', port=5000)


# from flask import Flask, request, jsonify
# import fitz  # PyMuPDF
# import os
# from pymongo.mongo_client import MongoClient
# from pymongo.server_api import ServerApi
# from azure.ai.textanalytics import TextAnalyticsClient, ExtractiveSummaryAction
# from azure.core.credentials import AzureKeyCredential

# # Initialize Flask app
# app = Flask(__name__)

# # MongoDB connection setup
# uri = "mongodb+srv://hipo:hipo@hipo.ia7ctsa.mongodb.net/?retryWrites=true&w=majority&appName=HiPo"
# client = MongoClient(uri, server_api=ServerApi('1'))

# # Check connection
# try:
#     client.admin.command('ping')
#     print("Pinged your deployment. You successfully connected to MongoDB!")
# except Exception as e:
#     print(e)

# # Database and collection
# db = client['pdf_extraction']
# collection = db['summaries']

# # Azure Text Analytics setup
# key = 'fed5dbd18382414381b07dbd04af5b1d'
# endpoint = 'https://hipo.cognitiveservices.azure.com/'

# # Authenticate the client using your key and endpoint 
# def authenticate_client():
#     ta_credential = AzureKeyCredential(key)
#     text_analytics_client = TextAnalyticsClient(endpoint=endpoint, credential=ta_credential)
#     return text_analytics_client

# text_analytics_client = authenticate_client()

# def sample_extractive_summarization(client, document, max_sentences):
#     poller = client.begin_analyze_actions(
#         document,
#         actions=[ExtractiveSummaryAction(max_sentence_count=max_sentences)],
#     )

#     document_results = poller.result()
#     for result in document_results:
#         extract_summary_result = result[0] 
#         if extract_summary_result.is_error:
#             error_message = f"Error code: {extract_summary_result.code}, Message: {extract_summary_result.message}"
#             print(error_message)
#             return None
#         else:
#             return " ".join([sentence.text for sentence in extract_summary_result.sentences])

# # Function to extract summary paragraph from PDF
# def find_summary_paragraph(pdf_path, summary_keywords):
#     pdf_document = fitz.open(pdf_path)
#     summary_paragraph = None
#     first_paragraph = None
    
#     paragraphs_collected = []
    
#     for page_num in range(len(pdf_document)):
#         page = pdf_document.load_page(page_num)
#         text = page.get_text()
        
#         paragraphs = text.split('\n\n')
        
#         if first_paragraph is None and paragraphs:
#             first_paragraph = paragraphs[0]
        
#         for para in paragraphs:
#             if any(keyword in para.lower() for keyword in summary_keywords):
#                 paragraphs_collected.append(para)
    
#     pdf_document.close()
    
#     if paragraphs_collected:
#         summary_paragraph = " ".join(paragraphs_collected)
#     elif first_paragraph:
#         summary_paragraph = first_paragraph
    
#     return summary_paragraph

# # Define the API endpoint for PDF extraction
# @app.route('/extract', methods=['POST'])
# def extract():
#     if 'pdf' not in request.files:
#         return jsonify({"error": "No PDF file provided"}), 400

#     pdf_file = request.files['pdf']
#     summary_keywords = ["summary", "conclusion", "abstract", "concluding remarks"]

#     # Ensure the temporary directory exists
#     tmp_dir = "/tmp"
#     if not os.path.exists(tmp_dir):
#         os.makedirs(tmp_dir)

#     # Save the uploaded PDF to a temporary file
#     pdf_path = os.path.join(tmp_dir, pdf_file.filename)
#     pdf_file.save(pdf_path)

#     # Extract the summary paragraph
#     summary_paragraph = find_summary_paragraph(pdf_path, summary_keywords)

#     # Remove the temporary file
#     os.remove(pdf_path)

#     if summary_paragraph:
#         # Get the desired number of sentences for the summary
#         max_sentences = 20
        
#         # Summarize the relevant sentences using Azure Text Analytics
#         summarized_text = sample_extractive_summarization(text_analytics_client, [summary_paragraph], max_sentences)
#         if not summarized_text:
#             summarized_text = summary_paragraph

#         # Save the summary paragraph to MongoDB
#         result = collection.insert_one({
#             "summary_paragraph": summary_paragraph,
#             "summarized_text": summarized_text
#         })
        
#         # Return the result including the MongoDB document ID
#         return jsonify({
#             "summary_paragraph": summary_paragraph,
#             "summarized_text": summarized_text,
#             "mongo_id": str(result.inserted_id)
#         })
#     else:
#         return jsonify({"error": "No summary paragraph found"}), 404

# # Run the Flask app with Waitress
# if __name__ == '__main__':
#     from waitress import serve
#     serve(app, host='0.0.0.0', port=5000)

from flask import Flask, request, jsonify
from gensim.summarization import summarize
import fitz  # PyMuPDF

app = Flask(__name__)

def summarize_pdf(pdf_path):
    # Extract text from the PDF
    pdf_document = fitz.open(pdf_path)
    full_text = ""
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        full_text += page.get_text() + "\n"
    pdf_document.close()

    # Summarize using gensim
    summary = summarize(full_text, ratio=0.1)  # Adjust ratio for desired summary length
    return summary

@app.route('/extract', methods=['POST'])
def extract():
    # Check if a PDF file is in the request
    if 'pdf' not in request.files:
        return jsonify({"error": "No PDF file provided"}), 400

    # Save the uploaded file
    pdf_file = request.files['pdf']
    pdf_path = "temp.pdf"
    pdf_file.save(pdf_path)

    # Generate the summary
    try:
        summary_text = summarize_pdf(pdf_path)
    except Exception as e:
        return jsonify({"error": f"Failed to summarize PDF: {str(e)}"}), 500

    # Return the summary as JSON
    return jsonify({"summary": summary_text})

# Run the Flask app with Waitress
if __name__ == '__main__':
    from waitress import serve
    serve(app, host='0.0.0.0', port=5001)
