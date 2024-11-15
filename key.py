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
Finally there is the Analytical who sees no reason to worry about the people involved or even getting it done if it isnt g """

# Process the paragraph
keyword_sentiments = process_long_paragraph(keywords, user_paragraph)

# Print out the results
for keyword, sentiment in keyword_sentiments.items():
    print(f"Keyword: {keyword}\nSentiment: {sentiment}\n")
