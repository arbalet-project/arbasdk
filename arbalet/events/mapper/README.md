# Event mappers
## Role

Mappers are in charge of mapping low level data to user level data that are meaningful in the context of a game.
For instance, a keyboard mapper may map the "A pressed" information into "LEFT pressed" event.

## Mappings are configurable

The idea behind the mappers in these folders is that the mapping can be modified by the user during runtime and eventually made persistent.
If it does not make sense for some specific mapping code to be changed by the end user, then it should not be an event mapper in this folder.

## Calls to mappers

Event mappers are called from event sources coded in the parent directory.

## Notes

The simulated and real (capacitive) touch mappers share a common interface (abstract class touch.TouchMapper).
It guaranties that they share the same "touch philosophy", i.e. six 2-pixel keys on the total surface.
Other touch displays should have their own mapping abstract class.
