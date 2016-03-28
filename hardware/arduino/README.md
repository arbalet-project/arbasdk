## Where should I place these libraries?

Each of these folders goes to your Arduino libraries folder.
Do not nest them, this is unsupported by the IDE.

If ~/sketchbook/libraries is your libraries folder, you must end up with the following folders:
```
~/sketchbook/libraries/Adafruit_NeoPixel
~/sketchbook/libraries/Arbalet
```

## And then?
Make sure all Arduino IDE windows are closed and reopen it, you should now see these libraries in File > Examples.
If you don't see them make sure they are not nested into subfolders.

## How to install the Arbalet firmware?
Open File > Arbalet > Arbalink
This is the firmware to load onto the microcontroller. Please refer to [Firmware uploading](https://github.com/arbalet-project/arbadoc/wiki/Hardware-and-Software-preliminaries#firmware-uploading) for details.
