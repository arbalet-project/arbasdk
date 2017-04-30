"""
    Arbalet - ARduino-BAsed LEd Table
    HTTPLink - Provide a HTTP access to the display matrices for HTTP clients
    
    Copyright 2017 Yoan Mollard - Arbalet project - http://github.com/arbalet-project
    License: GPL version 3 http://www.gnu.org/licenses/gpl.html
"""
from __future__ import print_function  # py2 stderr
from .abstract import AbstractDisplayDevice
from bottle import Bottle, response, request
from threading import Thread
from struct import pack


__all__ = ['HTTPDisplayServer']


class HTTPDisplayServer(AbstractDisplayDevice):
    def __init__(self, host, hardware_config, diminution=1):
        super(HTTPDisplayServer, self).__init__(host, hardware_config, diminution)
        self.bottle = Bottle()
        self.connected = False
        self.port = self.config['port']
        self.num_pixels = len(self.config['mapping'])*len(self.config['mapping'][0])
        self.size_frame = self.num_pixels * 3 
        self.frame = [0] * self.size_frame   # A frame is on the form: [R, G, B, R, G, B, ...]
        self.route()

    def route(self):
        self.bottle.route('/pixels/binary', method='GET', callback=self.get_pixels_bin)

    def is_connected(self):
        return self.connected

    def allow_cors(func):
        def wrapper(*args, **kwargs):
            response.headers['Access-Control-Allow-Origin'] = '*'
            return func(*args, **kwargs)
        return wrapper

    @allow_cors
    def get_pixels_bin(self):
        return pack("!{}B".format(self.size_frame), *self.frame)

    def connect(self):
        def serve():
            self.connected = True
            self.bottle.run(host='127.0.0.1', port=self.port)
        #serve()
        server = Thread(target=serve)
        server.daemon = True
        server.start()

    def get_touch_events(self):
        return []

    @staticmethod
    def to_8b(float):
        return min(255, max(1, int(float*255)))   # 0 is forbidden this is considered the end of the packet by e:cue

    def write_led_frame(self, end_model):
        model_frame = end_model.data_frame
        int_frame = [1]*self.size_frame
        for h in range(end_model.get_height()):
            for w in range(end_model.get_width()):
                index = self.map_pixel_to_led(h, w)
                if index > 0:
                    index = index -1 # -1 because DMX starts at address 1
                    pixel = map(self.to_8b, end_model.get_pixel(h, w))
                    int_frame[index*3] = pixel[0]
                    int_frame[index*3+1] = pixel[1]
                    int_frame[index*3+2] = pixel[2]
        self.frame = int_frame

