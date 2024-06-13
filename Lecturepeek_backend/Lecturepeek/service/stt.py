from pytube import YouTube
from pydub import AudioSegment
from pydub.silence import split_on_silence
from dotenv import load_dotenv
from google.cloud import storage
from google.cloud import speech
import os
import time
import datetime
from googleapiclient.discovery import build
import re
import concurrent.futures

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")


# Step 1: Download audio from YouTube
def download_audio_from_youtube(youtube_url, output_file):
    """
    Downloads audio from a YouTube video and converts it to a specified format.

    Args:
    youtube_url (str): URL of the YouTube video.
    output_file (str): Path to save the extracted audio file.

    Returns:
    int: Number of audio channels in the downloaded file.
    """
    start_time = time.time()  # 시작 시간 기록
    # Create a YouTube object using the provided URL
    yt = YouTube(youtube_url)

    # Filter streams to get only audio and select the first stream available
    stream = yt.streams.filter(only_audio=True).first()

    # Download the audio stream to a temporary file
    stream.download(filename='temp_audio')

    # Use pydub to convert the downloaded audio file to the desired format (FLAC)
    audio = AudioSegment.from_file('temp_audio')
    audio.export(output_file, format='flac')

    # Get the number of channels in the audio file
    channels = audio.channels

    # Remove the temporary file as it is no longer needed
    os.remove('temp_audio')

    end_time = time.time()  # 종료 시간 기록
    elapsed_time = end_time - start_time  # 소요 시간 계산

    print(f"오디오가 {output_file}로 저장되었습니다.")
    print(f"실행 시간: {elapsed_time:.2f}초")
    print(f"Downloaded and converted audio to {output_file} with {channels} channels")

    return channels


# Step 2: Upload audio file to Google Cloud Storage
def upload_to_gcs(bucket_name, source_file_name, destination_blob_name):
    """
    Uploads a file to a specified Google Cloud Storage bucket.

    Args:
    bucket_name (str): The name of the GCS bucket.
    source_file_name (str): Path to the local file to upload.
    destination_blob_name (str): The destination path in the GCS bucket.

    Returns:
    None
    """
    # Initialize a GCS client
    storage_client = storage.Client()

    # Get the bucket object from the specified bucket name
    bucket = storage_client.bucket(bucket_name)

    # Create a blob object for the destination path in the bucket
    blob = bucket.blob(destination_blob_name)

    # Upload the local file to the blob
    blob.upload_from_filename(source_file_name)
    print(f"File {source_file_name} uploaded to {destination_blob_name}.")


# Step 3: Transcribe audio file using Google Cloud Speech-to-Text
def transcribe_gcs(gcs_uri, channels, language_code):
    """
    Transcribes an audio file stored in Google Cloud Storage using Google Cloud Speech-to-Text API.

    Args:
    gcs_uri (str): The GCS URI of the audio file.
    channels (int): Number of audio channels.

    Returns:
    None
    """
    # Initialize a Speech-to-Text client
    client = speech.SpeechClient()

    first_language = language_code
    alternate_languages_list = ["en", "es", "hi"]
    # Configure the audio file with the GCS URI
    audio = speech.RecognitionAudio(uri=gcs_uri)

    # Set up the recognition configuration, specifying the audio encoding, sample rate, and language
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.FLAC,
        sample_rate_hertz=44100,
        language_code=first_language,
        alternative_language_codes=alternate_languages_list,
        audio_channel_count=channels,  # Set the number of audio channels
        enable_word_time_offsets=True,
        enable_automatic_punctuation=True,
    )

    start_time = time.time()
    # Initiate a long-running recognize operation
    operation = client.long_running_recognize(config=config, audio=audio)
    print("Waiting for operation to complete...")

    # Wait for the operation to complete, with a timeout of 10 minutes
    response = operation.result(timeout=3600)
    end_time = time.time()
    elapsed_time = end_time - start_time

    transcription_text = ""
    temp_text = ""
    print(f"stt 실행 시간: {elapsed_time:.2f}초")
    lt = time.localtime(start_time)
    today = time.strftime("%m-%d-%H-%M-%S", lt)
    filename = f"transcriptions{today}.txt"
    # Open a file to save the transcription results
    for result in response.results:
        # Write each transcript alternative to the file
        temp_text += result.alternatives[0].transcript + '\n'
    print(f"temp_text : {temp_text}")

    with open(filename, 'w') as f:
        for result in response.results:
            alternative = result.alternatives[0]
            if alternative.words:
                # 첫 단어의 시작 시간을 포함한 스크립트 추출하기
                start_time = alternative.words[0].start_time
                start_time_seconds = start_time.seconds + start_time.microseconds / 1e6
                start_time_formatted = str(datetime.timedelta(seconds=start_time_seconds)).split(".")[0]
                line = f"{start_time_formatted} : {alternative.transcript}\n"
                f.write(line)
                transcription_text += line

    print("Transcription with timestamps saved to transcription.txt")
    print(transcription_text)
    return transcription_text


# 링크를 받아 stt -> 스크립트 처리 수행함수
def speech_to_text(url):
    # Define the YouTube URL to download audio from
    input_youtube_url = url

    video_id = get_video_id(url)
    language = get_video_language(video_id)
    print(f"언어 코드 : {language}\n")

    # Define the local path to save the extracted audio file
    output_file = 'audio.flac'


    # Define the GCS bucket name and destination path for the audio file
    bucket_name = 'test-lecutrepeek'
    destination_blob_name = 'audio/audio.flac'

    # Download and convert the audio from YouTube
    channels = download_audio_from_youtube(input_youtube_url, output_file)

    # Upload the audio file to the specified GCS bucket
    upload_to_gcs(bucket_name, output_file, destination_blob_name)

    # Construct the GCS URI of the uploaded file
    gcs_uri = f'gs://{bucket_name}/{destination_blob_name}'

    # Transcribe the audio file using Google Cloud Speech-to-Text
    script = transcribe_gcs(gcs_uri, channels, language)
    return script


def get_video_language(video_id):
    api_service_name = "youtube"
    api_version = "v3"

    youtube = build(api_service_name, api_version, developerKey=api_key)

    request = youtube.videos().list(
        part="snippet",
        id=video_id
    )
    response = request.execute()

    if response["items"]:
        snippet = response["items"][0]["snippet"]
        language = snippet.get("defaultAudioLanguage", "Language info not available")
        return language
    else:
        return "Video not found"


def get_video_id(url):
    # 유튜브 URL에서 비디오 ID를 추출하는 정규 표현식
    regex = re.compile(r'(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})')
    match = regex.search(url)
    return match.group(1) if match else None
