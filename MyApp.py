from flask import Flask, render_template, request
from azure.cognitiveservices.vision.customvision.prediction import CustomVisionPredictionClient
from msrest.authentication import ApiKeyCredentials
import tempfile
import os

app = Flask(__name__)

# Replace with your Custom Vision endpoint and prediction key
custom_vision_endpoint = "https://myfacereco.cognitiveservices.azure.com/"
prediction_key = "9111952c4b2c4468a25fcfe844c646f0"

# Replace with your Custom Vision project ID and iteration name
project_id = "263d1028-2552-4f21-87c8-9b2a46894ac6"
iteration_name = "Iteration 3"

# Define the tags used in your Custom Vision project
female_tag = "female"
male_tag = "male"

credentials = ApiKeyCredentials(in_headers={"Prediction-Key": prediction_key})
predictor = CustomVisionPredictionClient(endpoint=custom_vision_endpoint, credentials=credentials)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'file' not in request.files:
        return render_template('index.html', error='No file part')

    file = request.files['file']

    if file.filename == '':
        return render_template('index.html', error='No selected file')

    if file:
        # Save the file to a temporary location
        temp_filename = os.path.join(tempfile.gettempdir(), 'temp_image.jpg')
        file.save(temp_filename)

        # Send the image to the Custom Vision API for prediction
        with open(temp_filename, 'rb') as image_file:
            result = predictor.classify_image(project_id, iteration_name, image_file.read())

        # Debugging: print the result
        print(result.predictions)

        # Process the response
        predictions = result.predictions

        # Filter predictions for female and male tags
        female_predictions = [p for p in predictions if female_tag in p.tag_name]
        male_predictions = [p for p in predictions if male_tag in p.tag_name]

        # Find the most confident prediction for each tag
        most_confident_female = max(female_predictions, key=lambda x: x.probability, default=None)
        most_confident_male = max(male_predictions, key=lambda x: x.probability, default=None)

        # Remove the temporary file after processing
        os.remove(temp_filename)

        return render_template('result.html', 
                                most_confident_female=most_confident_female,
                                most_confident_male=most_confident_male)

if __name__ == '__main__':
    app.run(debug=False)




