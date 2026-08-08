import subprocess
import itertools
import threading
import json
import queue
from composer import util

class RenderWorker:
    def __init__(self):
        self._process = subprocess.Popen(
            ['node', 'render-build.js'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        self._id_counter = itertools.count()

        self._pending_lock = threading.Lock()
        self._write_lock = threading.Lock()
        self._pending = dict()

        self._reader = threading.Thread(target=self._read, daemon=True)
        self._reader.start()

        self._err_reader = threading.Thread(target=self._err_read, daemon=True)
        self._err_reader.start()

    def _read(self):
        for line in self._process.stdout:
            line = line.strip()
            ret = None
            try:
                ret = json.loads(line)
            except json.JSONDecodeError:
                print(line)
                continue
            with self._pending_lock:
                q = self._pending.pop(ret['id'], None)
                q.put(ret['ret'])

    def _err_read(self):
        for line in self._process.stderr:
            print(line)

    def render(self, rite):
        request_id = next(self._id_counter)
        request = util.dump_data({'content':rite, 'id':request_id}) + '\n'
        q = queue.Queue(maxsize=1)
        with self._pending_lock:
            self._pending[request_id] = q

        with self._write_lock:
            self._process.stdin.write(request)
            self._process.stdin.flush()

        try:
            ret = q.get(timeout=10)
            return ret
        except queue.Empty:
            with self._pending_lock:
                self._pending.pop(request_id, None)
            raise TimeoutError()

    def close(self):
        self._process.stdin.close()
