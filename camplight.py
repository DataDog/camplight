#!/usr/bin/env python

"""
Campfire command-line client

Usage: camplight.py <command> [<args>]

The API is described at http://developer.37signals.com/campfire/index
"""

__author__ = 'Mathias Lafeldt <mathias.lafeldt@gmail.com>'
__all__ = ['Campfire', 'Room', 'Sound']

import requests
import simplejson as json


def json_encode(obj=None):
    if obj is None:
        obj = {}
    return json.dumps(obj)


def json_decode(s):
    return json.loads(s) if s.startswith('{') else {}


class Campfire(object):

    def __init__(self, url, token):
        self._url = url
        self._auth = (token, '')

    def _request(self, method, path, **kwargs):
        r = requests.request(method, self._url + path + '.json',
                             auth=self._auth, **kwargs)
        r.raise_for_status()
        return json_decode(r.content)

    def get(self, path):
        return self._request('GET', path)

    def post(self, path, data=None):
        return self._request('POST', path,
                             headers={'Content-Type': 'application/json'},
                             data=json_encode(data))

    def put(self, path, data=None):
        return self._request('PUT', path,
                             headers={'Content-Type': 'application/json'},
                             data=json_encode(data))

    def rooms(self):
        return self.get('/rooms')['rooms']

    def room(self, id):
        try:
            int(id)
        except:
            id = [r['id'] for r in self.rooms() if r['name'] == id][0]
        return Room(self, id)

    def user(self, id='me'):
        return self.get('/users/%s' % id)['user']

    def presence(self):
        return self.get('/presence')['rooms']

    def search(self, term):
        return self.get('/search/%s' % term)['messages']


class Room(object):

    def __init__(self, campfire, room_id):
        self.campfire = campfire
        self.room_id = room_id

    def get(self, path=None, **kwargs):
        if path == None:
            path = ''
        return self.campfire.get('/room/%s%s' % (self.room_id, path), **kwargs)

    def post(self, path=None, **kwargs):
        if path == None:
            path = ''
        return self.campfire.post('/room/%s%s' % (self.room_id, path),
                                  **kwargs)

    def put(self, path=None, **kwargs):
        if path == None:
            path = ''
        return self.campfire.put('/room/%s%s' % (self.room_id, path), **kwargs)

    def show(self):
        return self.get()['room']

    def set_name(self, name):
        self.put(data={'room': {'name': name}})

    def set_topic(self, topic):
        self.put(data={'room': {'topic': topic}})

    def recent(self):
        return self.get('/recent')['messages']

    def transcript(self):
        return self.get('/transcript')['messages']

    def uploads(self):
        return self.get('/uploads')['uploads']

    def join(self):
        self.post('/join')

    def leave(self):
        self.post('/leave')

    def lock(self):
        self.post('/lock')

    def unlock(self):
        self.post('/unlock')

    def speak(self, message, type='TextMessage'):
        data = {'message': {'body': message, 'type': type}}
        return self.post('/speak', data=data)['message']

    def paste(self, message):
        return self.speak(message, 'PasteMessage')

    def play(self, sound):
        return self.speak(sound, 'SoundMessage')


class Sound(object):
    crickets = 'crickets'
    drama = 'drama'
    greatjob = 'greatjob'
    live = 'live'
    rimshot = 'rimshot'
    tmyk = 'tmyk'
    trombone = 'trombone'
    vuvuzela = 'vuvuzela'
    yeah = 'yeah'


if __name__ == '__main__':
    import sys
    import os

    # TODO add proper option handling
    def handle_cmd(campfire, args):
        cmd = args[1]
        if cmd == 'rooms':
            return campfire.rooms()
        elif cmd == 'user':
            return campfire.user(args[2])
        elif cmd == 'presence':
            return campfire.presence()
        elif cmd == 'search':
            return campfire.search(args[2])
        else:
            room_id = os.environ['CAMPFIRE_ROOM']
            room = campfire.room(room_id)
            if cmd == 'show':
                return room.show()
            elif cmd == 'name':
                return room.set_name(args[2])
            elif cmd == 'topic':
                return room.set_topic(args[2])
            elif cmd == 'recent':
                return room.recent()
            elif cmd == 'transcript':
                return room.transcript()
            elif cmd == 'uploads':
                return room.uploads()
            elif cmd == 'join':
                return room.join()
            elif cmd == 'leave':
                return room.leave()
            elif cmd == 'lock':
                return room.lock()
            elif cmd == 'unlock':
                return room.unlock()
            elif cmd == 'speak':
                return room.speak(args[2])
            elif cmd == 'paste':
                return room.paste(args[2])
            elif cmd == 'play':
                return room.play(args[2])
            else:
                raise Exception('invalid command')

    token = os.environ['CAMPFIRE_TOKEN']
    url = os.environ['CAMPFIRE_URL']
    campfire = Campfire(url, token)
    data = handle_cmd(campfire, sys.argv)
    if data:
        # HACK re-encode json for pretty output
        import simplejson as json
        print json.dumps(data, indent=4)
