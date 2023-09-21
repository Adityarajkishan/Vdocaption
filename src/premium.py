import logging
import boto3
from botocore.exceptions import ClientError
import os
import json

def upload_file(file_name, bucket, object_name=None):

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = os.path.basename(file_name)

    # Upload the file
    try:
        s3_client = boto3.client('s3')
        response = s3_client.upload_file(file_name, bucket, object_name)
    except ClientError as e:
        logging.error(e)
        return error(e)

    return True

#Function to transcribe the video file
def transcribe_video(job_name, job_uri, output_bucket, language_code):
    settings = {
        "ChannelIdentification": False,
        "ShowSpeakerLabels": True,
        "MaxSpeakerLabels": 2
    }

    transcribe_client = boto3.client('transcribe')
    response = transcribe_client.start_transcription_job(
        TranscriptionJobName=job_name,
        LanguageCode=language_code,
        MediaFormat="mp4",
        Media={
            "MediaFileUri": job_uri
        },
        OutputBucketName=output_bucket,
        Settings=settings
    )

    while True:
        response = transcribe_client.get_transcription_job(
            TranscriptionJobName=job_name
        )
        status = response['TranscriptionJob']['TranscriptionJobStatus']
        if status in ['COMPLETED', 'FAILED']:
            break

    return True

def process_transcript(job_name:str,output_bucket:str, fileName: str,jsonpath: str, translate_code: str) -> str:
    s3 = boto3.client('s3')
    transcript = s3.get_object(Bucket=output_bucket, Key=f"{job_name}.json")
    transcript_body = transcript['Body'].read().decode('utf-8')
    transcript_body = json.loads(transcript_body)
    transcript_body = transcript_body['results']['transcripts'][0]['transcript']
    with open(fileName, 'w') as file:
        file.write(transcript_body)
    if translate_code != 'none':
        translate = boto3.client('translate')
        translatedoutput = translate.translate_text(Text=transcript_body, SourceLanguageCode="en", TargetLanguageCode=translate_code)
        transcript_body = translatedoutput['TranslatedText']
    return transcript_body