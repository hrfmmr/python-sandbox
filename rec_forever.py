import asyncio
import logging
from queue import Queue
from threading import Thread

import numpy as np
import pyaudio

from logger import setup_logger
from ring_buffer import ShortRingBuffer

# ビット深度
FORMAT = pyaudio.paInt16
# 1チャンネル=モノラル
CHANNELS = 1
# サンプリングレート(Hz)
RATE = 16_000
# 1フレームの秒数
FRAME_SEC = 0.04
# 1フレームのbufferサイズ
CHUNK = int(RATE * FRAME_SEC)

setup_logger('logging.conf.yml')
logger = logging.getLogger(__name__)


class Recorder:
    def __init__(self):
        self.buf_input_queue = Queue()
        self.buf_output_queue = Queue()
        self._audio = pyaudio.PyAudio()
        self._stream = None
        self._ring_buf = ShortRingBuffer(capacity=CHUNK * 20, frame_size=CHUNK*4)

    def start_rec(self):
        logger.debug('start_rec')
        self._stream = self._audio.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK,
            stream_callback=self.callback
        )
        logger.debug("recording...")
        threads = (
            Thread(
                name='Buffering',
                target=self.buffering,
            ),
            Thread(
                name='HandleReadBuf',
                target=self.handle_read_buf,
            ),
        )
        for th in threads:
            th.start()

    def stop_rec(self):
        logger.debug('stop_rec')
        if self._stream:
            self._stream.stop_stream()

    def callback(
            self,
            in_data,
            frame_count,
            time_info,
            status
    ):
        logger.debug(f'in_data len:{len(in_data)} type:{type(in_data)}')
        self.buf_input_queue.put(in_data)
        return None, pyaudio.paContinue

    def buffering(self):
        while True:
            buf = self.buf_input_queue.get()
            logger.debug(f'👇 write buf:{buf[:10]}({len(buf)})')
            self._ring_buf.write(buf)
            while self._ring_buf.is_filled():
                buf = self._ring_buf.read()
                logger.debug(f'👆 read buf:{buf[:10]}({len(buf)})')
                self.buf_output_queue.put(buf)

    def handle_read_buf(self):
        async def coro():
            while self._stream.is_active():
                buf = self.buf_output_queue.get()
                logger.debug(f'🙌 fetched buffer buf:{buf[:10]}({len(buf)})')
                #  int16arr = np.frombuffer(buf, dtype=np.int16)

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(coro())


if __name__ == '__main__':
    recorder = Recorder()
    try:
        recorder.start_rec()
    except KeyboardInterrupt:
        recorder.stop_rec()
