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
    NoSectionError = None
except ImportError: # python2
    from ConfigParser import ConfigParser, NoSectionError

import requests

class TvDbIdNotFound(Exception):
    'Raised if no tvdbid could be found for a show name'

class AccessDenied(Exception):
    'Raised if the api returns a json object whose result field is `denied`'

class QueryFailure(Exception):
    'Raised if api returns a json object whose result field is `failure`'

class InvalidEpisodeId(Exception):
    'Raised if passed an invalid episode id'

ErrorPrintAsIs = (AccessDenied, QueryFailure, InvalidEpisodeId)

class Sick(object):
    def __init__(self, host, api_key):
        self.host = host
        self.api_key = api_key

    def get(self, cmd, **params):
        params['cmd'] = cmd
        qstr = urlencode(sorted(params.items()))
        response = requests.get('http://{}/api/{}/?{}'.format(self.host, self.api_key, qstr))
        body = response.json()
        result = body.get('result')
        if result == 'denied':
            raise AccessDenied(body.get('message', ''))
        elif result == 'failure' or result == 'error':
            raise QueryFailure(body.get('message', ''))
        else:
            return body, response

    def shows(self):
        data, _ = self.get('shows')
        shows = ((show['show_name'], tvdbid) for tvdbid, show
                 in data['data'].items())
        for show_name, tvdbid in sorted(shows):
            print("{}\t{}".format(tvdbid, show_name))
        return 0

    def episodes(self, tvdbid=None, show_name=None):
        data, _ = self.get('show.seasons', tvdbid=tvdbid)
        seasons = ((int(num), season) for num, season in data['data'].items())
        for season_num, season in sorted(seasons):
            episodes = ((int(num), ep['name']) for num, ep in season.items()
                        if ep.get('status') == 'Downloaded')
            for episode_num, episode_name in sorted(episodes):
                print("s{:02}e{:02}\t{}".format(season_num, episode_num, episode_name))
        return 0

    def episode(self, episode, tvdbid=None, show_name=None, ):
        season, episode_num = episode
        data, _ = self.get('episode', tvdbid=tvdbid, season=season, episode=episode_num, full_path=1)
        location = data['data']['location']
        if location:
            print(location)
            return 0
        else:
            return 1

    def find_tvdbid(self, show_name):
        data, _ = self.get('shows')
        shows = ((strip_name(show['show_name']), tvdbid) for tvdbid, show
                 in data['data'].items())
        to_compare = strip_name(show_name)
        for possible_show_name, tvdbid in shows:
            if to_compare == possible_show_name:
                return tvdbid
        raise TvDbIdNotFound(show_name)

def strip_name(name):
    return re.sub('[^a-z]', '', name.lower())

def parse_episode(episode_str):
    match = re.match(r's(\d+)e(\d+)', episode_str)
    if match:
        season, ep = match.groups()
        return int(season), int(ep)
    else:
        raise InvalidEpisodeId('Could not parse episode id {}. Must look something like s03e10'.format(episode_str))

def main(args=None):
    config = ConfigParser()
    config.read(['sick.ini', os.path.expanduser('~/.sick.ini'), os.path.expanduser('~/.config/sick/sick.ini')])
    try:
        sick_config = config['sick']
    except KeyError:
        sick_config = {}
    except AttributeError: # python2
        try:
            sick_config = dict(config.items('sick'))
        except NoSectionError:
            sick_config = {}
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

    try:
        if num_args == 0:
            cmd = 'shows'
        else:
            try:
                parsed['tvdbid'] = int(input_args[0])
            except Exception:
                parsed['tvdbid'] = sick.find_tvdbid(input_args[0])

            if num_args == 1:
                cmd = 'episodes'
            else:
                cmd = 'episode'
                parsed['episode'] = parse_episode(input_args[1])

        return getattr(sick, cmd)(**parsed)
    except ErrorPrintAsIs as e:
        print(e, file=sys.stderr)
        return 1
    except TvDbIdNotFound as e:
        print('Could not find TVDB id for {}'.format(e), file=sys.stderr)
        return 1

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
