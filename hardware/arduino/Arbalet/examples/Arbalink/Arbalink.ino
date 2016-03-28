/*
    Arbalet - ARduino-BAsed LEd Table
    Arbalink - Low-level Arduino code to be loaded on the microcontroller
    

    Copyright 2015 Yoan Mollard - Arbalet project - http://github.com/arbalet-project
    License: GPL version 3 http://www.gnu.org/licenses/gpl.html
*/
#include <Wire.h>
#include <Adafruit_NeoPixel.h>
#include <Adafruit_MPR121.h>

#define CMD_HELLO 'H'
#define CMD_BUFFER_READY 'B'  // Used if no touch data comes with this frame (TODO config["touch_frequency"]?)
#define CMD_BUFFER_READY_DATA_FOLLOWS 'D'
#define CMD_INIT_SUCCESS 'S'
#define CMD_INIT_FAILURE 'F'
#define CMD_ERROR 'E'
#define PROTOCOL_VERSION 2

unsigned short leds_num = 0;
char pin_num = 255;
char touch_type = 255;

// Create an ledStrip object and specify the pin it will use.
Adafruit_NeoPixel *pixels = NULL;
Adafruit_MPR121 *touch = NULL;
char *buffer;
char rgb[3];
uint16_t touch_int = 0;  // Stores a boolean status for each touch input
uint16_t *touch_values = NULL;

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

boolean handshake() {
  write_char(CMD_HELLO);
  if(read_char()!=CMD_HELLO) return false;
  write_char(PROTOCOL_VERSION);
  leds_num = read_short();  // default: 150
  if(leds_num==0) return false;
  pin_num = read_char();    // default: 12
  if(pin_num==0) return false;
  touch_type = read_char(); // default: 0 (off)
  if(touch_type==255) return false;
  pixels = new Adafruit_NeoPixel(leds_num, pin_num, NEO_GRB + NEO_KHZ800);
  touch = new Adafruit_MPR121();
  touch_values = malloc(size_of(*touch_values)*touch_type);
  buffer = (char*) malloc(3*leds_num);
  pixels->begin();
  boolean touch_init = touch? touch->begin() : false;
  write_char((buffer==NULL || pixels==NULL || touch_init==false || touch_values==NULL)? CMD_INIT_FAILURE: CMD_INIT_SUCCESS);
  return true;
}

boolean read_buffer(char readiness) {
  write_char(readiness);
  for(unsigned short led=0; led<leds_num; ++led) {
    short num_read = Serial.readBytes(rgb, 3);
    if(num_read!=3) {
      return false;
    }
    for(unsigned short color=0; color<3; ++color) {
      buffer[3*led+color] = rgb[color];
    }
  }
  return true;
}

void read_touch_sensors() {
    write_short(cap.touched());
    for(char id=0; id<touch_type; ++id) {
      write_short(cap.filtered(id));
    }
}



void update_leds_from_buffer() {
  for(unsigned short led=0; led<leds_num; ++led) {
    pixels->setPixelColor(led, pixels->Color(buffer[led*3], buffer[led*3+1], buffer[led*3+2]));
  }
  pixels->show();
}

void loop() {
    if(!read_buffer(CMD_BUFFER_READY_DATA_FOLLOWS)) {
      wait_for_connection();
    }
    else {
      update_leds_from_buffer();
      read_touch_sensors();
      write_touch_frame();
    }
}
