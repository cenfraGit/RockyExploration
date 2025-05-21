import speech_recognition as sr
from faster_whisper import WhisperModel
import io

try:
    model = WhisperModel("tiny.en", device="cpu", compute_type="int8")
    print("Model loaded.")
except Exception as e:
    print(e)

r = sr.Recognizer()

def transcribe_audio_data(audio_data: sr.AudioData):
    wav_file = io.BytesIO(audio_data.get_wav_data())
    segments, info = model.transcribe(wav_file, beam_size=3, language="en") 
    full_text = ""
    for segment in segments:
        full_text += segment.text
    return full_text.strip()

with sr.Microphone() as source:

    print("Adjusting for ambient noise...")
    r.adjust_for_ambient_noise(source, duration=1)

    while True:
        try:

            print("Listening...")

            audio = r.listen(source, timeout=None, phrase_time_limit=2)
            transcribed_text = transcribe_audio_data(audio)

            if transcribed_text:
                print(f"You said: \"{transcribed_text}\"")

        except sr.WaitTimeoutError:
            continue
        except sr.UnknownValueError:
            pass
        except Exception as e:
            print(e)
            break