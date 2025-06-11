from flask import Flask, request, jsonify
import fitz  # PyMuPDF
import re
import io
from openai import AzureOpenAI
import json  # Added this import


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
    
# def analyze_insights(summaries):
#     combined_text = "\n\n".join([f"Report {i+1}:\n{summary}" for i, summary in enumerate(summaries)])

#     prompt = f"""
# You are an expert feedback analyst.

# 1. **Extracting Key Insights from Reports**
# {combined_text}

# 2. **Cross-Document Analysis**
# - Combine feedback from multiple reports and identify:
#     - Common strengths across all reports.
#     - Common improvement areas across all reports.
#     - Any contradictory feedback or outliers.
# - Create a summary of feedback trends across all uploaded reports. Highlight consistent themes and diverging opinions.

# 3. **Linking Strengths and Improvement Areas**
# - Analyze the strengths and improvement areas listed. Are there any improvement areas that could be side effects or overextensions of the person’s strengths? Provide examples.
# - Highlight any potential trade-offs between strengths and improvement areas.

# 4. **Identifying Blind Spots**
# - Based on this feedback, identify any potential blind spots for the individual.
# - What assumptions might the person be making about their own strengths or improvement areas based on this feedback? Suggest areas for reflection.

# 5. **Actionable Insights**
# - Turn this feedback into actionable insights.
# - Suggest specific actions to leverage strengths further.
# - Provide steps to address areas for improvement effectively.
# - Create a development plan with short-term (1-3 months) and long-term (6-12 months) goals.

# Respond clearly and concisely in **plain text**, without headings, bullets, or markdown formatting.
# Just write readable, paragraph-style insights with minimal structure.

# """

#     completion = client.chat.completions.create(
#         model=deployment,
#         messages=[{"role": "user", "content": prompt}],
#         max_tokens=1200,
#         temperature=0.3,
#         top_p=0.95,
#         frequency_penalty=0,
#         presence_penalty=0,
#         stream=False
#     )

#     response = completion.choices[0].message.content.strip()
#     return response


# @app.route('/insights', methods=['POST'])
# def insights():
#     if not request.is_json or 'summaries' not in request.json:
#         return jsonify({"error": "Missing 'summaries' field in request or invalid format."}), 400

#     summaries = request.json['summaries']

#     # Normalize input to a list of strings
#     if isinstance(summaries, str):
#         summaries = [summaries]
#     elif not isinstance(summaries, list) or not all(isinstance(item, str) for item in summaries):
#         return jsonify({"error": "'summaries' must be a string or a list of strings."}), 400

#     try:
#         result = analyze_insights(summaries)
#         print("Insight Output:\n", result)  # Debugging
#         return result, 200, {'Content-Type': 'text/plain'}

#     except Exception as e:
#         return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500
def analyze_insights(summaries):
    summaries = [s.strip() for s in summaries if isinstance(s, str) and s.strip()]
    combined_text = "\n\n".join([f"Report {i + 1}:\n{summary}" for i, summary in enumerate(summaries)])


    prompt = f"""
    Section 1: Prompt for identifying strengths and weaknesses from each report

    Task:
    Summarize a psychometric or developmental report as a trusted career coach. Identify key strengths and areas of improvements in 2-3 lines each, focusing on critical insights for self-awareness and growth. Be specific, actionable, and motivational.

    Example Output:

    Strengths:
    You excel at solving problems under pressure and inspire trust with your collaborative approach.

    Growth Opportunities:
    Improve time management to reduce stress and build confidence to take bold leadership steps.

    <Input: uploaded report / data>


    Section 2: Summary section:

    Play the role of a trusted coach. You have been shared with longitudinal psychometric data (strengths and improvement areas across reports and testimonials by year). Analyse trends across the longitudinal data in terms of strengths and improvement and, provide a 2-paragraph insight covering these key areas:

    Common Strength Themes: Identify recurring strengths and what they reveal about the individual’s core capabilities.
    Common Improvement Themes: Highlight consistent areas for growth and their impact.
    Contradictory Feedback or Outliers: Identify any contradictions or unique patterns across reports.
    Links Between Strengths and Improvement Areas: Examine the Relationship Between Strengths and Improvement Areas (if any improvement area is a possible side effect of a strength of that person)
    Blind Spots: Point out overlooked areas of potential concern.
    Recommended Actions: Provide short- and long-term steps to maximize strengths and address improvement areas.

    Here are the reports:

    {combined_text}

    Strictly return ONLY the final two-paragraph insight and the concise strengths and growth opportunities. No headings, no formatting, and no extra text.
    """

    completion = client.chat.completions.create(
        model=deployment,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1000,
        temperature=0.3,
        top_p=0.95,
        frequency_penalty=0,
        presence_penalty=0,
        stream=False
    )

    return completion.choices[0].message.content.strip()


