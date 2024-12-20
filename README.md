# search

import os
from openai import AzureOpenAI

# Directly provide the endpoint and deployment values
endpoint = "https://hipo-ai.openai.azure.com/"
deployment = "gpt-4"
api_key = "1Uty3zR2yIuFmz75r9nDwkAh3mLbNbWZu4XlFDn6AjBoP9foaAE0JQQJ99AJACYeBjFXJ3w3AAAAACOGOqBp"  # Replace with your actual API key

client = AzureOpenAI(
    azure_endpoint=endpoint,
    api_key=api_key,  # Use the API key for authentication
    api_version="2024-05-01-preview"
)

# List of keywords to match in the paragraph
# List of keywords to match in the paragraph
keywords = [
    "Leadership Orientation",
    "Persuasive Communication",
    "Result Orientation",
    "Change Champion",
    "Innovation mindset",
    "Customer Focus",
    "Team Management",
    "Coaching Orientation",
    "Delegating",
    "Data driven problem solving",
    "Talent Champion",
    "Direction",
    "Conflict Management",
    "Negotiation skills",
    "Active Listening",
    "Impactful communication",
    "Emotional Intelligence",
    "Synergy driven",
    "Inter-personal networking",
    "Collaboration mindset",
    "Political Acumen",
    "Global mindset",
    "Decision Making",
    "Decisiveness",
    "Strategic Thinking",
    "Organisation Stewardship",
    "Learning Orientation",
    "Creative Problem-Solving",
    "Analytical Thinking",
    "Growth Mindset",
    "Business Acumen",
    "Continous Improvement Mindset",
    "Process Orientation",
    "Initiative taking",
    "Time Management",
    "Strategic Planning",
    "System driven",
    "Resilience",
    "Energetic",
    "Assertiveness",
    "Ambitious",
    "Self-Awareness",
    "Self driven",
    "Accountability",
    "Professionalism",
    "Dependability",
    "Adaptability"
]


# Function to split a long paragraph into chunks
def split_paragraph(paragraph, max_length=500):
    sentences = paragraph.split('. ')
    chunks = []
    current_chunk = ""

    for sentence in sentences:
        if len(current_chunk) + len(sentence) <= max_length:
            current_chunk += sentence + ". "
        else:
            chunks.append(current_chunk.strip())
            current_chunk = sentence + ". "
    
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks

# Function to analyze keywords in a paragraph
def analyze_keywords_in_paragraph(keywords, paragraph):
    keyword_sentiments = []

    for keyword in keywords:
        # Construct the prompt for each keyword
        prompt = f"Does the paragraph mention the keyword '{keyword}'? If yes, is the sentiment positive or negative? Respond only with 'positive' or 'negative'. If not mentioned, do not respond.\n\nParagraph: {paragraph}"

        # Make the API call to Azure OpenAI
        completion = client.chat.completions.create(
            model=deployment,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=10,
            temperature=0.7,
            top_p=0.95,
            frequency_penalty=0,
            presence_penalty=0,
            stop=None,
            stream=False
        )
        
        sentiment = completion.choices[0].message.content.strip()
        if sentiment in ["positive", "negative"]:
            keyword_sentiments.append((keyword, sentiment))
    
    return keyword_sentiments

# Function to process a long paragraph by splitting it
def process_long_paragraph(keywords, paragraph, max_length=500):
    chunks = split_paragraph(paragraph, max_length)
    aggregated_results = []

    for chunk in chunks:
        results = analyze_keywords_in_paragraph(keywords, chunk)
        aggregated_results.extend(results)
    
    # Remove duplicate keyword results (if a keyword appears in multiple chunks, take the first result)
    final_results = {}
    for keyword, sentiment in aggregated_results:
        if keyword not in final_results:
            final_results[keyword] = sentiment
    
    return final_results

