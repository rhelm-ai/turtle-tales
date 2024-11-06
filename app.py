from flask import Flask, render_template, request, jsonify
import openai
import os
from datetime import datetime

app = Flask(__name__)

# Configure OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')

# Store history in memory (in production, you might want to use a database)
story_history = []

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
        initial_prompt = f"Write a fun, short story (max 200 words) about a sea turtle with the following description: {turtle_description}"

        # Make first API call to OpenAI
        initial_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a creative storyteller who writes fun, family-friendly stories about sea turtles."},
                {"role": "user", "content": initial_prompt}
            ],
            max_tokens=300,
            temperature=0.7
        )

        # Extract the initial story
        initial_story = initial_response.choices[0].message.content.strip()

        # Create the refinement prompt
        refinement_prompt = (
            "Please rewrite the following story to make it more creative, magical, and concise (max 150 words). "
            "Add more vivid imagery and enchanting details while keeping it child-friendly: \n\n"
            f"{initial_story}"
        )

        # Make second API call to OpenAI for refinement
        refined_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a master storyteller who specializes in creating magical, concise stories with vivid imagery."},
                {"role": "user", "content": refinement_prompt}
            ],
            max_tokens=250,
            temperature=0.8
        )

        # Extract the refined story
        refined_story = refined_response.choices[0].message.content.strip()

        # Add to history
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        story_entry = {
            'description': turtle_description,
            'story': refined_story,  # Use the refined story
            'timestamp': timestamp
        }
        story_history.insert(0, story_entry)  # Add to beginning of list

        # Keep only the last 10 stories
        if len(story_history) > 10:
            story_history.pop()

        return jsonify({
            'story': refined_story,  # Return the refined story
            'history': story_history
        })

    except openai.error.OpenAIError as e:
        return jsonify({'error': f'OpenAI API error: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'An unexpected error occurred: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=False)