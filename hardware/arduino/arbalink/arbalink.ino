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

#include <Adafruit_NeoPixel.h>

#define WIDTH 10
#define HEIGHT 15
#define PIN 12

#define BUFFER_READY 1

const byte leds_num = WIDTH*HEIGHT;

// Create an ledStrip object and specify the pin it will use.
Adafruit_NeoPixel pixels = Adafruit_NeoPixel(leds_num, PIN, NEO_GRB + NEO_KHZ800);
char buffer[WIDTH*HEIGHT*3];
char rgb[3];

void show_all(byte r=0, byte g=0, byte b=0) {
  for(int led=0; led<leds_num; ++led){
    pixels.setPixelColor(led, pixels.Color(r, g, b));
  }
  pixels.show();
}

void setup() {
  pixels.begin();
  show_all(0, 5, 0);   // Light green
  while(!Serial);
  Serial.begin(1000000);
  show_all(0, 0, 0);
}

void read_buffer() {
  Serial.write(BUFFER_READY);
  for(int led=0; led<leds_num; ++led) {
    byte num_read = Serial.readBytes(rgb, 3);
    for(byte color=0; color<num_read; ++color) {
      buffer[3*led+color] = rgb[color];
    }
  } 
}

void loop() {
    read_buffer();
    for(int led=0; led<leds_num; ++led) {
      pixels.setPixelColor(led, pixels.Color(buffer[led*3], buffer[led*3+1], buffer[led*3+2]));
    }
    pixels.show();
}
