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

class Cryostat:
    
    def __init__(self, ip: str, port: int=23) -> None:
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

    def get_data(self, command: str) -> dict[str, float]:
        self.socket.send(f"{command}\r\n".encode('ascii'))
        return self.socket.recv(1024).decode('ascii')

    @property
    def fr(self):
        res =  self.get_data("RR925?")
        if res == "?RR925":
            return None
        else:
            return float(res[7:])
        
    @property
    def still(self):
        res =  self.get_data("RR931?")
        if res == "?RR931":
            return None
        else:
            return float(res[7:])
        
    @property
    def stage2(self):
        res =  self.get_data("RR933?")
        if res == "?RR933":
            return None
        else:
            return float(res[7:])
        
    @property
    def stage1(self):
        res =  self.get_data("RR935?")
        if res == "?RR935":
            return None
        else:
            return float(res[7:])

