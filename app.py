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
# Function to analyze the summary and extract competencies
# def analyze_paragraph(paragraph):
#     prompt_template = """
#     Analyze the following paragraph and identify which of these competencies/skills are mentioned or implied. 
#     For each identified competency, indicate if it's discussed positively or negatively.
#     Then, generate a descriptive sentence explaining why the competencies are positive or negative based on the paragraph.
#     If no weaknesses are explicitly mentioned, infer one based on potential areas of improvement.
#     If no strengths are explicitly mentioned, infer one based on any positive aspects present.
    
#     Paragraph: {paragraph}

#     Format your response exactly like this:

#     Positive: (A descriptive sentence explaining the positive competencies and why they are positive based on the paragraph.)
#     Negative: (A descriptive sentence explaining the negative competencies and why they are negative based on the paragraph.)
#     """

#     results = {"positive": "", "negative": ""}
#     chunks = chunk_text(paragraph, max_tokens=500)

#     for chunk in chunks:
#         prompt = prompt_template.format(paragraph=chunk)
#         completion = client.chat.completions.create(
#             model=deployment,
#             messages=[{"role": "user", "content": prompt}],
#             max_tokens=500,
#             temperature=0.3,
#             top_p=0.95,
#             frequency_penalty=0,
#             presence_penalty=0,
#             stream=False
#         )
        
#         response = completion.choices[0].message.content.strip()
#         for line in response.split('\n'):
#             if line.lower().startswith("positive:"):
#                 results["positive"] = line.replace("Positive:", "").strip()
#             elif line.lower().startswith("negative:"):
#                 results["negative"] = line.replace("Negative:", "").strip()

#     # Ensure output always has a positive and a negative competency
#     if not results["positive"]:
#         results["positive"] = "The individual demonstrates a willingness to engage with the topic, showing some level of interest and effort in the discussion."
#     if not results["negative"]:
#         results["negative"] = "While competent in some areas, there is room for improvement in adaptability and flexibility, as a more open approach to different perspectives could enhance effectiveness."

#     return f"Positive: {results['positive']}\nNegative: {results['negative']}"

def analyze_paragraph(paragraph):
    prompt_template = """
    Analyze the following information and identify which of these competencies/skills are mentioned or implied. 
    For each identified competency, indicate if it's discussed positively or negatively.
    Then, generate a descriptive sentence explaining why the competencies are positive or negative based on the information.
    If no weaknesses are explicitly mentioned, infer one based on potential areas of improvement.
    If no strengths are explicitly mentioned, infer one based on any positive aspects present.

   
    {paragraph}

    Format your response exactly like this:

    Positive: (A descriptive sentence explaining the positive competencies and why they are positive based on the user information.)
    Negative: (A descriptive sentence explaining the negative competencies and why they are negative based on the information.)

    """

    results = {"positive": "", "negative": ""}
    chunks = chunk_text(paragraph, max_tokens=500)

    for chunk in chunks:
        prompt = prompt_template + f"\n\n{chunk}"
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
            if line.lower().startswith("positive:"):
                results["positive"] = line.replace("Positive:", "").strip()
            elif line.lower().startswith("negative:"):
                results["negative"] = line.replace("Negative:", "").strip()

    # Ensure output always has a positive and negative insight
    if not results["positive"]:
        results["positive"] = "Demonstrates a strategic mindset, with a focus on achieving impactful results through structured decision-making."
    if not results["negative"]:
        results["negative"] = "Could benefit from a more flexible approach, balancing structure with adaptability to navigate complex challenges."

    return f"Positive: {results['positive']}\nNegative: {results['negative']}"


# Route to process summary text for competencies
@app.route('/summary', methods=['POST'])
def summary():
    if not request.is_json or 'summary' not in request.json:
        return jsonify({"error": "No summary text provided or invalid request format."}), 400

    summary_text = request.json['summary']
    
    if not isinstance(summary_text, str):
        return jsonify({"error": "Invalid format: 'summary' must be a string (paragraph)."}), 400

    try:
        paragraphs = [summary_text] if '\n' not in summary_text else summary_text.split('\n')
        formatted_responses = []

        for paragraph in paragraphs:
            processed_result = analyze_paragraph(paragraph)
            formatted_responses.append(processed_result)

        final_response = "\n".join(formatted_responses)
        print("Final Output: ", final_response)  # Debugging

        return final_response, 200, {'Content-Type': 'text/plain'}

    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Failed to fetch PDF: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500


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
    

@app.route('/callsumarrextract', methods=['POST'])
def callsumarrextract():
    if not request.is_json or 'pdf' not in request.json:
        return jsonify({"error": "No PDF URL provided or invalid request format."}), 400

    pdf_url = request.json['pdf']
    
    try:
        response = requests.get(pdf_url)
        response.raise_for_status()
        pdf_file_stream = io.BytesIO(response.content)
        
        # Extract all summary paragraphs
        summary_paragraphs = find_summary_paragraph(pdf_file_stream)
        
        if not summary_paragraphs:
            return jsonify({"message": "No summary paragraph found."}), 200
        
        # Combine all paragraphs into a single text block
        full_summary = "\n".join(summary_paragraphs)

        # Process the full summary instead of each paragraph separately
        final_response = analyze_paragraph(full_summary)
        
        print("Final Output: ", final_response)  # Debugging
        
        return final_response, 200, {'Content-Type': 'text/plain'}
    
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Failed to fetch PDF: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