# Example paragraph from the user
user_paragraph = """
Finally there is the Analytical who sees no reason to worry about the people involved or even getting it done if it isnt going to be done correctly While the Personal style is focused on the needs of the workers involved and how best to utilize their talents the Practical doesnt really care as much about the personal needs or if it is done right he just wants to get it done One of each style are sitting around a table trying to figure out what to do Heres a simple example of the three in contrast to each other To some extent we are all capable of making all three kinds of decisions but our preference tends to be for one more than the other two To this style the world is a problem to be explored and solved They are more concerned with thinking about things and analysis than actual results or personal concerns of others They see people as part of a system and tend to think in very black and white terms The Analytical Style People with a preference for this style of making decisions tend to see the world from a theoretical perspective more in an abstract way than a concrete one To this style the world is an objective waiting to be achieved They see people in comparative ways as they relate to others They are more concerned with results than others and theory The Practical Style People with a preference for this style of making decisions tend to see things in very practical no nonsense realworld task oriented manner To this style the world is filled with people needing to be understood This involves a personal involvement with concentration on or investment in people They see people in a unique individual light and are more concerned about others than the results and theory The Personal Style People with a preference for this style of making decisions tend to see the world from a personal point of view or with concern for the individuals involved These dimensions can be examined in the form of patterns based on two distinct factors unique to axiology The three decisional styles are the personal the practical and the analytical This preference becomes a subconscious force affecting the decisions we make on a daily basis and shaping how we perceive the world around us and ourselves Each of us can make decisions in these three ways but we tend to develop a preference for one more than the other two Attribute Index Patterns Overview Kanti Gopal Kovvali Copyright Innermetrix Incorporated All rights reserved Over fifty years of scientific research has revealed that there are three distinct styles of decisionmaking Attribute Index Patterns Overview Kanti Gopal Kovvali Copyright Innermetrix Incorporated All rights reserved Over fifty years of scientific research has revealed that there are three distinct styles of decisionmaking Each of us can make decisions in these three ways but we tend to develop a preference for one more than the other two Each of us can make decisions in these three ways but we tend to develop a preference for one more than the other two This preference becomes a subconscious force affecting the decisions we make on a daily basis and shaping how we perceive the world around us and ourselves"""

# Process the paragraph
keyword_sentiments = process_long_paragraph(keywords, user_paragraph)

# Print out the results
for keyword, sentiment in keyword_sentiments.items():
    print(f"Keyword: {keyword}\nSentiment: {sentiment}\n")














# import os
# from openai import AzureOpenAI

# # Azure OpenAI Configuration
# endpoint = "https://hipo-ai.openai.azure.com/"
# deployment = "gpt-4"
# api_key = "1Uty3zR2yIuFmz75r9nDwkAh3mLbNbWZu4XlFDn6AjBoP9foaAE0JQQJ99AJACYeBjFXJ3w3AAAAACOGOqBp"

# client = AzureOpenAI(
#     azure_endpoint=endpoint,
#     api_key=api_key,
#     api_version="2024-05-01-preview"
# )

# keywords = [
#     "Leadership Orientation", "Persuasive Communication", "Result Orientation",
#     "Change Champion", "Innovation mindset", "Customer Focus", "Team Management",
#     "Coaching Orientation", "Delegating", "Data driven problem solving",
#     "Talent Champion", "Direction", "Conflict Management", "Negotiation skills",
#     "Active Listening", "Impactful communication", "Emotional Intelligence",
#     "Synergy driven", "Inter-personal networking", "Collaboration mindset",
#     "Political Acumen", "Global mindset", "Decision Making", "Decisiveness",
#     "Strategic Thinking", "Organisation Stewardship", "Learning Orientation",
#     "Creative Problem-Solving", "Analytical Thinking", "Growth Mindset",
#     "Business Acumen", "Continous Improvement Mindset", "Process Orientation",
#     "Initiative taking", "Time Management", "Strategic Planning", "System driven",
#     "Resilience", "Energetic", "Assertiveness", "Ambitious", "Self-Awareness",
#     "Self driven", "Accountability", "Professionalism", "Dependability", "Adaptability"
# ]

