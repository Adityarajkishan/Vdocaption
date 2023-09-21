from moviepy.editor import VideoFileClip
from google.cloud import speech_v1p1beta1 as speech
import speech_recognition as sr
import librosa
from datetime import datetime
from pathlib import Path


def extract_audio(video_path, audio_path):
    video = VideoFileClip(video_path)
    video.audio.write_audiofile(audio_path)

def speech_to_text(audio_path, output_path):
    r = sr.Recognizer()

    with sr.AudioFile(audio_path) as source:
        audio = r.record(source)  # Read the entire audio file

    try:
        text = r.recognize_google(audio)
        print("Transcript: {}".format(text))

        # Save the transcript as a text file
        with open(output_path, "w") as file:
            file.write(text)
        print("Transcript saved as: {}".format(output_path))
        return text
    except sr.UnknownValueError:
        print("Speech recognition could not understand audio")
    except sr.RequestError as e:
        print(
            "Could not request results from Google Speech Recognition service; {0}".format(e))

def generate_timestamps(audio_path, transcript_path,output_path):
    audio, sr = librosa.load(audio_path)

    with open(transcript_path) as f:
        transcript = f.read()

    lines = transcript.split(".")

    timestamps = []
    current_time = 0

    for line in lines:
        line = line.strip()

        if line:
            words = line.split()

            for word in words:
                audio_word = librosa.samples_to_time(
                    len(audio)) / len(transcript.split())
                word_duration = len(word.split()) * audio_word
                current_time += word_duration

            if not timestamps:
                timestamp = "00:00:00"
            else:
                timestamp = datetime.utcfromtimestamp(
                    current_time).strftime("%H:%M:%S")

            timestamps.append(f"{timestamp} - {line}")

    # Adjust the last line timestamp if it exceeds the audio duration
    audio_duration = librosa.get_duration(y=audio, sr=sr)
    last_timestamp = datetime.utcfromtimestamp(
        min(current_time, audio_duration)).strftime("%H:%M:%S")
    timestamps[-1] = timestamps[-1].replace(timestamp, last_timestamp)

    timestamps_text = "\n".join(timestamps)

    with open(output_path, 'a') as file:
        file.write(timestamps_text)

    print("Timestamps generated and saved as timestamps.txt")


# Specify the path to your transcript text file
transcript_path = "transcript.txt"


def translate_transcript(transcript_path, target_language):
    # Read the transcript file
    with open(transcript_path, 'r') as file:
        transcript = file.read()

    # Translate the transcript to the target language
    translator = Translator(to_lang=target_language)
    translated_text = translator.translate(transcript)

    # Save the translated transcript to a file
    translated_path = f"translated_{target_language}.txt"
    with open(translated_path, 'w') as file:
        file.write(translated_text)

    print(
        f"Transcript translated to {target_language} and saved to {translated_path}.")


# Example usage
transcript_path = "transcript.txt"
target_language = "fr"
