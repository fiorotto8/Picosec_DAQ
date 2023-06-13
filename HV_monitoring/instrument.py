import serial


class Instrument:
    def __init__(
        self,
        port,
        baud=9600,
        parity=serial.PARITY_NONE,
        xonxoff=True,
        endl="\r\n",
        timeout=1,
    ):
        self.ser = serial.Serial(port, baud, parity=parity)
        self.ser.xonxoff = xonxoff
        self.ser.timeout = timeout
        self.endl = endl

    def write(self, command):
        self.ser.write(command.encode())

    def read(self):
        result = self.ser.read_until(self.endl)
        return result.decode()

    def get_settings(self):
        return self.ser.get_settings()
