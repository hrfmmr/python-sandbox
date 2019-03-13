import wave

import pyaudio

# ビット深度=int16(short)=65536段階で音階を表現
FORMAT = pyaudio.paInt16
# 1チャンネル=モノラル
CHANNELS = 1
# サンプリングレート(Hz)
RATE = 44100
# 1フレームの秒数
FRAME_SEC = 0.04
# 1フレームのbufferサイズ
CHUNK = int(RATE * FRAME_SEC)
RECORD_SECONDS = 10
WAVE_OUTPUT_FILENAME = "file.wav"


def main():
    audio = pyaudio.PyAudio()

    stream = audio.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        frames_per_buffer=CHUNK
    )
    print("recording...")

    frames = []
    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)
    print("finished recording")

    stream.stop_stream()
    stream.close()
    audio.terminate()

    waveFile = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    waveFile.setnchannels(CHANNELS)
    waveFile.setsampwidth(audio.get_sample_size(FORMAT))
    waveFile.setframerate(RATE)
    waveFile.writeframes(b''.join(frames))
    waveFile.close()


if __name__ == '__main__':
    main()
