# Copyright 2022 Google LLC

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     https://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# import functions_framework  # Import the functions_framework library for HTTP functions
# import vertexai  # Import the vertexai library for AI model handling
# from vertexai.preview.language_models import TextGenerationModel  # Import the TextGenerationModel from vertexai
# import json  # Import the JSON library for working with JSON data

# # Replace with your project ID !!!
# PROJECT_ID = ""  

# # Define a function named "summarize" that takes a text input and generates a response
# def summarize(text: str):
#     parameters = {
#         "temperature": 0.2,          # Control the randomness of the generated text
#         "max_output_tokens": 256,    # Limit the maximum number of output tokens
#         "top_p": 0.8,               # Set a nucleus sampling threshold
#         "top_k": 40,                # Set a top-k sampling threshold
#     }

#     # Initialize the Vertex AI project with the provided project ID
#     vertexai.init(project=PROJECT_ID)

#     # Load the pre-trained TextGenerationModel named "text-bison@001"
#     model = TextGenerationModel.from_pretrained("text-bison@001")

#     # Generate a response by providing the input text and model parameters
#     response = model.predict(
#         f"Make a short summary : {text}",  # Format the input text
#         **parameters,  # Pass the defined parameters
#     )

#     # Print the response from the model
#     print(f"Response from Model: {response.text}")

#     # Return the generated response as text
#     return response.text

# # Define an HTTP function using the functions_framework library
# @functions_framework.http
# def hello_vertex(request):
#     # Process and clean the input data received from the HTTP request
#     parsed_data = (str(request.data)).replace('"', "").replace("'", "").replace(",", "").replace("\n", "")

#     # Call the "summarize" function with the cleaned input data to generate a model response
#     model_response = summarize(parsed_data)

#     # Define headers for the HTTP response to allow cross-origin requests
#     headers = {"Access-Control-Allow-Origin": "*"}

#     # Return the model response, HTTP status code 200 (OK), and the headers
#     return (model_response, 200, headers)


import functions_framework  # Import the functions_framework library for HTTP functions
from google.cloud import vision, storage  # Import the vision and storage libraries from Google Cloud
import vertexai  # Import the vertexai library for AI model handling
from vertexai.preview.language_models import TextGenerationModel  # Import the TextGenerationModel from vertexai
import json  # Import the JSON library for working with JSON data
from flask import Flask, request, jsonify  # Import Flask libraries for handling HTTP requests and responses
from flask_cors import CORS  # Import CORS for handling cross-origin requests

app = Flask(__name__)
CORS(app)

# Replace with your project ID
PROJECT_ID = ""

# Initialize the GCP clients
vision_client = vision.ImageAnnotatorClient()
storage_client = storage.Client()

def analyze_image(gcs_uri):
    """Analyze an image using the Google Cloud Vision API."""
    image = vision.Image()
    image.source.image_uri = gcs_uri

    response = vision_client.label_detection(image=image)
    labels = [label.description for label in response.label_annotations]
    return labels

def generate_reactions(labels):
    """Generate reactions based on the detected labels using Vertex AI."""
    parameters = {
        "temperature": 0.2,          # Control the randomness of the generated text
        "max_output_tokens": 256,    # Limit the maximum number of output tokens
        "top_p": 0.8,                # Set a nucleus sampling threshold
        "top_k": 40,                 # Set a top-k sampling threshold
    }

    # Initialize the Vertex AI project with the provided project ID
    vertexai.init(project=PROJECT_ID)

    # Load the pre-trained TextGenerationModel named "text-bison@001"
    model = TextGenerationModel.from_pretrained("text-bison@001")

    # Generate a response by providing the input text and model parameters
    prompt = f"Possible reactions between {', '.join(labels)}, if no reactions are possible explain the physical phenomenon that these objects are able of performing, and if not that explain their structure and architecture "
    response = model.predict(
        prompt,  # Format the input text
        **parameters,  # Pass the defined parameters
    )

    # Return the generated response as text
    return response.text

@app.route('/upload', methods=['POST'])
def upload_image():
    """Upload an image to Google Cloud Storage."""
    file = request.files['file']
    if file:
        bucket_name = "your-bucket" #'visionlab_bucket'
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(file.filename)
        blob.upload_from_file(file)

        gcs_uri = f"gs://{bucket_name}/{file.filename}"
        return jsonify({'message': 'Image uploaded successfully', 'gcs_uri': gcs_uri}), 200
    return jsonify({'message': 'No file uploaded'}), 400

@app.route('/analyze', methods=['POST'])
def analyze():
    """Analyze the uploaded image."""
    gcs_uri = request.json['gcs_uri']
    labels = analyze_image(gcs_uri)
    return jsonify({'labels': labels}), 200

@app.route('/generate', methods=['POST'])
def generate():
    """Generate reactions based on the detected labels."""
    labels = request.json['labels']
    reactions = generate_reactions(labels)
    return jsonify({'reactions': reactions}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
