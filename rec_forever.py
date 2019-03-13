import asyncio
import logging
from queue import Queue
from threading import Thread
import time
import wave

import pyaudio

# ビット深度
FORMAT = pyaudio.paInt16
# 1チャンネル=モノラル
CHANNELS = 1
# サンプリングレート(Hz)
RATE = 44100
# 1フレームの秒数
FRAME_SEC = 0.04
# 1フレームのbufferサイズ
CHUNK = int(RATE * FRAME_SEC)

logging.basicConfig(
    level=logging.DEBUG,
    format='[%(levelname)s] (%(threadName)-10s) %(message)s',
)


class Recorder:
    def __init__(self):
        self.q = Queue()
        self._audio = pyaudio.PyAudio()
        self._stream = None

    def start_rec(self):
        logging.debug('start_rec')
        self._stream = self._audio.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK,
            stream_callback=self.callback
        )
        logging.debug("recording...")
        th = Thread(
            name='Handler',
            target=self.handle_buf,
            args=(self.q,)
        )
        th.start()
        th.join()
        self._stream.close()
        self._audio.terminate()

    def stop_rec(self):
        logging.debug('stop_rec')
        if self._stream:
            self._stream.stop_stream()

    def callback(
            self,
            in_data,
            frame_count,
            time_info,
            status
    ):
        logging.debug(f'in_data len:{len(in_data)} type:{type(in_data)}')
        self.q.put(in_data)
        return None, pyaudio.paContinue

    def handle_buf(self, q: Queue):
        logging.debug(f'start handle_buf')

        async def coro():
            while self._stream.is_active():
                buf = q.get()
                await asyncio.sleep(0.3)
                logging.debug(f'dequeued buf:{len(buf)}')

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(coro())


if __name__ == '__main__':
    recorder = Recorder()
    try:
        recorder.start_rec()
    except KeyboardInterrupt:
        recorder.stop_rec()
