#!/usr/bin/env python
"""
    Arbalet - ARduino-BAsed LEd Table
    Spectrum Analyzer for Audio files

    This Spectrum analyzer has 2 classes:
    * SpectrumAnalyser: reading a wave file, computing the Discrete Fourier Transform
      (DFT, FFT) for each chunk of file, and playing the chunk of sound
    * Renderer: coloring the table with respect to the FFT
    It works in vertical and horizontal, splitting the range of frequencies consequently

    Copyright (C) 2015 Yoan Mollard <yoan@konqifr.fr>

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program; if not, write to the Free Software
    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
"""
import struct, argparse, numpy, pyaudio, audioop, wave, time
from arbasdk import Arbapp, hsv
from threading import Thread
from copy import copy

class Renderer(Thread):
    """
    This thread renders the FFT bands on Arbalet
    It is in charge of all colors and animations
    """
    def __init__(self, rate, model, height, width, vertical=True):
        Thread.__init__(self)
        self.setDaemon(True)
        self.rate = rate
        self.model = model
        self.height = height
        self.width = width
        self.averages = None     # FFT bands
        self.num_bands = width if vertical else height
        self.vertical = vertical
        self.colors = [hsv(c, 100, 100) for c in range(0, 360, int(360./self.num_bands))]
        self.amplitude_factor = 3500000 # Sum of amplitudes [tricky to compute and cannot be real-time] TODO
        self.running = True

    def stop(self):
        self.running = False

    def update_bands(self, averages):
        self.averages = map(int, averages)

    def draw_bars_hv(self, num_bands, num_bins, vertical):
        for bin in range(num_bins):
            ampli_b = bin*self.amplitude_factor
            for band in range(num_bands):
                if ampli_b < self.averages[band]:
                    color = self.colors[band]
                elif self.old_model: # animation with light decreasing
                    old = self.old_model.get_pixel(bin if vertical else band, band if vertical else bin).hsva
                    color = hsv(old[0], old[1], old[2]*0.8)
                else:
                    color = 'black'
                self.model.set_pixel(bin if vertical else band, band if vertical else bin, color)

    def draw_bars(self):
        """
        Draw the bins using FFT averages according to the orientation of the grid (vertical, horizontal)
        """
        if self.averages:
            self.old_model = copy(self.model)
            if self.vertical:
                self.draw_bars_hv(self.width, self.height, True)
            else:
                self.draw_bars_hv(self.height, self.width, False)

    def run(self):
        while self.running:
            self.draw_bars()
            time.sleep(1./self.rate)

class SpectrumAnalyser(Arbapp):
    """
    This is the main entry point of the spectrum analyser, it reads the file, computes the FFT and plays the sound
    """
    def __init__(self, height, width, argparser, vertical=True):
        Arbapp.__init__(self, width, height, argparser)
        self.chunk = 2*1024
        self.vertical = vertical
        self.parser = argparser
        self.renderer = None
        self.file = None
        self.pyaudio = pyaudio.PyAudio()

        ##### Fourier related attributes, we generate a suitable log-scale
        self.num_bands = self.width if self.vertical else self.height
        self.min = 50
        self.max = 22050
        #self.db_scale = [self.file.getframerate()*2**(b-self.num_bands) for b in range(self.num_bands)]
        #self.db_scale = [self.min+self.max*2**(b-self.num_bands+1) for b in range(self.num_bands)]
        self.db_scale = [self.max*(numpy.exp(-numpy.log(float(self.min)/self.max)/self.num_bands))**(b-self.num_bands) for b in range(1, self.num_bands+1)]
        print "Scale of maximum frequencies:", map(int, self.db_scale)

    def fft(self, sample):
        """
        Compute the FFT on this sample and update the self.averages FFT result
        """
        def chunks(l, n):
            for i in xrange(0, len(l), n):
                yield l[i:i+n]

        def str_to_int(string):
            return struct.unpack('<h', string)[0] # Convert little-endian char into int

        sample_range = map(str_to_int, list(chunks(sample, self.file.getsampwidth())))
        fft_data = abs(numpy.fft.rfft(sample_range)) # real fft gives samplewidth/2 bands
        try:
            fft_freq = numpy.fft.rfftfreq(len(sample_range))
        except AttributeError:   # numpy<1.8
            fft_freq = [0.5/len(fft_data)*f for f in range(len(fft_data))]
        freq_hz = [abs(fft_freq[i])*self.file.getframerate() for i, fft in enumerate(fft_data)]
        fft_freq_scaled = [0.]*len(self.db_scale)
        ref_index = 0
        for i, f in enumerate(fft_data):
            if freq_hz[i]>self.db_scale[ref_index]:
                ref_index += 1
            fft_freq_scaled[ref_index] += f
        self.averages = fft_freq_scaled

    def play_file(self, f):
        self.file = wave.open(f, 'rb')
        self.stream = self.pyaudio.open(format=self.pyaudio.get_format_from_width(self.file.getsampwidth()),
                                channels=self.file.getnchannels(),
                                rate=self.file.getframerate(),
                                output=True)
        try:
            data = self.file.readframes(self.chunk)
            while data != '':
                mono_data = audioop.tomono(data, self.file.getsampwidth(), 0.5, 0.5)
                self.fft(mono_data)
                self.renderer.update_bands(self.averages)

                self.stream.write(data)
                data = self.file.readframes(self.chunk)
        finally:
            self.stream.stop_stream()
            self.stream.close()

    def run(self):
        self.renderer = Renderer(30, self.model, self.height, self.width, self.vertical)
        self.renderer.start()
        for f in self.args.input:
            self.play_file(f)
        self.renderer.stop()

if __name__=='__main__':
    parser = argparse.ArgumentParser(description='Spectrum analyzer of WAVE files')
    parser.add_argument('-i', '--input',
                        type=str,
                        required=True,
                        nargs='+',
                        help='Wave file(s) to play')
    SpectrumAnalyser(15, 10, parser, vertical=False).start()