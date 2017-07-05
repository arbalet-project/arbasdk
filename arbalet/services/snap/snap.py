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
from numpy.random import randint
from threading import Lock
import sys


class SnapServer(Application):
    def __init__(self, port, **kwargs):
        super(SnapServer, self).__init__(**kwargs)
        self.flask = Flask(__name__)
        CORS(self.flask)

        self.nicknames = []
        self.authorized_nick = {}
        self.nicknames_lock = Lock()
        self.init_nicknames()

        self.port = int(port)
        self.route()

    def init_nicknames(self):
        self.nicknames = ['Apple', 'Apricot', 'Avocado', 'Banana', 'Bilberry', 'Blackberry', 'Blackcurrant',
                          'Blueberry', 'Boysenberry', 'Currant', 'Cherry', 'Cherimoya', 'Cloudberry', 'Coconut',
                          'Cranberry', 'Cucumber', 'Custard apple', 'Damson', 'Date', 'Dragonfruit', 'Durian',
                          'Elderberry', 'Feijoa', 'Fig', 'Goji berry', 'Gooseberry', 'Grape', 'Raisin',
                          'Grapefruit', 'Guava', 'Honeyberry', 'Huckleberry', 'Jabuticaba', 'Jackfruit',
                          'Jambul', 'Jujube', 'Juniper berry', 'Kiwifruit', 'Kumquat', 'Lemon', 'Lime',
                          'Loquat', 'Longan', 'Lychee', 'Mango', 'Marionberry', 'Melon', 'Cantaloupe',
                          'Honeydew', 'Watermelon', 'Miracle fruit', 'Mulberry', 'Nectarine', 'Nance',
                          'Olive', 'Orange', 'Blood orange', 'Clementine', 'Mandarine', 'Tangerine',
                          'Papaya', 'Passionfruit', 'Peach', 'Pear', 'Persimmon', 'Physalis', 'Plantain',
                          'Plum', 'Prune', 'Pineapple', 'Plumcot', 'Pomegranate', 'Pomelo', 'Purple mangosteen',
                          'Quince', 'Raspberry', 'Salmonberry', 'Rambutan', 'Redcurrant', 'Salal berry', 'Salak',
                          'Satsuma', 'Soursop', 'Star fruit', 'Solanum quitoense', 'Strawberry', 'Tamarillo',
                          'Tamarind', 'Ugli fruit', 'Yuzu']

    def route(self):
        # self.flask.route('/set_pixel/<h>/<w>/<color>', methods=['GET'])(self.set_pixel)
        # self.flask.route('/erase_all', methods=['GET'])(self.erase_all)
        self.flask.route('/set_pixel_rgb', methods=['POST'])(self.set_pixel_rgb)
        self.flask.route('/is_authorized/<nickname>', methods=['GET'])(self.is_authorized)
        self.flask.route('/authorize', methods=['POST'])(self.authorize)
        self.flask.route('/get_nickname', methods=['GET'])(self.get_nickname)

    # def set_pixel(self, h, w, color):
    #     self.model.set_pixel(int(h)-1, int(w)-1, color)
    #     return ''

    # def erase_all(self):
    #     self.model.set_all('black')
    #     return ''

    def set_pixel_rgb(self):
        def scale(v):
            return min(1., max(0., float(v)/255.))
        try:
            data = request.get_data().split(':')
            if self.authorized_nick[data[-1]]:
                self.model.set_pixel(int(data[0])-1, int(data[1])-1, map(scale, data[2:-1]))
        except Exception:
            sys.exc_clear()
        return ''

    def is_authorized(self, nickname):
        with self.nicknames_lock:
            if not nickname in self.authorized_nick.keys():
                self.authorized_nick[nickname] = False
        return str(self.authorized_nick[nickname])

    def authorize(self):
        # first revock authorization of other participants
        with self.nicknames_lock:
            for key in self.authorized_nick.keys():
                self.authorized_nick[key] = False
            self.authorized_nick[request.get_data()] = True
        return ''

    def get_nickname(self):
        rand_id = randint(0, len(self.nicknames))
        with self.nicknames_lock:
            while self.nicknames[rand_id] in self.authorized_nick.keys():
                rand_id = randint(0, len(self.nicknames))
            nickname = self.nicknames[rand_id]
            self.authorized_nick[nickname] = False 
        return nickname

    def run(self):
        # open('http://snap.berkeley.edu/run')
        self.flask.run(host='0.0.0.0', port=self.port)

