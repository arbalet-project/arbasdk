/*
    Arbalet - ARduino-BAsed LEd Table
    Arbalink - Low-level Arduino code to be loaded on the microcontroller
    

    Copyright 2015 Yoan Mollard - Arbalet project - http://github.com/arbalet-project
    License: GPL version 3 http://www.gnu.org/licenses/gpl.html
*/

#include <Adafruit_NeoPixel.h>

#define CMD_HELLO 'H'
#define CMD_BUFFER_READY 'B'
#define CMD_INIT_SUCCESS 'S'
#define CMD_INIT_FAILURE 'F'
#define CMD_ERROR 'E'
#define PROTOCOL_VERSION 1

unsigned short leds_num = 0;
char pin_num = 0;
char touch_type = 0;

// Create an ledStrip object and specify the pin it will use.
Adafruit_NeoPixel *pixels = NULL;
char *buffer;
char rgb[3];

void show_all(byte r=0, byte g=0, byte b=0) {
  for(unsigned short led=0; led<leds_num; ++led){
    pixels->setPixelColor(led, pixels->Color(r, g, b));
  }
  pixels->show();
}

void setup() {
  while(!Serial);
  Serial.begin(115200);
  Serial.setTimeout(5000);
  handshake();
}

char read_char() {
  char c=0;
  Serial.readBytes(&c, 1);
  return c;
}

void write_char(char c) {
  Serial.write(c);
}

unsigned short read_short() {
  unsigned short s=0;
  Serial.readBytes((char*)&s, 2);
  return s;
}

void write_short(unsigned short s) {
  Serial.write(s);
}

void handshake() {
  write_char(CMD_HELLO);
  if(read_char()==CMD_HELLO) {
    write_char(PROTOCOL_VERSION);
    leds_num = read_short();  // default: 150
    pin_num = read_char();    // default: 12
    touch_type = read_char(); // default: 0 (off)
    pixels = new Adafruit_NeoPixel(leds_num, pin_num, NEO_GRB + NEO_KHZ800);
    buffer = (char*) malloc(3*leds_num);
    pixels->begin();
    write_short((buffer==0 || pixels==0)? CMD_INIT_FAILURE: CMD_INIT_SUCCESS);
  }
  else {
    write_char(CMD_ERROR);
  }
}

void read_buffer() {
  write_char(CMD_BUFFER_READY);
  for(unsigned short led=0; led<leds_num; ++led) {
    short num_read = Serial.readBytes(rgb, 3);
    for(unsigned short color=0; color<num_read; ++color) {
      buffer[3*led+color] = rgb[color];
    }
  } 
}

void loop() {
    read_buffer();
    for(unsigned short led=0; led<leds_num; ++led) {
      pixels->setPixelColor(led, pixels->Color(buffer[led*3], buffer[led*3+1], buffer[led*3+2]));
    }
    pixels->show();
}
