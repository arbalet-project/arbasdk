/*
    Arbalet - ARduino-BAsed LEd Table
    Arbalink - Low-level Arduino code to be loaded on the microcontroller
    
    WARNING - WARNING - WARNING - WARNING - WARNING - WARNING - WARNING
    Since this code depends on your hardware it is not part of arbasdk.
    Because of this, loading this code will probably NOT work if you
    use different hardware than mine (Pololu LED strips WS2812B)
    
    Choose your case A or B:
    
    A) You do not use WS2812B, WS2811, WS2812 or TM1804 based LED strips:
    A.1) You can implement you own for you own LEDs as long as you make it
    compatible with the protocol used by arbasdk. See the wiki to do so:
    http://github.com/arbalet-project/arbadoc
    A.2) The read_model() function already reads the protocol used by arbasdk
    and returns a matrix of RGB values.
    A.3) From this matrix update you LEDs as needed, whatever they are
    addressable, connected through a demux, directly on digital pins, ...
    
    B) You do use WS2812B, WS2811, WS2812 or TM1804 addressable LED strips:
    B.1) You can use this present code based on the Pololu library:
    https://github.com/pololu/pololu-led-strip-arduino
    B.2) Please download that library first and import it in you Arduino IDE
    with menu Sketch > Import library > Add library (this is the step you
    have missed in case of error "no such file or directory")
    B.3) To check that your wiring and the low-level library work well
    please run the examples provided in that library before connecting
    your table with arbask (LedStripColorTester, LedStripGradient,
    LedStripRainbow and LedStripXmas).
    B.4) Update the macros of this script (width, height, pin)
    B.5) Connect the arbasdk...

    Copyright 2015 Yoan Mollard - Arbalet project - http://github.com/arbalet-project
    License: GPL version 3 http://www.gnu.org/licenses/gpl.html
*/

#include <Wire.h>
#include <SPI.h>
#include <PololuLedStrip.h>
#include <Adafruit_CAP1188.h>

#define WIDTH 10
#define HEIGHT 15

// Create an ledStrip object and specify the pin it will use.
PololuLedStrip<12> ledStrip;

// Create the connexion to the capacitive sensors
Adafruit_CAP1188 cap = Adafruit_CAP1188();

// Create a buffer for holding the colors (3 bytes per color).
rgb_color colors[WIDTH*HEIGHT];
char matrix[WIDTH*HEIGHT*3];


void cleanup() {
  byte p;
  for(p=0; p<WIDTH*HEIGHT; ++p) {
      colors[p] = (rgb_color){ 0, 0, 0 };
  }
  ledStrip.write(colors, WIDTH*HEIGHT);
}

int readMatrix(int len) {
  int b = 0;
  while(b<len) {
    if(Serial.available()) {
      matrix[b] = Serial.read();
      ++b;
    }
  }
  return b;
}

void setup() {
  cleanup();
  while(!cap.begin());
  Serial.begin(1000000);
}

void loop() {
    int num = readMatrix(WIDTH*HEIGHT*3);
    byte h, w;
    for(h=0; h<HEIGHT; ++h) {
      for(w=0; w<WIDTH; ++w) {
        byte pixel = h*WIDTH+w;
        colors[pixel] = (rgb_color){ matrix[3*pixel], matrix[3*pixel+1], matrix[3*pixel+2] };
      }
    }
    Serial.println(cap.touched());
    ledStrip.write(colors, WIDTH*HEIGHT);
}
