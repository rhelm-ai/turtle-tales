from flask import Flask, render_template, request, jsonify, redirect
import openai
import os
from datetime import datetime

app = Flask(__name__)

# Configure OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')

# Store history in memory (in production, you might want to use a database)
story_history = []

# HTTPS redirection and auth token extraction
@app.before_request
def before_request():
    if not request.is_secure and app.env != "development":
        url = request.url.replace("http://", "https://", 1)
        return redirect(url, code=301)


@app.route('/')
def home():
    return render_template('index.html', history=story_history)

@app.route('/generate-story', methods=['POST'])
def generate_story():
    try:
        turtle_description = request.json.get('description', '')
        
        if not turtle_description:
            return jsonify({'error': 'Please provide a turtle description'}), 400

        # Create the initial prompt for the story
        initial_prompt = f"Write a fun, creative story about a sea turtle with the following description: {turtle_description}"

        # Make first API call to OpenAI
        initial_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a creative storyteller who writes fun, family-friendly stories about sea turtles. Include dialogue and vivid descriptions."},
                {"role": "user", "content": initial_prompt}
            ],
            max_tokens=500,
            temperature=0.7
        )

        # Extract the initial story
        initial_story = initial_response.choices[0].message.content.strip()

        # Create the refinement prompt - being very specific about length and completion
        refinement_prompt = (
            "Rewrite this story to be more magical and engaging. The story MUST be complete and MUST be between 80-90 words. "
            "Focus on the most captivating elements and ensure the story has a clear beginning, middle, and end. "
            f"{initial_story}"
        )

        # Make second API call to OpenAI for refinement
        refined_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a master storyteller who creates magical tales with vivid imagery. You must write complete stories between 80-90 words with proper endings. Never leave a story unfinished."},
                {"role": "user", "content": refinement_prompt}
            ],
            max_tokens=200,
            temperature=0.8
        )

        # Extract the refined story
        refined_story = refined_response.choices[0].message.content.strip()

        # Add to history
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        story_entry = {
            'description': turtle_description,
            'story': refined_story,
            'timestamp': timestamp
        }
        story_history.insert(0, story_entry)

        # Keep only the last 10 stories
        if len(story_history) > 10:
            story_history.pop()

        return jsonify({
            'story': refined_story,
            'history': story_history
        })

    except openai.error.OpenAIError as e:
        return jsonify({'error': f'OpenAI API error: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'An unexpected error occurred: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=False)