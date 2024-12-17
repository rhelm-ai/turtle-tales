from flask import Flask, render_template, request, jsonify, redirect, session

import openai

import os

from datetime import datetime

import requests

import base64

from io import BytesIO



app = Flask(__name__)

app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key')  # Required for session



# Configure OpenAI and Hugging Face

openai.api_key = os.getenv('OPENAI_API_KEY')

huggingface_token = os.getenv('HUGGINGFACE_TOKEN')



# Store history in memory (in production, you might want to use a database)

story_history = []



def generate_image(story):

    API_URL = "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5"

    headers = {"Authorization": f"Bearer {huggingface_token}"}

    

    # Create a prompt for the image based on the story

    prompt = f"digital art of a sea turtle: {story}"

    

    try:

        response = requests.post(API_URL, headers=headers, json={

            "inputs": prompt,

            "parameters": {

                "num_inference_steps": 30,

                "guidance_scale": 7.5,

                "negative_prompt": "blurry, bad art, poor quality"

            }

        })

        

        # Convert the image to base64 for embedding in JSON

        image_bytes = response.content

        image_base64 = base64.b64encode(image_bytes).decode('utf-8')

        return image_base64

    except Exception as e:

        print(f"Image generation error: {str(e)}")

        return None



@app.route('/')

def home():

    # Simplify to just render the template

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



        # Create the refinement prompt

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



        # Generate image based on the story

        print("Attempting to generate image...")

        image_base64 = generate_image(refined_story)

        

        if image_base64 is None:

            print("Failed to generate image")

        else:

            print("Successfully generated image")



        # Add to history

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        story_entry = {

            'description': turtle_description,

            'story': refined_story,

            'timestamp': timestamp,

            'image': image_base64

        }

        story_history.insert(0, story_entry)



        # Keep only the last 10 stories

        if len(story_history) > 10:

            story_history.pop()



        return jsonify({

            'story': refined_story,

            'image': image_base64,

            'history': story_history

        })



    except openai.error.OpenAIError as e:

        print(f"OpenAI error: {str(e)}")

        return jsonify({'error': f'OpenAI API error: {str(e)}'}), 500

    except Exception as e:

        print(f"Unexpected error: {str(e)}")

        return jsonify({'error': f'An unexpected error occurred: {str(e)}'}), 500



@app.route('/send-to-chat', methods=['POST'])

def send_to_chat():

    try:

        # Get data from request

        data = request.json

        auth_token = data.get('token')

        tool_id = data.get('tool_id')

        story = data.get('story')



        if not auth_token:

            return jsonify({'error': 'No authentication token provided'}), 401



        if not story:

            return jsonify({'error': 'No story provided'}), 400



        # Send to Einstein Chat API

        einstein_api_url = 'https://api.einstein-chat.com/api/tool/webhook'

        payload = {

            "tool_id": tool_id,

            "tool_input": "Hello",

            "tool_output": story,

            "auth_token": auth_token

        }



        response = requests.post(

            einstein_api_url,

            json=payload,

            headers={

                'accept': 'application/json',

                'Content-Type': 'application/json'

            }

        )



        if response.ok:

            return jsonify({'message': 'Story sent successfully'})

        else:

            return jsonify({'error': f'Failed to send story: {response.text}'}), response.status_code



    except Exception as e:

        print("Exception occurred:", str(e))

        return jsonify({'error': f'An unexpected error occurred: {str(e)}'}), 500



if __name__ == '__main__':

    app.run(debug=False)
