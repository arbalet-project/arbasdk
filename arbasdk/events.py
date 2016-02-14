"""
    Arbalet - ARduino-BAsed LEd Table
    events - Arbalet Event Manager

    Generates events for joysticks, keyboards and touch screen

    Copyright 2016 Yoan Mollard - Arbalet project - http://github.com/arbalet-project
    License: GPL version 3 http://www.gnu.org/licenses/gpl.html
"""

from threading import RLock

__all__ = ['get']

BI_DIRECTIONAL = 2
TRI_DIRECTIONAL = 3
QUADRI_DIRECTIONAL = 4
COLUMNS = 5
INDIVIDUAL = 6

num_buttons = 6  # Number of touch buttons
previous_state = [False]*num_buttons
touch_events = []
events_lock = RLock()

def create_event(touch):
    """
    Create the event associated to the specified touch state
    """
    global touch_events, previous_state

    def touch_to_buttons(touch):
        return [(touch & (1 << bit)) > 0 for bit in range(num_buttons)]

    state = touch_to_buttons(touch)
    with events_lock:
        for button in range(num_buttons):
            if state[button] == previous_state[button]:
                continue
            event = { 'id': button+1, 'pressed': state[button] }
            touch_events.append(event)
    previous_state = state

def get(mode=INDIVIDUAL):
    global touch_events

    if mode == BI_DIRECTIONAL:
        mapping = { 1: None, 2: 'left', 3: 'right', 4: 'left', 5: None, 6: 'right' }
    elif mode == TRI_DIRECTIONAL:
        mapping = { 1: 'up', 2: None, 3: None, 4: 'left', 5: None, 6: 'right' }
    elif mode == QUADRI_DIRECTIONAL:
        mapping = { 1: 'up', 2: 'left', 3: 'right', 4: None, 5: 'down', 6: None }
    elif mode == COLUMNS:
        mapping = { 1: None, 2: 2, 3: 4, 4: 1, 5: 3, 6: 5 }
    elif mode == INDIVIDUAL:
        mapping = { 1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6 }
    else:
        raise RuntimeError("Mode {} is not known to {}".format(mode, __file__))
    with events_lock:
        events = map_events(touch_events, mapping)
        touch_events = []
    return events

def map_events(raw_events, mapping):
    events = []
    for event in raw_events:
        meaning = mapping[event['id']]
        down = event['pressed']
        if meaning is not None:
            events.append({ 'key': meaning,
                            'type': 'down' if down else 'up' })
    return events
