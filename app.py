from flask import Flask, request, jsonify
import fitz  # PyMuPDF
import re
import io
from openai import AzureOpenAI

import requests




app = Flask(__name__)

# Azure OpenAI Configuration
endpoint = "https://hipo-ai.openai.azure.com/"
deployment = "gpt-4"
api_key = "1Uty3zR2yIuFmz75r9nDwkAh3mLbNbWZu4XlFDn6AjBoP9foaAE0JQQJ99AJACYeBjFXJ3w3AAAAACOGOqBp"

client = AzureOpenAI(
    azure_endpoint=endpoint,
    api_key=api_key,
    api_version="2024-05-01-preview"
)



# Function to find summary paragraphs in a PDF
def find_summary_paragraph(pdf_file_stream):
    # Open the provided PDF file from the in-memory stream
    pdf_document = fitz.open(stream=pdf_file_stream, filetype="pdf")
    
    summary_paragraphs = []
    
    # Iterate through pages
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        text = page.get_text("text")
        
        # Split text into paragraphs
        paragraphs = text.split('\n\n')
        
        # Check each paragraph for summary keywords
        summary_keywords = ["summary", "conclusion", "abstract", "concluding remarks"]
        for para in paragraphs:
            if any(keyword in para.lower() for keyword in summary_keywords):
                # Extract the sentences around the paragraph containing the keyword
                relevant_data = extract_surrounding_sentences(text, para)
                summary_paragraphs.append(relevant_data)
    
    # Close the PDF document
    pdf_document.close()
    
    # Return all valid data found
    return summary_paragraphs




# # Function to extract surrounding sentences
# def extract_surrounding_sentences(text, paragraph):
#     # Split the full text into sentences using regex for proper sentence-ending punctuation
#     sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', text)
    
#     # Find the index of the paragraph in the text
#     para_start_idx = text.find(paragraph)
#     para_end_idx = para_start_idx + len(paragraph)
    
#     # Find the surrounding sentences by checking the index
#     relevant_sentences = []
#     for sentence in sentences:
#         if para_start_idx <= text.find(sentence) <= para_end_idx:
#             if is_valid_sentence(sentence):  # Check if the sentence is valid
#                 relevant_sentences.append(sentence.strip())
    
#     # Add nearby sentences (before and after) for more context
#     surrounding_data = []
#     for i, sentence in enumerate(sentences):
#         # Include sentences that are relevant to the paragraph and longer than 2 words
#         if text.find(paragraph) <= text.find(sentence) <= text.find(paragraph) + len(paragraph):
#             if is_valid_sentence(sentence):  # Check if the sentence is valid
#                 surrounding_data.append(sentence.strip())
            
#             # Add previous sentence if valid
#             if i > 0 and is_valid_sentence(sentences[i - 1]):
#                 surrounding_data.insert(0, sentences[i - 1].strip())  
            
#             # Add next sentence if valid
#             if i + 1 < len(sentences) and is_valid_sentence(sentences[i + 1]):
#                 surrounding_data.append(sentences[i + 1].strip())  
    
#     # Clean the sentences by removing numbers and non-alphabetic characters
#     clean_data = clean_text(" ".join(surrounding_data))
    
#     return clean_data

# # Helper function to determine if a sentence is valid
# def is_valid_sentence(sentence):
#     words = sentence.split()
    
#     # Remove unwanted single words or fragments
#     if len(words) <= 2 or not any(word.isalpha() for word in words):  # Avoid fragments
#         return False
#     return True

# # Clean the extracted text by removing all numbers, decimal points, and non-alphabetic characters
# def clean_text(text):
#     cleaned_text = re.sub(r'[^a-zA-Z\s]', '', text)
#     cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
#     return cleaned_text


# Function to extract surrounding sentences
def extract_surrounding_sentences(text, paragraph):
    # Split the full text into sentences using regex for proper sentence-ending punctuation
    sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)\s(?=\.|\?)\s', text)
    
    # Find the index of the paragraph in the text
    para_start_idx = text.find(paragraph)
    para_end_idx = para_start_idx + len(paragraph)
    
    # Find the surrounding sentences by checking the index
    relevant_sentences = []
    for sentence in sentences:
        if para_start_idx <= text.find(sentence) <= para_end_idx:
            if is_valid_sentence(sentence):  # Check if the sentence is valid
                relevant_sentences.append(sentence.strip())
    
    # Add nearby sentences (before and after) for more context
    surrounding_data = []
    for i, sentence in enumerate(sentences):
        # Include sentences that are relevant to the paragraph and longer than 2 words
        if text.find(paragraph) <= text.find(sentence) <= text.find(paragraph) + len(paragraph):
            if is_valid_sentence(sentence):  # Check if the sentence is valid
                surrounding_data.append(sentence.strip())
            
            # Add previous sentence if valid
            if i > 0 and is_valid_sentence(sentences[i - 1]):
                surrounding_data.insert(0, sentences[i - 1].strip())  
            
            # Add next sentence if valid
            if i + 1 < len(sentences) and is_valid_sentence(sentences[i + 1]):
                surrounding_data.append(sentences[i + 1].strip())  
    
    # Clean the sentences by removing numbers and non-alphabetic characters
    clean_data = clean_text(" ".join(surrounding_data))
    
    # Remove any two-letter words
    clean_data = ' '.join([word for word in clean_data.split() if len(word) > 2])

    return clean_data

# Helper function to determine if a sentence is valid
def is_valid_sentence(sentence):
    words = sentence.split()
    
    # Remove unwanted single words or fragments
    if len(words) <= 2 or not any(word.isalpha() for word in words):  # Avoid fragments
        return False
    return True

