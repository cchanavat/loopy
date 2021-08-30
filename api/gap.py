from os.path import getsize
from os import chdir

from time import sleep
from subprocess import Popen, PIPE, call
from shlex import split as shlex_split

from numpy import savetxt, array

from loopapy.loop import Loop
from loopapy.setup import THIS_DIR


class ScreenAPI:
    def __init__(self, session_name: str):
        self.session_name = session_name
        self.sleep_time = 0.005
        self.log_delay = 0.05
        self.log_filename = f"logs/{self.session_name}.log"
        self.max_command_len = 100
        chdir(THIS_DIR)

    @staticmethod
    def screen_list():
        p = Popen("screen -ls", shell=True, stdout=PIPE, stderr=PIPE)
        return p.communicate()[0].decode('utf-8')

    def kill(self):
        call(shlex_split(f'./screen.sh kill {self.session_name}'))
        sleep(self.sleep_time)

    def send(self, command: str):
        n = self.max_command_len
        N = len(command)
        nb_command = N // n
        commands = []
        for i in range(nb_command):
            commands.append(command[i * n:(i + 1) * n])
        commands.append(command[nb_command * n:])

        for partial in commands:
            call(shlex_split(f"./screen.sh send {self.session_name} '{partial}'"))
            sleep(self.sleep_time)

        call(shlex_split(f"./screen.sh send {self.session_name} '^M'"))
        sleep(self.sleep_time)

    def reset_logs(self):
        f = open(self.log_filename, "w")
        f.write("")
        f.close()

    def logs(self):
        call(shlex_split(f"./screen.sh logs {self.session_name}"))
        self._wait()
        f = open(self.log_filename, 'r+')
        s = f.readlines()
        f.close()
        return s

    def _wait(self):
        size = getsize(self.log_filename)
        while True:
            sleep(self.log_delay)
            new_size = getsize(self.log_filename)
            if new_size == size:
                return
            size = new_size


class GAPy(ScreenAPI):
    def __init__(self, session_name: str, start_gap=False):
        super().__init__(session_name)
        if start_gap:
            self.start_gap()

    def start_gap(self):
        self.send("gap")
        self.wait_gap()

    def is_gap_done(self):
        logs = self.logs()
        if len(logs) >= 1:
            last = logs[-1]
            return last[:4] == "gap>" and ";" not in last
        return False

    def wait_gap(self):
        sleep(1)
        while not self.is_gap_done():
            continue

    def last_result(self, wait_gap=True):
        if wait_gap:
            self.wait_gap()
        elif not self.is_gap_done():
            return None

        logs = self.logs()
        result = []
        for line in reversed(logs[:-1]):
            if line[:4] == "gap>":
                break
            result.append(line)
        return result

    def send_group(self, var_name: str, loop: Loop, optional_id: str = None):
        self.send_loop(var_name, loop, optional_id)
        self.send(f'{var_name}:=AsGroup({var_name});')

    def send_loop(self, var_name: str, loop: Loop, optional_id: str = None):
        """
            set a unique optional_id when working with for loops with Python and GAP working in parallel
        """
        if optional_id is None:
            optional_id = ""

        fname = f"{THIS_DIR}temp/send{optional_id}.loop"
        table = loop.tmul + 1
        savetxt(f"{fname}", table, fmt="%i")
        self.send(f'{var_name}:=LoopFromFile("{fname}", " ");')

    def read(self, script_name: str, script_path: str = None):
        if script_path is None:
            script_path = THIS_DIR + "scripts/"
        self.send(f'Read("{script_path}{script_name}");')

    def send_as_array(self, var_name: str, arr: list):
        s = ",".join(arr)
        self.send(f"{var_name} := [{s}];")
