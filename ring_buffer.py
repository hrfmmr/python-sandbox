import numpy as np


class ShortRingBuffer:
    DATA_TYPE = np.int16

    def __init__(self, capacity: int, frame_size: int) -> None:
        self.capacity = capacity
        self.frame_size = frame_size
        self.read_pos = 0
        self.write_pos = 0
        self.buffer = np.array([], dtype=self.__class__.DATA_TYPE)

    def write(self, buffer: bytes):
        arr = np.frombuffer(buffer, dtype=self.__class__.DATA_TYPE)
        self._write(arr)

    def _write(self, arr: np.ndarray):
        if len(arr) == 0:
            return
        if len(arr) < self.capacity - self.write_pos:
            # 全部今の位置から書き込める
            if not len(self.buffer) >= self.write_pos + len(arr):
                pad = (self.write_pos + len(arr)) - len(self.buffer)
                self.buffer = np.append(
                    self.buffer,
                    np.zeros(pad, dtype=self.__class__.DATA_TYPE)
                )
            self.buffer[self.write_pos:self.write_pos + len(arr)] = arr
            self.write_pos += len(arr)
        else:
            # 端まで書き込む
            to_cap_len = self.capacity - self.write_pos
            if not len(self.buffer) >= self.write_pos + to_cap_len:
                pad = (self.write_pos + to_cap_len) - len(self.buffer)
                self.buffer = np.append(
                    self.buffer,
                    np.zeros(pad, dtype=self.__class__.DATA_TYPE)
                )
            self.buffer[self.write_pos:self.write_pos + to_cap_len] = arr[:to_cap_len]

            # 先頭から残りを書き込む
            rest_len = len(arr) - to_cap_len
            if rest_len == 0:
                self.write_pos = self.capacity
                return
            rest_buf = arr[to_cap_len:to_cap_len + rest_len]
            if rest_len <= self.capacity:
                self.buffer[:rest_len] = rest_buf
                self.write_pos = rest_len
            else:
                # 端まで書き込んだのでcursorをリセット
                self.write_pos = 0
                self._write(rest_buf)

    def read(self) -> bytes:
        if not self.is_filled():
            raise BufferError('Does not have enough buffer to read...')
        if self.frame_size < self.capacity - self.read_pos:
            # 今の位置から全部読み込める
            ret = self.buffer[self.read_pos:self.read_pos + self.frame_size]
            self.read_pos += self.frame_size
            return ret.tobytes()
        else:
            # 端まで読み込む
            to_cap_len = self.capacity - self.read_pos
            to_cap_buf = self.buffer[self.read_pos:self.read_pos + to_cap_len]
            # 先頭から残りを読み込む
            rest_len = self.frame_size - to_cap_len
            rest_buf = self.buffer[:rest_len]
            ret = np.append(to_cap_buf, rest_buf)
            self.read_pos = rest_len
            return ret.tobytes()

    def read_rest(self) -> bytes:
        ret = np.zeros(self.frame_size, dtype=self.__class__.DATA_TYPE)
        if self.read_pos <= self.write_pos:
            rest_len = self.write_pos - self.read_pos
            ret[:rest_len] = self.buffer[
                    self.read_pos:
                    self.read_pos + rest_len]
        else:
            to_cap_len = self.capacity - self.read_pos
            ret[:to_cap_len] = self.buffer[
                    self.read_pos:
                    self.read_pos + to_cap_len]
            rest_len = self.write_pos
            ret[to_cap_len:to_cap_len + rest_len] = self.buffer[:rest_len]
        self.reset()
        return ret.tobytes()

    def is_filled(self):
        if self.read_pos <= self.write_pos:
            return self.write_pos - self.read_pos >= self.frame_size
        else:
            to_cap_len = self.capacity - self.read_pos
            return to_cap_len + self.write_pos >= self.frame_size

    def reset(self):
        self.read_pos = 0
        self.write_pos = 0
