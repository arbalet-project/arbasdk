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
char pin_num = 255;
char touch_type = 255;

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
  Serial.setTimeout(500);
  wait_for_connection();
}

void wait_for_connection() {
  while(!handshake());
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

void free_allocated_memory() {
  if(pixels!=NULL) {
    delete(pixels);
    pixels = NULL;
  }
  if(buffer!=NULL) {
    free(buffer);
    buffer = NULL;
  }
}

int handshake() {
  write_char(CMD_HELLO);
  if(read_char()!=CMD_HELLO) return 0;
  write_char(PROTOCOL_VERSION);
  leds_num = read_short();  // default: 150
  if(leds_num==0) return 0;
  pin_num = read_char();    // default: 12
  if(pin_num==0) return 0;
  touch_type = read_char(); // default: 0 (off)
  if(touch_type==255) return 0;
  
  /* Memory allocation */
  free_allocated_memory();
  // TODO: Do not free, updating existing objects could make connection faster with a Leonardo since connection does not reset the board
  
  pixels = new Adafruit_NeoPixel(leds_num, pin_num, NEO_GRB + NEO_KHZ800);
  buffer = (char*) malloc(3*leds_num);
  pixels->begin();
  write_char((buffer==0 || pixels==0)? CMD_INIT_FAILURE: CMD_INIT_SUCCESS);
  return 1;
}

int read_buffer() {
  write_char(CMD_BUFFER_READY);
  for(unsigned short led=0; led<leds_num; ++led) {
    short num_read = Serial.readBytes(rgb, 3);
    if(num_read!=3) {
      return 0;
    }
    for(unsigned short color=0; color<3; ++color) {
      buffer[3*led+color] = rgb[color];
    }
  }
  return 1;
}

void loop() {
    if(!read_buffer()) {
      wait_for_connection();
    }
    else {
      for(unsigned short led=0; led<leds_num; ++led) {
        pixels->setPixelColor(led, pixels->Color(buffer[led*3], buffer[led*3+1], buffer[led*3+2]));
      }
      pixels->show();
    }
}
