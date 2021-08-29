import json
import subprocess

from vosk import Model, KaldiRecognizer, SetLogLevel
import os
import wave
import soundfile as sf
from bot.config import BASE_DIR
import requests

# model_path = BASE_DIR / 'model'
model_path = "/home/mark/PycharmProjects/atom/vosk_test/model"


def convert_ogg2wav(path_ogg, path_wav=None):
    data, samplerate = sf.read(path_ogg)
    if not path_wav:
        path_wav = path_ogg + '.wav'
    sf.write(path_wav, data, samplerate)
    return path_wav


def get_text(path_wav):
    SetLogLevel(0)

    if not os.path.exists(model_path):
        print("Идиот, забыл модель скачать блять. https://alphacephei.com/vosk/models/vosk-model-ru-0.10.zip")
        exit(1)

    wf = wave.open(path_wav, "rb")
    if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
        print("Audio file must be WAV format mono PCM.")
        exit(1)

    model = Model(model_path)
    rec = KaldiRecognizer(model, wf.getframerate())
    rec.SetWords(True)

    # all_text = ""
    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            partial_res = json.loads(rec.Result())
            # if 'text' in partial_res.keys():
            #     all_text += partial_res['text']
            # print(partial_res)
        else:
            json.loads(rec.PartialResult())
    final_result = json.loads(rec.FinalResult())
    # is_final = all_text + final_result['text']
    return final_result['text']


def ogg_to_wav(ogg_full_path, wav_full_path):
    print('start converting ogg to wav')
    command = ['ffmpeg', '-i', ogg_full_path, '-ac', '1', '-f', 'wav', wav_full_path]
    subprocess.run(command, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    print('conversion finished')


def convert_and_get_text(file_ogg) -> str:
    # file_wav = convert_ogg2wav(file_ogg)
    file_wav = file_ogg + ".wav"
    ogg_to_wav(file_ogg, file_wav)
    text = get_text(path_wav=file_wav)
    return text


def send_request(text):
    api_host = "http://10.91.54.226:8000"
    endpoint = "/api/task/"
    res = requests.post(api_host + endpoint, data={"description": text})
    data = res.json()
    if not 'description' in data.keys():
        print("че происходит. пришел стремный ответ от сервера")
        print(data)
    if data['description'].startswith("Choosing department model cannot confidently define department to choose for"):
        return "Не смогли найти подходящий департамент. Мы перенаправили запрос человеку на рассмотрение"
    # TODO add person that yes