# def analyze_paragraph(paragraph):
#     # Construct a more efficient prompt that analyzes all keywords at once
#     prompt = f"""
#     Analyze the following paragraph and identify which of these competencies/skills are mentioned or implied. 
#     For each identified competency, indicate if it's discussed positively or negatively.
#     Only include competencies that are clearly referenced or implied - do not force matches.
    
#     Paragraph: {paragraph}
    
#     Format your response exactly like this, including ONLY the competencies that are actually mentioned or implied:
#     Competency: Sentiment
    
#     For example:
#     Analytical Thinking: negative
#     Leadership Orientation: positive
#     """

#     # Make a single API call
#     completion = client.chat.completions.create(
#         model=deployment,
#         messages=[{"role": "user", "content": prompt}],
#         max_tokens=500,
#         temperature=0.3,
#         top_p=0.95,
#         frequency_penalty=0,
#         presence_penalty=0,
#         stream=False
#     )

#     # Process the response
#     response = completion.choices[0].message.content.strip()
    
#     # Parse the results into a dictionary
#     results = {}
#     for line in response.split('\n'):
#         if ':' in line:
#             competency, sentiment = line.split(':', 1)
#             competency = competency.strip()
#             sentiment = sentiment.strip().lower()
#             if competency in keywords and sentiment in ['positive', 'negative']:
#                 results[competency] = sentiment
    
#     return results