@app.route('/insights', methods=['POST'])
def insights():
    if not request.is_json or 'summaries' not in request.json:
        return jsonify({"error": "Missing 'summaries' field in request or invalid format."}), 400

    summaries = request.json['summaries']

    if isinstance(summaries, str):
        summaries = [summaries]
    elif not isinstance(summaries, list) or not all(isinstance(item, str) for item in summaries):
        return jsonify({"error": "'summaries' must be a string or a list of strings."}), 400

    summaries = [s.strip() for s in summaries if s.strip()]
    if not summaries:
        return jsonify({"error": "No valid summaries found after filtering empty inputs."}), 400

    try:
        result = analyze_insights(summaries)
        print("Insight Output:\n", result)
        return result, 200, {'Content-Type': 'text/plain'}
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500


def analyze_summary(name, industry, function, current_level, experience, personal_aspiration, professional_aspiration,
                    non_negotiable_values, skills, functional_technical_skills, five_year_goals,
                    improvement_areas, strengths, selected_areas_to_work_on, cultural_working_preference, other_info):

    prompt = f"""
    You are a strategic talent analyst. Based on the provided structured profile, return only a single plain paragraph (~200 words) that meets the following brief:

    1. Connect the dots between the individual's demographic background, aspirations, skills, and personality traits.
    2. Highlight the top 3 interesting insights from their strengths, improvement areas, and potential blind spots.
    3. Conclude with the top 2 levers (skills, habits, mindset) that can drive their success in their 5-year goal.

    Do not include bullets, lists, formatting, or extra comments. Strictly output only one concise paragraph with an analytical tone.

    Input Profile:

    ### Demographic Data:
    - Name: {name}
    - Industry: {industry}
    - Function: {function}
    - Current Level: {current_level}
    - Experience: {experience} years

    ### Person's Profile:
    - Personal Aspiration: {personal_aspiration}
    - Professional Aspiration: {professional_aspiration}
    - Non-Negotiable Values: {non_negotiable_values}
    - Skill to Plan and Execute: {skills.get("plan_and_execute", "N/A")} / 5
    - Skill to Connect and Build Trusting Relationships: {skills.get("connect_and_build_trusting_relationships", "N/A")} / 5
    - Skill to Think and Decide: {skills.get("think_and_decide", "N/A")} / 5
    - Skill to Learn and Grow: {skills.get("learn_and_grow", "N/A")} / 5
    - Functional/Technical Skills: {functional_technical_skills}
    - Strengths: {strengths}
    - Improvement Areas: {improvement_areas}
    - Selected Areas to Work On: {selected_areas_to_work_on}
    - Cultural Working Preference: {cultural_working_preference}
    - Five-Year Goals:
        - Realistic: {five_year_goals.get("realistic_goal")}
        - Aspirational: {five_year_goals.get("aspirational_goal")}

    ### Additional Context:
    {other_info}

    Only return the final paragraph.
    """

    completion = client.chat.completions.create(
        model=deployment,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=700,
        temperature=0.4,
        top_p=0.9,
        frequency_penalty=0,
        presence_penalty=0,
        stream=False
    )

    return completion.choices[0].message.content.strip()


