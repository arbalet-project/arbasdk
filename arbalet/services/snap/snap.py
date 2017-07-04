#!/usr/bin/env python
"""
    Arbalet - ARduino-BAsed LEd Table
    Bridge for the Snap! visual programming language

    Provides a visual programming language to Arbalet for children or beginners

    Copyright 2015 Yoan Mollard - Arbalet project - http://github.com/arbalet-project
    License: GPL version 3 http://www.gnu.org/licenses/gpl.html
"""
from flask import Flask
from flask import request
from flask_cors import CORS
from arbalet.application import Application
from webbrowser import open


class SnapServer(Application):
    def __init__(self, port, **kwargs):
        super(SnapServer, self).__init__(**kwargs)
        self.flask = Flask(__name__)
        CORS(self.flask)
        self.authorized_nick = {}
        self.port = int(port)
        self.route()


    def route(self):
        # self.flask.route('/set_pixel/<h>/<w>/<color>', methods=['GET'])(self.set_pixel)
        # self.flask.route('/erase_all', methods=['GET'])(self.erase_all)
        self.flask.route('/set_pixel_rgb', methods=['POST'])(self.set_pixel_rgb)
        self.flask.route('/is_authorized/<nickname>', methods=['GET'])(self.is_authorized)
        self.flask.route('/authorize', methods=['POST'])(self.authorize)

    # def set_pixel(self, h, w, color):
    #     self.model.set_pixel(int(h)-1, int(w)-1, color)
    #     return ''

    # def erase_all(self):
    #     self.model.set_all('black')
    #     return ''

    def set_pixel_rgb(self):
        def scale(v):
            return min(1., max(0., float(v)/255.))
        data = request.get_data().split(':')
        self.model.set_pixel(int(data[0])-1, int(data[1])-1, map(scale, data[2:]))
        return ''

    def is_authorized(self, nickname):
        if not nickname in self.authorized_nick.keys():
            self.authorized_nick[nickname] = False
        return str(self.authorized_nick[nickname])

    def authorize(self):
        # first revock authorization of other participants
        for key in self.authorized_nick.keys():
            self.authorized_nick[key] = False
        # then authorize given nickname
        self.authorized_nick[request.get_data()] = True
        return ''

    def run(self):
        # open('http://snap.berkeley.edu/run')
        self.flask.run(host='0.0.0.0', port=self.port)