# # Example usage
# user_paragraph = """
# Would you care to summarise these Adhering closely to policy procedure regulations and precedent would many believe have both a positive and a negative influence on performance They are also designed to identify whether he is adaptable in terms of modifying his behaviour to meet the needs of colleagues The following series of questions can be used to verify the profile and the extent to which Rajnish Sharma is aware of his impact on others within the working environment Are you satisfied with your own level of performance In general terms how well is your organisation performing What were the reasons for these Have you experienced any major disagreements at work in the recent past Is this situation likely to continue If this is the case for how long and for what reasons Do you report to or have you in the recent past reported to more than one manager What evidence is there of this Do you believe that you have the trust and support of your workplace colleagues What three things would you change in him if you could Describe his management style Tell me about your current boss Tight Graph III Are the execution of your duties and responsibilities backed up by the necessary resources and level of authority How do you overcome these Give me some examples of things that frustrate you at work Tell me about your current responsibilities and the management support that you get from your current boss If you ever feel your own performance levels are below expectation how do you overcome the problem What was the outcome When last was your performance formally appraised What are the consequences of these What range of adverse trading or business conditions impact directly or indirectly on you and your team How successful or otherwise have the results been Please summarise recent performance in your job What is your reaction to this observation Tight Graph II There are signs that you may be experiencing very challenging times at work These may be obtained through the Reports screen Points To Review If you have not seen any reference to Points to Review in other Thomas reports additional information will be contained in the PPA Profile and Executive Summary reports This exploratory approach has been prompted by the contents of the PPA report These probing questions have been designed to assist the interviewer in gaining a more indepth understanding of Rajnish Sharma his strengths limitations and behavioural style Thomas International UK Limited httpswwwthomascotermsconditions INTERVIEWERS GUIDE PERSONAL PROFILE ANALYSIS Rajnish Sharma We recommend that the following questions be considered by the interviewer when meeting with Rajnish Sharma Thomas International UK Limited httpswwwthomascotermsconditions INTERVIEWERS GUIDE PERSONAL PROFILE ANALYSIS Rajnish Sharma We recommend that the following questions be considered by the interviewer when meeting with Rajnish Sharma These probing questions have been designed to assist the interviewer in gaining a more indepth understanding of Rajnish Sharma his strengths limitations and behavioural style These probing questions have been designed to assist the interviewer in gaining a more indepth understanding of Rajnish Sharma his strengths limitations and behavioural style This exploratory approach has been prompted by the contents of the PPA report This exploratory approach has been prompted by the contents of the PPA report Points To Review If you have not seen any reference to Points to Review in other Thomas reports additional information will be contained in the PPA Profile and Executive Summary reports Points To Review If you have not seen any reference to Points to Review in other Thomas reports additional information will be contained in the PPA Profile and Executive Summary reports These may be obtained through the Reports screen These may be obtained through the Reports screen Tight Graph II There are signs that you may be experiencing very challenging times at work Tight Graph II There are signs that you may be experiencing very challenging times at work What is your reaction to this observation What is your reaction to this observation Please summarise recent performance in your job Please summarise recent performance in your job How successful or otherwise have the results been How successful or otherwise have the results been What range of adverse trading or business conditions impact directly or indirectly on you and your team What range of adverse trading or business conditions impact directly or indirectly on you and your team What are the consequences of these What are the consequences of these When last was your performance formally appraised When last was your performance formally appraised What was the outcome What was the outcome If you ever feel your own performance levels are below expectation how do you overcome the problem If you ever feel your own performance levels are below expectation how do you overcome the problem Tell me about your current responsibilities and the management support that you get from your current boss Tell me about your current responsibilities and the management support that you get from your current boss Give me some examples of things that frustrate you at work Give me some examples of things that frustrate you at work How do you overcome these How do you overcome these Tight Graph III Are the execution of your duties and responsibilities backed up by the necessary resources and level of authority Tight Graph III Are the execution of your duties and responsibilities backed up by the necessary resources and level of authority Tell me about your current boss Tell me about your current boss Describe his management style Describe his management style What three things would you change in him if you could What three things would you change in him if you could Do you believe that you have the trust and support of your workplace colleagues Do you believe that you have the trust and support of your workplace colleagues What evidence is there of this What evidence is there of this Do you report to or have you in the recent past reported to more than one manager Do you report to or have you in the recent past reported to more than one manager If this is the case for how long and for what reasons If this is the case for how long and for what reasons Is this situation likely to continue Is this situation likely to continue Have you experienced any major disagreements at work in the recent past Have you experienced any major disagreements at work in the recent past What were the reasons for these What were the reasons for these In general terms how well is your organisation performing In general terms how well is your organisation performing Are you satisfied with your own level of performance Are you satisfied with your own level of performance The following series of questions can be used to verify the profile and the extent to which Rajnish Sharma is aware of his impact on others within the working environment The following series of questions can be used to verify the profile and the extent to which Rajnish Sharma is aware of his impact on others within the working environment They are also designed to identify whether he is adaptable in terms of modifying his behaviour to meet the needs of colleagues They are also designed to identify whether he is adaptable in terms of modifying his behaviour to meet the needs of colleagues Adhering closely to policy procedure regulations and precedent would many believe have both a positive and a negative influence on performance Adhering closely to policy procedure regulations and precedent would many believe have both a positive and a negative influence on performance Would you care to summarise these Would you care to summarise these INTERVIEWERS GUIDE Rajnish Sharma Private Confidential INTERVIEWERS GUIDE Rajnish Sharma Private Confidential",
   
#         """

# # Process the paragraph and get results
# results = analyze_paragraph(user_paragraph)

# # Print results
# # print("\nAnalysis Results:")
# # print("-----------------")
# for competency, sentiment in results.items():
#     print(f"{competency}: {sentiment}")


























from flask import Flask, request, jsonify
import fitz  # PyMuPDF
import re
import io





app = Flask(__name__)

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
    sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', text)
    
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

@app.route('/extract', methods=['POST'])
def extract():
    # Check if a PDF file is in the request
    if 'pdf' not in request.files:
        return jsonify({"error": "No PDF file provided"}), 400

    # Save the uploaded file into memory
    pdf_file = request.files['pdf'].read()  # Read the file as bytes
    pdf_file_stream = io.BytesIO(pdf_file)  # Create a BytesIO stream from the byte data

    try:
        # Pass the BytesIO stream directly to fitz.open using the `stream` parameter
        summary_paragraphs = find_summary_paragraph(pdf_file_stream)
        
        if summary_paragraphs:
            return jsonify({"summary_paragraphs": summary_paragraphs})
        else:
            return jsonify({"message": "No summary paragraph found."})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
