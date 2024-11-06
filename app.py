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

        # Create the prompt for the story
        prompt = f"Write a fun, short story (max 200 words) about a sea turtle with the following description: {turtle_description}"

        # Make API call to OpenAI
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a creative storyteller who writes fun, family-friendly stories about sea turtles."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300,
            temperature=0.7
        )

        # Extract the story from the response
        story = response.choices[0].message.content.strip()

        # Add to history
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        story_entry = {
            'description': turtle_description,
            'story': story,
            'timestamp': timestamp
        }
        story_history.insert(0, story_entry)  # Add to beginning of list

        # Keep only the last 10 stories
        if len(story_history) > 10:
            story_history.pop()

        return jsonify({
            'story': story,
            'history': story_history
        })

    except openai.error.OpenAIError as e:
        return jsonify({'error': f'OpenAI API error: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'An unexpected error occurred: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=False) 