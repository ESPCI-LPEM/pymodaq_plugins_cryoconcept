"""
Created the 20/03/2025

@author: Louis Grandvaux
"""

import re
import socket
import time

import numpy as np

from pymodaq_utils.logger import set_logger, get_module_name

logger = set_logger(get_module_name(__file__), add_to_console=False)

class MMR3:
    
    def __init__(self, ip: str, port: int) -> None:
        self.ip = ip
        self.port = port
        self.socket: socket.socket = None

    def connect(self) -> bool:
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.ip, self.port))
            return True
        except Exception as e:
            logger.error(f"Unable to connect to {self.ip}:{self.port}.\n{e}")
            return False
        
    def disconnect(self) -> None:
        if self.socket is not None:
            self.socket.close()

    def get_data(self) -> dict[str, float]:
        data = {}

        try:
            d = self.socket.recv(1024).decode('ascii')
            pattern: re.Pattern = re.compile(
                r"(\d+);-?(\d+);(\d+.\d+e[-\+]\d+)"
            )

            for match in pattern.finditer(d):
                if int(match.group(1)) == 3:
                    data["R1"] = float(match.group(3))
                if int(match.group(1)) == 14:
                    data["R2"] = float(match.group(3))
                if int(match.group(1)) == 25:
                    data["R3"] = float(match.group(3))
        except socket.error as e:
            logger.error(f"Communication problem with {self.ip}:{self.port}.\n{e}")
            data = None
        except Exception as e:
            logger.error(f"Unable to match data in received data.\n{d}\n{e}")
            data = None

        return data
