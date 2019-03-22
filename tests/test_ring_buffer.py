import logging

import numpy as np
import pytest

from ring_buffer import ShortRingBuffer

logging.basicConfig(
    level=logging.DEBUG,
    format="[%(levelname)s](%(process)s-%(threadName)s) @%(asctime)s"
           " - %(name)s.%(filename)s#%(funcName)s():L%(lineno)s"
           " - %(message)s"
)


class TestShortRingBuffer:

    @pytest.mark.parametrize('capacity,frame_size,pcm,expected', [
        (
            5,
            1,
            np.arange(3, dtype=ShortRingBuffer.DATA_TYPE),
            dict(
                write_pos=3,
                buffer=np.array([0, 1, 2], dtype=ShortRingBuffer.DATA_TYPE),
            ),
        ),
        (
            5,
            1,
            np.arange(7, dtype=ShortRingBuffer.DATA_TYPE),
            dict(
                write_pos=2,
                buffer=np.array([5, 6, 2, 3, 4], dtype=ShortRingBuffer.DATA_TYPE)
            ),
        ),
        (
            5,
            1,
            np.arange(12, dtype=ShortRingBuffer.DATA_TYPE),
            dict(
                write_pos=2,
                buffer=np.array([10, 11, 7, 8, 9], dtype=ShortRingBuffer.DATA_TYPE)
            ),
        ),
        (
            5,
            1,
            np.arange(15, dtype=ShortRingBuffer.DATA_TYPE),
            dict(
                write_pos=5,
                buffer=np.array([10, 11, 12, 13, 14], dtype=ShortRingBuffer.DATA_TYPE)
            ),
        ),
    ])
    def test_write(
            self,
            capacity,
            frame_size,
            pcm,
            expected
    ):
        ring_buf = ShortRingBuffer(capacity, frame_size)

        ring_buf.write(pcm.tobytes())

        logging.debug(ring_buf.__dict__)
        logging.debug(f'ring_buf.buffer:{ring_buf.buffer} len:{len(ring_buf.buffer)}')

        assert ring_buf.write_pos == expected['write_pos']
        assert (ring_buf.buffer == expected['buffer']).all()

    def test_read(self):
        capacity = 5
        frame_size = 2
        ring_buf = ShortRingBuffer(capacity, frame_size)

        pcm = np.array([1, 2, 3, 4, 5], dtype=ShortRingBuffer.DATA_TYPE)
        ring_buf.write(pcm.tobytes())

        read_buf = ring_buf.read()
        assert read_buf == np.array([1, 2], dtype=ShortRingBuffer.DATA_TYPE).tobytes()
        read_buf = ring_buf.read()
        assert read_buf == np.array([3, 4], dtype=ShortRingBuffer.DATA_TYPE).tobytes()

        pcm = np.array([6], dtype=ShortRingBuffer.DATA_TYPE)
        ring_buf.write(pcm.tobytes())

        read_buf = ring_buf.read()
        assert read_buf == np.array([5, 6], dtype=ShortRingBuffer.DATA_TYPE).tobytes()

        with pytest.raises(BufferError):
            ring_buf.is_filled = lambda: False
            ring_buf.read()

    def test_read_rest(self):
        capacity = 5
        frame_size = 2
        ring_buf = ShortRingBuffer(capacity, frame_size)

        def _write(arr):
            pcm = np.array(arr, dtype=ShortRingBuffer.DATA_TYPE)
            ring_buf.write(pcm.tobytes())

        _write([1])
        rest_buf = ring_buf.read_rest()
        assert rest_buf == np.array([1, 0], dtype=ShortRingBuffer.DATA_TYPE).tobytes()

    def test_is_filled(self):
        capacity = 6
        frame_size = 2
        ring_buf = ShortRingBuffer(capacity, frame_size)

        def _write(arr):
            pcm = np.array(arr, dtype=ShortRingBuffer.DATA_TYPE)
            ring_buf.write(pcm.tobytes())

        assert not ring_buf.is_filled()
        _write([1, 2, 3, 4, 5, 6])
        ring_buf.read()
        ring_buf.read()
        ring_buf.read()
        assert not ring_buf.is_filled()
        _write([7])
        assert not ring_buf.is_filled()
        _write([8])
        assert ring_buf.is_filled()