@app.route('/full-summary', methods=['POST'])
def full_summary():
    try:
        data = request.json

        required_fields = [
            'name', 'industry', 'function', 'current_level', 'experience',
            'personal_aspiration', 'professional_aspiration', 'non_negotiable_values',
            'skills', 'functional_technical_skills', 'five_year_goals',
            'improvement_areas', 'strengths', 'selected_areas_to_work_on',
            'cultural_working_preference', 'other_info'
        ]

        missing = [field for field in required_fields if field not in data]
        if missing:
            return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

        result = analyze_summary(
            name=data['name'],
            industry=data['industry'],
            function=data['function'],
            current_level=data['current_level'],
            experience=data['experience'],
            personal_aspiration=data['personal_aspiration'],
            professional_aspiration=data['professional_aspiration'],
            non_negotiable_values=data['non_negotiable_values'],
            skills=data['skills'],
            functional_technical_skills=data['functional_technical_skills'],
            five_year_goals=data['five_year_goals'],
            improvement_areas=data['improvement_areas'],
            strengths=data['strengths'],
            selected_areas_to_work_on=data['selected_areas_to_work_on'],
            cultural_working_preference=data['cultural_working_preference'],
            other_info=data['other_info']
        )

        print("Full Summary Output:\n", result)
        return result, 200, {'Content-Type': 'text/plain'}

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


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
        
        # if not summary_paragraphs:
        #     return jsonify({"message": "No summary paragraph."}), 200
        if not summary_paragraphs:
            full_text = extract_full_text(pdf_file_stream)
            return analyze_paragraph(full_text)

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


# Route to process development coaching data
@app.route('/development-coaching', methods=['POST'])
def development_coaching():
    if not request.is_json:
        return jsonify({"error": "Invalid request format. JSON expected."}), 400

    required_fields = [
        'industry', 'function', 'current_level', 'experience',
        'personal_aspiration', 'professional_aspiration', 'non_negotiable_values',
        'skills', 'functional_technical_skills', 'five_year_goals',
        'improvement_areas', 'strengths', 'selected_areas_to_work_on',
        'cultural_working_preference'
    ]

    # Check if all required fields are present
    missing_fields = [field for field in required_fields if field not in request.json]
    if missing_fields:
        return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400

    try:
        # Extract data from request
        coaching_data = request.json

        # Process coaching data and generate recommendations
        recommendations = generate_coaching_recommendations(coaching_data)
        
        # Structure the response according to the required format
        formatted_response = format_coaching_recommendations(recommendations)
        
        return formatted_response, 200, {'Content-Type': 'text/plain'}

        # formatted_response = format_coaching_recommendations_json(recommendations)
        
        # return formatted_response, 200, {'Content-Type': 'application/json'}

    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

def generate_coaching_recommendations(coaching_data):
    """Process the coaching data using Azure OpenAI to generate recommendations"""
    
    # Create prompt with template and coaching data
    prompt_template = """
You are an expert development coach with deep expertise in behavioral economics, nudge theory, and personalized coaching. 
Use the following demographic and profile data to create tailored recommendations for personal and professional growth.
You are known for your depth of insight, clarity of thought and communication, use of language which is simple and devoid of jargon,
ability to connect the dots,differentiate the critical from the not so critical and prioritise development areas andhighlight blindspots which the coachee might have missed by analysing how theirstrengths when taken to an extreme can become a weakness.

### Demographic Data:
1. Industry: {industry}
2. Function: {function}
3. Current Level: {current_level}
4. Experience: {experience}

### Person's Profile:
1. Personal Aspiration: {personal_aspiration}
2. Professional Aspiration: {professional_aspiration}
3. Non-Negotiable Values: {non_negotiable_values}
4. Professional Skills Profile:
   - Skill to Plan and Execute: {skills[plan_and_execute]} out of 5
   - Skill to Connect and Build Trusting Relationships: {skills[connect_and_build_trusting_relationships]} out of 5
   - Skill to Think and Decide: {skills[think_and_decide]} out of 5
   - Skill to Learn and Grow: {skills[learn_and_grow]} out of 5
5. Functional/Technical Skills: {functional_technical_skills}
6. Five-Year Goals:
   - Realistic Goal: {five_year_goals[realistic_goal]}
   - Aspirational Goal: {five_year_goals[aspirational_goal]}
7. Improvement Areas: {improvement_areas}
8. Strengths: {strengths}

### Selected Areas to Work On: {selected_areas_to_work_on}
### Cultural Working Preference: {cultural_working_preference}

Generate a JSON response with the following structure:
{{
  "targeted_questions": [
    {{
      "topic": "Topic area (e.g., Delegation)",
      "question": "Specific behavioral question",
      "bias": "Name and brief explanation of bias"
    }},
    // Two more questions
  ],
  "practical_actions": [
    {{
      "name": "Action name",
      "instruction": "Specific step-by-step instruction taking less than 2 minutes",
      "rationale": "Clear rationale linking to profile data"
    }},
    // Two more actions
  ],
  "strategic_actions": [
    {{
      "title": "Strategic action title",
      "steps": ["Step 1", "Step 2", "Step 3"],
      "rationale": "Strategic rationale linking to career goals"
    }},
    // One more action
  ],
  "blind_spots": [
    {{
      "name": "Blind spot name",
      "risk": "Why it's a risk",
      "impact": "Impact on aspirations and values",
      "solution": "Solution"
    }},
    // Three more blind spots
  ],
  "commitment_plan": {{
    "immediate": "Specific action for this week",
    "short_term": "Specific action for next 30 days",
    "mid_term": "Specific action for next 90 days",
    "long_term": "Specific action for ongoing"
  }}
}}


"""
#   Your recommendations must cover these themes:
# - Delegation and control
# - Decision-making patterns
# - Trust and relationship building
# - Work-life balance
# - Leadership scaling  

    # Format prompt with coaching data
    formatted_prompt = prompt_template.format(**coaching_data)
    
    try:
        # Call Azure OpenAI for completion
        completion = client.chat.completions.create(
            model=deployment,
            messages=[{"role": "user", "content": formatted_prompt}],
            max_tokens=1500,
            temperature=0.3,
            top_p=0.95,
            frequency_penalty=0,
            presence_penalty=0,
            stream=False
        )
        
        # Extract and parse the response
        ai_response = completion.choices[0].message.content
        recommendations = json.loads(ai_response)
        
        return recommendations
        
    except Exception as e:
        print(f"Error calling Azure OpenAI: {str(e)}")
        # Return default recommendations if API call fails
        return get_default_recommendations(coaching_data)

