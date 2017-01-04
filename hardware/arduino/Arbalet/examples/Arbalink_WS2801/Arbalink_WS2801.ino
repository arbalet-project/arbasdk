
/*
    Arbalet - ARduino-BAsed LEd Table
    Arbalink - Low-level Arduino code to be loaded on the microcontroller
    WS2801 version
   

    Copyright 2015 Yoan Mollard - Arbalet project - http://github.com/arbalet-project
    License: GPL version 3 http://www.gnu.org/licenses/gpl.html
*/

#include <Wire.h>
#include <Adafruit_WS2801.h>
#include "SPI.h" // Comment out this line if using Trinket or Gemma

#define CMD_HELLO 'H'
#define CMD_BUFFER_READY 'B'
#define CMD_BUFFER_READY_DATA_FOLLOWS 'D'
#define CMD_INIT_SUCCESS 'S'
#define CMD_INIT_FAILURE 'F'
#define CMD_ERROR 'E'
#define PROTOCOL_VERSION 2

unsigned short leds_num = 0;
char pin_num = 255;
char touch_type = 255;

Adafruit_WS2801 *pixels = NULL;
char *buffer;
char rgb[3];

void setup() {
  while(!Serial);
  Serial.begin(115200);
  Serial.setTimeout(5000);
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

uint16_t read_short() {
  uint16_t s=0;
  Serial.readBytes((char*)&s, 2);
  return s;
}

void write_short(uint16_t s) {
  Serial.write((uint8_t *)&s, 2);
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
 
  /* Memory allocation */
  free_allocated_memory();  // TODO, do not free, updating existing objects would be faster
  pixels = new Adafruit_WS2801(leds_num);
  
  /* Init the LED strip */
  buffer = (char*) malloc(3*leds_num);
  pixels->begin();
 
  /* Check that init is fully successful */
  write_char((buffer==NULL || pixels==NULL)? CMD_INIT_FAILURE: CMD_INIT_SUCCESS);
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

void send_touch_frame() {
}

void update_leds_from_buffer() {
  for(unsigned short led=0; led<leds_num; ++led) {
    pixels->setPixelColor(led, buffer[led*3], buffer[led*3+1], buffer[led*3+2]);
  }
  pixels->show();
}

void loop() {
    char readiness = touch_type>0? CMD_BUFFER_READY_DATA_FOLLOWS : CMD_BUFFER_READY;
    if(read_buffer(readiness)) {
      if(touch_type>0) {
          send_touch_frame();
      }
      update_leds_from_buffer();
    }
    else {
      wait_for_connection();
    }
} 
