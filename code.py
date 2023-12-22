from flask import Flask, render_template, request
from azure.cognitiveservices.vision.face import FaceClient
from msrest.authentication import CognitiveServicesCredentials

app = Flask(__name__)

# Replace with your own values
subscription_key = 'bfa547c2d1c840d1bcae51cd18a31d76'
face_api_endpoint = 'https://projetcloudinstance.cognitiveservices.azure.com/'

# Create a FaceClient with your endpoint and subscription key
face_client = FaceClient(face_api_endpoint, CognitiveServicesCredentials(subscription_key))

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
        file_path = 'temp_image.jpg'
        file.save(file_path)

        # Detect faces in the uploaded image
        detected_faces = face_client.face.detect_with_stream(open(file_path, 'rb'), detection_model='detection_03', return_face_attributes=['age', 'gender'])

        # Check if faces are detected
        if detected_faces:
            face_info = []
            for face in detected_faces:
                age = face.face_attributes.age
                gender = face.face_attributes.gender
                face_info.append({'age': age, 'gender': gender})
            
            return render_template('result.html', face_info=face_info, image_path=file_path)
        else:
            return render_template('index.html', error='No faces detected in the uploaded image')

if __name__ == '__main__':
    app.run(debug=True, port=5001)  # Change the port number if needed