def get_default_recommendations(coaching_data):
    """Return default recommendations if the AI call fails"""
    return {
        'targeted_questions': [
            {
                'topic': 'Delegation',
                'question': 'How might your need for control be limiting your teams growth?',
                'bias': 'Ownership Bias – Tendency to value what youve created more than others work'
            },
            {
                'topic': 'Decision Making',
                'question': 'When was the last time you made a decision with incomplete information?',
                'bias': 'Analysis Paralysis – Overvaluing perfect information at cost of timeliness'
            },
            {
                'topic': 'Trust Building',
                'question': 'What team members capabilities have you underestimated recently?',
                'bias': 'Competence Bias – Assuming others cannot match your standards'
            }
        ],
        'practical_actions': [
            {
                'name': 'Two-Minute Delegation Exercise',
                'instruction': 'Identify one task youre currently doing and write down who could do it instead',
                'rationale': f"Builds the habit of looking for delegation opportunities based on your goal to {coaching_data['professional_aspiration']}"
            },
            {
                'name': 'Decision Timeboxing',
                'instruction': 'Set a timer for important decisions based on their impact - 5 minutes for small, 30 for medium, 24 hours for large',
                'rationale': 'Prevents overthinking while maintaining quality aligned with your analytical strengths'
            },
            {
                'name': 'Trust Deposit',
                'instruction': 'Each morning, identify one opportunity to express confidence in a team members abilities',
                'rationale': f"Systematically builds psychological safety while addressing your improvement area of {coaching_data['improvement_areas']}"
            }
        ],
        'strategic_actions': [
            {
                'title': 'Delegation System Implementation',
                'steps': [
                    'Map current responsibilities',
                    'Identify delegation candidates for each area',
                    'Schedule handover meetings'
                ],
                'rationale': f"Creates structured progress toward your five-year goal of {coaching_data['five_year_goals']['aspirational_goal']} while addressing control tendencies"
            },
            {
                'title': 'Decision Framework Adoption',
                'steps': [
                    'Document your decision criteria',
                    'Create templates for different decision types',
                    'Share framework with team for feedback'
                ],
                'rationale': 'Systematizes your strong analytical thinking while making it accessible to others'
            }
        ],
        'blind_spots': [
            {
                'name': 'Perfectionism in Others',
                'risk': 'Setting unrealistic standards based on your own capabilities',
                'impact': f"Creates tension between your aspiration for team growth and your value of {coaching_data['non_negotiable_values'][0] if coaching_data['non_negotiable_values'] else 'excellence'}",
                'solution': 'Define "good enough" criteria for each role and deliverable'
            },
            {
                'name': 'Relationship Building as "Extra"',
                'risk': 'Treating relationship development as secondary to task completion',
                'impact': 'Undermines your aspiration for senior leadership which requires strong networks',
                'solution': 'Schedule relationship building as a priority task with measurable outcomes'
            },
            {
                'name': 'Over-reliance on Technical Skills',
                'risk': 'Defaulting to technical solutions when people solutions are needed',
                'impact': 'Creates disconnect between your value of people development and your behavior',
                'solution': 'Ask "Is this a technical or people challenge?" before responding to problems'
            },
            {
                'name': 'Work-Life Imbalance',
                'risk': 'Sacrificing personal goals for professional achievement',
                'impact': f"Creates long-term conflict with personal aspirations like {coaching_data['personal_aspiration']}",
                'solution': 'Define non-negotiable personal commitments and block calendar accordingly'
            }
        ],
        'commitment_plan': {
            'immediate': 'Identify three tasks to delegate this week',
            'short_term': 'Implement decision timeboxing framework',
            'mid_term': 'Complete delegation mapping for all responsibilities',
            'long_term': 'Monthly review of blind spot mitigation progress'
        }
    }

    
