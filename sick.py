from __future__ import print_function # python2

import argparse
import os
import re
import sys
import traceback

try:
    from urllib.parse import urlencode
except ImportError: # python2
    from urllib import urlencode

try:
    from configparser import ConfigParser
except ImportError: # python2
    from ConfigParser import ConfigParser

import requests

class IdNotFound(Exception):
    'Raised if no tvdbid could be found for a show name'

class Sick(object):
    def __init__(self, host, api_key):
        self.host = host
        self.api_key = api_key

    def get(self, cmd, **params):
        params['cmd'] = cmd
        qstr = urlencode(params)
        return requests.get('http://{}/api/{}/?{}'.format(self.host, self.api_key, qstr))

    def shows(self):
        data = self.get('shows').json()
        shows = ((show['show_name'], tvdbid) for tvdbid, show
                 in data['data'].items())
        for show_name, tvdbid in sorted(shows):
            print("{}\t{}".format(tvdbid, show_name))
        return 0

    def episodes(self, tvdbid=None, show_name=None):
        data = self.get('show.seasons', tvdbid=tvdbid).json()
        seasons = ((int(num), season) for num, season in data['data'].items())
        for season_num, season in sorted(seasons):
            episodes = ((int(num), ep['name']) for num, ep in season.items())
            for episode_num, episode_name in sorted(episodes):
                print("s{:02}e{:02}\t{}".format(season_num, episode_num, episode_name))
        return 0

    def episode(self, episode, tvdbid=None, show_name=None, ):
        season, episode_num = episode
        data = self.get('episode', tvdbid=tvdbid, season=season, episode=episode_num, full_path=1).json()
        location = data['data']['location']
        if location:
            print(location)
            return 0
        else:
            return 1

    def find_tvdbid(self, show_name):
        data = self.get('shows').json()
        shows = ((strip_name(show['show_name']), tvdbid) for tvdbid, show
                 in data['data'].items())
        to_compare = strip_name(show_name)
        for possible_show_name, tvdbid in shows:
            if to_compare == possible_show_name:
                return tvdbid
        raise IdNotFound()

def strip_name(name):
    return re.sub('[^a-z]', '', name.lower())

def parse_episode(episode_str):
    match = re.match(r's(\d+)e(\d+)', episode_str)
    if match:
        season, ep = match.groups()
        return int(season), int(ep)
    else:
        raise Exception('Could not parse {}'.format(episode_str))

def main(args):
    config = ConfigParser()
    config.read(['sick.ini', os.path.expanduser('~/.sick.ini'), os.path.expanduser('~/.config/sick/sick.ini')])
    try:
        sick_config = config['sick']
    except KeyError:
        sick_config = {}
    except AttributeError: # python2
        sick_config = dict(config.items('sick'))
    parser = argparse.ArgumentParser()
    default_host = sick_config.get('host')
    host_required = default_host is None
    default_api_key = sick_config.get('api_key')
    api_key_required = default_api_key is None

    parser.add_argument('--host', default=default_host, required=host_required)
    parser.add_argument('--api_key', default=default_api_key, required=api_key_required)
    parser.add_argument('args', nargs='*')
    parsed = vars(parser.parse_args(args))

    host = parsed.pop('host')
    api_key = parsed.pop('api_key')
    sick = Sick(host, api_key)

    input_args = parsed.pop('args')

    num_args = len(input_args)
    if num_args == 0:
        cmd = 'shows'
    else:
        try:
            parsed['tvdbid'] = int(input_args[0])
        except Exception:
            try:
                parsed['tvdbid'] = sick.find_tvdbid(input_args[0])
            except IdNotFound:
                print('Could not find id for {}'.format(input_args[0]), file=sys.stderr)
                return 1

        if num_args == 1:
            cmd = 'episodes'
        else:
            cmd = 'episode'
            parsed['episode'] = parse_episode(input_args[1])

    try:
        return getattr(sick, cmd)(**parsed)
    except Exception:
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
