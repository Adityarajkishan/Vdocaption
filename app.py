import os, tempfile, datetime, time
from flask import Flask, request, render_template, jsonify, send_file
import boto3
from src.fileops import allowed_file, delete_file, delete_files_in_folder,upload_to_local_folder, create_object_id
from src.premium import upload_file, transcribe_video, process_transcript
from src.standard import extract_audio, speech_to_text, generate_timestamps
app = Flask(__name__)

#Declaration of required paths and variables
S3_BUCKET = 'storevdos' #TODO: Remove the secrets revealed
objectID = None
fileName = None
filePath = None
transcriptPath = 'transcripts'

#Other formalities

#Render pages
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact(): 
    return render_template('contact.html') 

@app.route('/gopremium')
def gopremium(): 
    return render_template('gopremium.html')

@app.route('/gostandard')
def gostandard(): 
    return render_template('gostandard.html')

#Upload video file 
@app.route('/upload', methods=['POST'])
def upload():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'})

        file = request.files['file']

        if file.filename == '':
            return jsonify({'error': 'No file selected.'})

        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Only .mp4 files are allowed.'})
        global fileName, filePath, objectID
        objectID = create_object_id()
        fileName = file.filename
        filePath = upload_to_local_folder(file,objectID, fileName)
        if (request.form.get('value') == 'premium'):
            return render_template('gopremium.html', results='Video uploaded successfully')
        else:
            return render_template('gostandard.html', results='Video uploaded successfully')
    
    except Exception as e:
        return jsonify({'error': str(e)})


@app.route('/premium', methods=['POST'])
def premium():
    s3_key = "videos/"+objectID+".mp4"
    upload_file(filePath,S3_BUCKET,s3_key)
    job_name = "transcribe-job-" + objectID
    job_uri = f"s3://{S3_BUCKET}/{s3_key}"
    output_bucket = S3_BUCKET
    language_code = "en-US"
    translate_code = request.form.get('language')

    try:
        _ = transcribe_video(job_name, job_uri, output_bucket, language_code)
        text = process_transcript(job_name, S3_BUCKET, f'{transcriptPath}/{fileName}.txt',f'{transcriptPath}/{fileName}.json', translate_code)

        return render_template('gopremium.html',results1="transcribed successfully and generated results", results2=text)

    except Exception as e:
        return jsonify({'error': str(e)})
        
    delete_files_in_folder('uploads')
    return render_template('gopremium.html',results1="transcription failed",results2="")

@app.route('/standard', methods=['POST'])
def standard():

    try:
        extract_audio(filePath, f'{filePath}_output.wav')
        text = speech_to_text(f'{filePath}_output.wav', f'{filePath}_output.txt')
        os.makedirs(transcriptPath, exist_ok=True)
        generate_timestamps(f'{filePath}_output.wav', f'{filePath}_output.txt', f'{transcriptPath}/{fileName}.txt')
        delete_files_in_folder('uploads')
    except Exception as e:
        return jsonify({'error': str(e)})

    return render_template('gostandard.html',results1="transcribed successfully and generated results", results2=text)


@app.route('/download', methods=['POST'])
def download_file():
    try:
        # Construct the file path
        file_name = f'{transcriptPath}/{fileName}.txt'
        file_path = os.path.join(app.root_path, file_name)

        # Check if the file exists
        if not os.path.exists(file_path):
            return jsonify({'error': 'File not found'})

        # Send the file to the user
        return send_file(file_path, as_attachment=True)
    except Exception as e:
        return jsonify({'error': str(e)})


#TODO: Add a route to download the transcript file
@app.route('/downloadjson', methods=['POST'])
def downloadjson():
    try:
        # Construct the file path
        file_name = f'{transcriptPath}/{fileName}.json'
        file_path = os.path.join(app.root_path, file_name)

        # Check if the file exists
        if not os.path.exists(file_path):
            return jsonify({'error': 'File not found'})

        # Send the file to the user
        return send_file(file_path, as_attachment=True)
    except Exception as e:
        return jsonify({'error': str(e)})


    
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080) 