def format_coaching_recommendations_json(recommendations):
    """Format the recommendations into a structured JSON format"""
    
    output = {
        "A. Targeted Development Questions": [
            {
                "Topic": q['topic'],
                "Question": q['question'],
                "Bias Addressed": q['bias']
            }
            for q in recommendations['targeted_questions']
        ],
        
        "B. Three Practical and Easy-to-Do Actions": [
            {
                "Action Name": action['name'],
                "Instruction": action['instruction'],
                "Why": action['rationale']
            }
            for action in recommendations['practical_actions']
        ],
        
        "C. Two Most Relevant and Impactful Actions": [
            {
                "Title": action['title'],
                "Steps": [f"Step {j + 1}: {step}" for j, step in enumerate(action['steps'])],
                "Why": action['rationale']
            }
            for action in recommendations['strategic_actions']
        ],
        
        "D. Blind Spots": [
            {
                "Blind Spot": spot['name'],
                "Why It's a Risk": spot['risk'],
                "Impact on Aspirations & Values": spot['impact'],
                "Solution": spot['solution']
            }
            for spot in recommendations['blind_spots']
        ],
        
        "E. Next Steps & Commitment Plan": {
            "Immediate Action (This Week)": recommendations['commitment_plan']['immediate'],
            "Short-Term (Next 30 Days)": recommendations['commitment_plan']['short_term'],
            "Mid-Term (Next 90 Days)": recommendations['commitment_plan']['mid_term'],
            "Long-Term (Ongoing)": recommendations['commitment_plan']['long_term']
        }
    }
    
    return jsonify(output)

def format_coaching_recommendations(recommendations):
    """Format the recommendations according to the required structure"""
    output = []
    
    # A. Targeted Development Questions
    output.append("A. Targeted Development Questions")
    for i, q in enumerate(recommendations['targeted_questions'], 1):
        output.append(f"{q['topic']}")
        output.append(f"{q['question']}")
        output.append(f"• Bias Addressed: {q['bias']}")
        if i < len(recommendations['targeted_questions']):
            output.append("")   
    
    output.append("\n")  
    
    # B. Three Practical and Easy-to-Do Actions
    output.append("B. Three Practical and Easy-to-Do Actions")
    for i, action in enumerate(recommendations['practical_actions'], 1):
        output.append(f"{i}. \"{action['name']}\"")
        output.append(f"• {action['instruction']}")
        output.append(f"• Why? {action['rationale']}")
        if i < len(recommendations['practical_actions']):
            output.append("")  # Empty line between actions
    
    output.append("\n")  # Separator between sections
    
    # C. Two Most Relevant and Impactful Actions
    output.append("C. Two Most Relevant and Impactful Actions")
    for i, action in enumerate(recommendations['strategic_actions'], 1):
        output.append(f"{i}. {action['title']}")
        for j, step in enumerate(action['steps'], 1):
            output.append(f"• Step {j}: {step}")
        output.append(f"• Why? {action['rationale']}")
        if i < len(recommendations['strategic_actions']):
            output.append("")  # Empty line between actions
    
    output.append("\n")  # Separator between sections
    
    # D. Blind Spots
    output.append("D. Blind Spots")
    # output.append("| Blind Spot | Why It's a Risk | Impact on Aspirations & Values | Solution |")
    # output.append("|------------|----------------|--------------------------------|----------|")
    output.append("D. Blind Spots\n")
    for spot in recommendations['blind_spots']:
        output.append(f"- Blind Spot: {spot['name']}")
        output.append(f"  - Why It's a Risk: {spot['risk']}")
        output.append(f"  - Impact on Aspirations & Values: {spot['impact']}")
        output.append(f"  - Solution: {spot['solution']}\n")  # Extra newline for spacing between entries    
    # for spot in recommendations['blind_spots']:
    #     output.append(f"| {spot['name']} | {spot['risk']} | {spot['impact']} | {spot['solution']} |")
    
    output.append("\n")  # Separator between sections
    
    # E. Next Steps & Commitment Plan
    output.append("E. Next Steps & Commitment Plan")
    output.append(f"1. Immediate Action (This Week): {recommendations['commitment_plan']['immediate']}")
    output.append(f"2. Short-Term (Next 30 Days): {recommendations['commitment_plan']['short_term']}")
    output.append(f"3. Mid-Term (Next 90 Days): {recommendations['commitment_plan']['mid_term']}")
    output.append(f"4. Long-Term (Ongoing): {recommendations['commitment_plan']['long_term']}")
    
    return "\n".join(output)








