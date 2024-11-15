
import os
from openai import AzureOpenAI

# Azure OpenAI Configuration
endpoint = "https://hipo-ai.openai.azure.com/"
deployment = "gpt-4"
api_key = "1Uty3zR2yIuFmz75r9nDwkAh3mLbNbWZu4XlFDn6AjBoP9foaAE0JQQJ99AJACYeBjFXJ3w3AAAAACOGOqBp"

client = AzureOpenAI(
    azure_endpoint=endpoint,
    api_key=api_key,
    api_version="2024-05-01-preview"
)

keywords = [
    "Leadership Orientation", "Persuasive Communication", "Result Orientation",
    "Change Champion", "Innovation mindset", "Customer Focus", "Team Management",
    "Coaching Orientation", "Delegating", "Data driven problem solving",
    "Talent Champion", "Direction", "Conflict Management", "Negotiation skills",
    "Active Listening", "Impactful communication", "Emotional Intelligence",
    "Synergy driven", "Inter-personal networking", "Collaboration mindset",
    "Political Acumen", "Global mindset", "Decision Making", "Decisiveness",
    "Strategic Thinking", "Organisation Stewardship", "Learning Orientation",
    "Creative Problem-Solving", "Analytical Thinking", "Growth Mindset",
    "Business Acumen", "Continous Improvement Mindset", "Process Orientation",
    "Initiative taking", "Time Management", "Strategic Planning", "System driven",
    "Resilience", "Energetic", "Assertiveness", "Ambitious", "Self-Awareness",
    "Self driven", "Accountability", "Professionalism", "Dependability", "Adaptability"
]

 

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

# Example usage
user_paragraph = """

ENTPs constantly scan their environment for opportunities and possibilities.
They see patterns and connections not obvious to others and at times
seem able to see into the future. They are adept at generating conceptual
possibilities and then analyzing them strategically. ENTPs are good at
understanding how systems work and are enterprising and resourceful in
maneuvering within them to achieve their ends.
ENTPs are enthusiastic innovators. Their world is full of possibilities,
interesting concepts, and exciting challenges. They are stimulated by
difficulties, quickly devising creative responses and plunging into activity,
trusting their ability to improvise. They enjoy using their ingenuity. ENTPs are
likely to be creative, imaginative, clever, theoretical, conceptual, and curious.
ENTPs like to analyze situations and their own ideas and to plan. They admire
competence, intelligence, precision, and efficiency. ENTPs are usually
analytical, logical, rational, objective, assertive, and questioning. They are
enterprising, resourceful, active, and energetic. They respond to challenging
problems by creating complex and global solutions. They can do almost
anything that captures their interest.
ENTPs are spontaneous and adaptable. They find schedules and standard
operating procedures confining and work around them whenever possible.
They are remarkably insightful about the attitudes of others, and their
enthusiasm and energy can mobilize people to support their vision. Their
conversational style is seen by many as challenging and stimulating because
they love to debate ideas. They are fluent conversationalists, are mentally
quick, and enjoy verbal sparring. At times they may speak with an intensity
and abruptness that seem to challenge others. Others usually see ENTPs as
independent, autonomous, creative, lively, enthusiastic, energetic, assertive,
and outspoken.
Sometimes life circumstances have not supported ENTPs in the development
and expression of their Intuition and Thinking preferences. If they have not
developed their Intuition, ENTPs may not take in enough relevant information,
resulting in “insights” unrelated to current reality. If they have not developed
their Thinking, they may not have reliable ways to evaluate their insights
and make plans to carry them through. Then they go from enthusiasm to
enthusiasm but may actually accomplish little or nothing.
        """

# Process the paragraph and get results
results = analyze_paragraph(user_paragraph)

 

# Print results

for competency, sentiment in results.items():
    print(f"{competency}: {sentiment}")
 