# Clean the extracted text by removing all numbers, decimal points, and non-alphabetic characters
def clean_text(text):
    cleaned_text = re.sub(r'[^a-zA-Z\s]', '', text)
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
    return cleaned_text






def chunk_text(text, max_tokens=500):
    """Split text into chunks of approximately `max_tokens`."""
    words = text.split()
    chunks = []
    current_chunk = []
    current_length = 0

    for word in words:
        word_length = len(word)  # Approximation of token length
        if current_length + word_length + 1 > max_tokens:  # +1 for space or separator
            chunks.append(' '.join(current_chunk))
            current_chunk = []
            current_length = 0
        current_chunk.append(word)
        current_length += word_length + 1

    if current_chunk:
        chunks.append(' '.join(current_chunk))

    return chunks




# Function to analyze the summary and extract competencies
def analyze_paragraph(paragraph):
    prompt_template = """
    Analyze the following paragraph and identify which of these competencies/skills are mentioned or implied. 
    For each identified competency, indicate if it's discussed positively or negatively.
    Only include competencies that are clearly referenced or implied - do not force matches.
    
    Paragraph: {paragraph}
    
    Format your response exactly like this, including ONLY the competencies that are actually mentioned or implied:
    Competency: Sentiment

    For example:
    Analytical Thinking: negative
    Leadership Orientation: positive

    """

    keywords = [
        "Leadership Orientation", "Persuasive Communication", "Result Orientation", "Change Champion", 
        "Innovation mindset", "Customer Focus", "Team Management", "Coaching Orientation", 
        "Delegating", "Data driven problem solving", "Talent Champion", "Direction", "Conflict Management", 
        "Negotiation skills", "Active Listening", "Impactful communication", "Emotional Intelligence", 
        "Synergy driven", "Inter-personal networking", "Collaboration mindset", "Political Acumen", 
        "Global mindset", "Decision Making", "Decisiveness", "Strategic Thinking", "Organisation Stewardship", 
        "Learning Orientation", "Creative Problem-Solving", "Analytical Thinking", "Growth Mindset", 
        "Business Acumen", "Continuous Improvement Mindset", "Process Orientation", "Initiative taking", 
        "Time Management", "Strategic Planning", "System driven", "Resilience", "Energetic", 
        "Assertiveness", "Ambitious", "Self-Awareness", "Self driven", "Accountability", "Professionalism", 
        "Dependability", "Adaptability"
    ]

    results = {}
    chunks = chunk_text(paragraph, max_tokens=500)

    for chunk in chunks:
        prompt = prompt_template.format(paragraph=chunk)
        completion = client.chat.completions.create(
            model=deployment,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
            temperature=0.3,
            top_p=0.95,
            frequency_penalty=0,
            presence_penalty=0,
            stream=False
        )
        
        response = completion.choices[0].message.content.strip()
        for line in response.split('\n'):
            if ':' in line:
                competency, sentiment = line.split(':', 1)
                competency = competency.strip()
                sentiment = sentiment.strip().lower()
                if competency in keywords and sentiment in ['positive', 'negative']:
                    results[competency] = sentiment

    return results



# Route to process summary text for competencies
@app.route('/summary', methods=['POST'])
def summary():
    # Check if the request contains summary text
    if 'summary' not in request.json:
        return jsonify({"error": "No summary text provided"}), 400

    # Extract the summary text from the request
    summary_text = request.json['summary']
    
    try:
        # Process the summary text and get the results
        results = analyze_paragraph(summary_text)

        if results:
            return jsonify( results )
        else:
            return jsonify({"message": "No competencies found."})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

 

@app.route('/extract', methods=['POST'])
def extract():
    # Parse the JSON request to get the URL
    data = request.get_json()
    if not data or 'pdf' not in data:
        return jsonify({"error": "No PDF URL provided"}), 400

    pdf_url = data['pdf']

    try:
        # Fetch the PDF file from the URL
        response = requests.get(pdf_url)
        response.raise_for_status()  # Raise an error if the request was not successful
        
        # Read the content and create a BytesIO stream
        pdf_file_stream = io.BytesIO(response.content)

        # Call your function to process the PDF
        summary_paragraphs = find_summary_paragraph(pdf_file_stream)
        
        if summary_paragraphs:
            return jsonify({"summary_paragraphs": summary_paragraphs})
        else:
            return jsonify({"message": "No summary paragraph found."})

    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Failed to fetch PDF: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

# Route to extract PDF content and send it for summary analysis
@app.route('/callsumarrextract', methods=['POST'])
def callsumarrextract():
    # Parse the JSON request to get the PDF URL
    data = request.get_json()
    if not data or 'pdf' not in data:
        return jsonify({"error": "No PDF URL provided"}), 400

    pdf_url = data['pdf']

    try:
        # Step 1: Fetch the PDF from the URL
        response = requests.get(pdf_url)
        response.raise_for_status()  # Raise an error for unsuccessful requests
        
        # Step 2: Read the content into a BytesIO stream
        pdf_file_stream = io.BytesIO(response.content)

        # Step 3: Extract summary paragraphs from the PDF
        summary_paragraphs = find_summary_paragraph(pdf_file_stream)

        if not summary_paragraphs:
            return jsonify({"message": "No summary paragraph found."})

        # Step 4: Send the extracted summary to the summary processing function
        results = []
        for paragraph in summary_paragraphs:
            processed_result = analyze_paragraph(paragraph)
            if processed_result:
                results.append(processed_result)

        if results:
            return jsonify(results)
        else:
            return jsonify({"message": "No competencies found in the summary."})

    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Failed to fetch PDF: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500




if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