def generate_prompt1(coaching_data):
    try:
        # Build each section dynamically to avoid string formatting issues
        sections = []
        
        # 1. Individual vs Collective
        sections.append(f"""
1. Individual vs Collective Achievement
   - Self Score: {coaching_data['individual_vs_collective']['self_score']}
   - Team Score: {coaching_data['individual_vs_collective']['team_score']}
   - Gap: {abs(coaching_data['individual_vs_collective']['self_score'] - coaching_data['individual_vs_collective']['team_score'])}
   - Definition: A culture that values individual achievements and rewards personal excellence vs. a culture prioritizing collective achievement and shared success.""")

        # 2. Team vs Customer
        sections.append(f"""
2. Team-Centric vs Customer-Centric Focus
   - Self Score: {coaching_data['team_vs_customer']['self_score']}
   - Team Score: {coaching_data['team_vs_customer']['team_score']}
   - Gap: {abs(coaching_data['team_vs_customer']['self_score'] - coaching_data['team_vs_customer']['team_score'])}
   - Definition: A mindset prioritizing the team's internal needs vs. a focus on meeting external stakeholder needs.""")

        # 3. Process vs Results
        sections.append(f"""
3. Process vs Results Orientation
   - Self Score: {coaching_data['process_vs_results']['self_score']}
   - Team Score: {coaching_data['process_vs_results']['team_score']}
   - Gap: {abs(coaching_data['process_vs_results']['self_score'] - coaching_data['process_vs_results']['team_score'])}
   - Definition: Security in following procedures vs. prioritizing outcomes and targets.""")

        # 4. Personal vs Stakeholder
        sections.append(f"""
4. Personal vs Stakeholder Expectations
   - Self Score: {coaching_data['personal_vs_stakeholder']['self_score']}
   - Team Score: {coaching_data['personal_vs_stakeholder']['team_score']}
   - Gap: {abs(coaching_data['personal_vs_stakeholder']['self_score'] - coaching_data['personal_vs_stakeholder']['team_score'])}
   - Definition: Driven by personal excellence vs. prioritizing stakeholder expectations.""")

        # 5. Deliberate vs Radical
        sections.append(f"""
5. Deliberate vs Radical Change Approach
   - Self Score: {coaching_data['deliberate_vs_radical']['self_score']}
   - Team Score: {coaching_data['deliberate_vs_radical']['team_score']}
   - Gap: {abs(coaching_data['deliberate_vs_radical']['self_score'] - coaching_data['deliberate_vs_radical']['team_score'])}
   - Definition: Preferring slow, careful changes vs. embracing rapid, transformative shifts.""")

        # 6. Structured vs Flexible
        sections.append(f"""
6. Structured vs Flexible Planning
   - Self Score: {coaching_data['structured_vs_flexible']['self_score']}
   - Team Score: {coaching_data['structured_vs_flexible']['team_score']}
   - Gap: {abs(coaching_data['structured_vs_flexible']['self_score'] - coaching_data['structured_vs_flexible']['team_score'])}
   - Definition: Preferring detailed planning vs. adapting spontaneously to situations.""")

        # 7. Competitive vs Collaborative
        sections.append(f"""
7. Competitive vs Collaborative Spirit
   - Self Score: {coaching_data['competitive_vs_collaborative']['self_score']}
   - Team Score: {coaching_data['competitive_vs_collaborative']['team_score']}
   - Gap: {abs(coaching_data['competitive_vs_collaborative']['self_score'] - coaching_data['competitive_vs_collaborative']['team_score'])}
   - Definition: Thriving in competitive environments vs. finding fulfillment in teamwork.""")

        # 8. Perfect vs Practical
        sections.append(f"""
8. Perfect vs Practical Solutions
   - Self Score: {coaching_data['perfect_vs_practical']['self_score']}
   - Team Score: {coaching_data['perfect_vs_practical']['team_score']}
   - Gap: {abs(coaching_data['perfect_vs_practical']['self_score'] - coaching_data['perfect_vs_practical']['team_score'])}
   - Definition: Seeking perfect solutions aligned with values vs. prioritizing effective, adaptable approaches.""")

        # Combine all sections and add the final instructions
        prompt = "Analyze the cultural preferences and provide recommendations:" + "".join(sections)
        
        prompt += """

Based on these inputs, provide 3 actionable coaching recommendations for each cultural preference.
Output JSON format:
{
  "actions": [
    "Action 1",
    "Action 2",
    "Action 3",
    // ... continue until Action 24 (3 recommendations per preference)
  ]
}"""

        return prompt

    except KeyError as e:
        raise ValueError(f"Missing required data field: {str(e)}")
    except Exception as e:
        raise ValueError(f"Error generating prompt: {str(e)}")

