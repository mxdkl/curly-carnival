import os
import shutil
from dotenv import load_dotenv
import wget
from pydub import AudioSegment
import azure.cognitiveservices.speech as speechsdk

load_dotenv()


def recognize_text_from_audio(downloadUrl) -> str:
    absolute_path = os.path.dirname(__file__)
    shutil.rmtree('downloads')
    os.mkdir('downloads')
    downloadPath = absolute_path+"/downloads/"
    try:
        filePath = wget.download(url=downloadUrl, out=downloadPath)
    except Exception as e:
        print(f"\nCould not download file {downloadUrl}")
        print(e)

    newAudioPath = filePath.replace('.oga', '.wav')
    audioConvert = AudioSegment.from_file(filePath)
    try:
        audioConvert.export(newAudioPath, format='wav')
    except Exception as e:
        print(f"\nCould not convert the audio file {filePath}")
        print(e)

    speech_config = speechsdk.SpeechConfig(subscription=os.getenv(
        'SPEECH_KEY'), region=os.getenv('SPEECH_REGION'))
    speech_config.speech_recognition_language = "en-US"
    audio_config = speechsdk.audio.AudioConfig(filename=newAudioPath)
    speech_recognizer = speechsdk.SpeechRecognizer(
        speech_config=speech_config, audio_config=audio_config)

    speech_recognition_result = speech_recognizer.recognize_once_async().get()

    if speech_recognition_result.reason == speechsdk.ResultReason.RecognizedSpeech:
        print("\nRecognized: {}".format(speech_recognition_result.text))
        return speech_recognition_result.text
    elif speech_recognition_result.reason == speechsdk.ResultReason.NoMatch:
        print("No speech could be recognized: {}".format(
            speech_recognition_result.no_match_details))
    elif speech_recognition_result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = speech_recognition_result.cancellation_details
        print("Speech Recognition canceled: {}".format(
            cancellation_details.reason))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            print("Error details: {}".format(
                cancellation_details.error_details))
            print("Did you set the speech resource key and region values?")


""" 
url="https://do-media-7103.fra1.digitaloceanspaces.com/7103872531/7ccb69bf-ddda-4acd-bd7c-999a816997b7.oga"
recognize_text_from_audio(url)


def synthesize_audio_from_text(messageText) -> str:
    # This example requires environment variables named "SPEECH_KEY" and "SPEECH_REGION"
    speech_config = speechsdk.SpeechConfig(subscription=os.getenv('SPEECH_KEY'), region=os.getenv('SPEECH_REGION'))
    audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)

    # The language of the voice that speaks.
    speech_config.speech_synthesis_voice_name='en-US-BlueNeural'
    speech_config.set_speech_synthesis_output_format(speechsdk.SpeechSynthesisOutputFormat.Riff24Khz16BitMonoPcm)
    speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=None)

    result = speech_synthesizer.speak_text_async(messageText).get()
    
    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        print("Speech synthesized for text [{}]".format(messageText))
        stream = speechsdk.AudioDataStream(result)

        timestr = time.strftime("%Y%m%d-%H%M%S")
        filePath = "downloads/"+timestr+".wav"
        stream.save_to_wav_file(filePath)
        return filePath
    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = result.cancellation_details
        print("Speech synthesis canceled: {}".format(cancellation_details.reason))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            if cancellation_details.error_details:
                print("Error details: {}".format(cancellation_details.error_details))
                print("Did you set the speech resource key and region values?")

 """