# @app.route("/culture_preference", methods=["POST"])
# def culture_preference():
#     try:
#         # Get and validate input data
#         coaching_data = request.json
#         if not coaching_data:
#             return jsonify({"error": "No data provided"}), 400

#         # Generate prompt
#         formatted_prompt = generate_prompt1(coaching_data)

#         # Call Azure OpenAI
#         completion = client.chat.completions.create(
#             model=deployment,
#             messages=[{"role": "user", "content": formatted_prompt}],
#             max_tokens=1500,
#             temperature=0.3,
#             top_p=0.95,
#             frequency_penalty=0,
#             presence_penalty=0,
#             stream=False
#         )

#         # Extract and validate response
#         ai_response = completion.choices[0].message.content
#         try:
#             recommendations = json.loads(ai_response)
#             if not isinstance(recommendations, dict) or 'actions' not in recommendations:
#                 return jsonify({"error": "Invalid AI response format"}), 500
#             return jsonify(recommendations)
#         except json.JSONDecodeError:
#             return jsonify({"error": "Invalid JSON response from AI"}), 500

#     except ValueError as ve:
#         return jsonify({"error": str(ve)}), 400
#     except Exception as e:
#         print("Error calling Azure OpenAI:", str(e))
#         return jsonify({"error": "Failed to generate recommendations"}), 500

@app.route("/culture_preference", methods=["POST"])
def culture_preference():
    try:
        # Get and validate input data
        coaching_data = request.json
        if not coaching_data:
            return jsonify({"error": "No data provided"}), 400

        # Generate prompt
        formatted_prompt = generate_prompt1(coaching_data)

        # Call Azure OpenAI
        completion = client.chat.completions.create(
            model=deployment,
            messages=[{"role": "user", "content": formatted_prompt}],
            max_tokens=1500,
            temperature=0.3,
            top_p=0.95,
            frequency_penalty=0,
            presence_penalty=0,
            stream=False
        )

        # Extract and validate response
        ai_response = completion.choices[0].message.content
        try:
            recommendations = json.loads(ai_response)
            if not isinstance(recommendations, dict) or 'actions' not in recommendations:
                return jsonify({"error": "Invalid AI response format"}), 500
            
            # Convert the list into a plain text string
            actions_text = " ,,, ".join(recommendations["actions"])
            return actions_text, 200, {"Content-Type": "text/plain"}
        
        except json.JSONDecodeError:
            return jsonify({"error": "Invalid JSON response from AI"}), 500

    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        print("Error calling Azure OpenAI:", str(e))
        return jsonify({"error": "Failed to generate recommendations"}), 500



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
