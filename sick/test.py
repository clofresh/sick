import json
import sys
import unittest

import responses
import requests

from sick.core import main as sick_main

class TestSick(unittest.TestCase):
    @responses.activate
    def test_list_shows(self):
        body = '''
{
    "data": {
        "70863": {
            "air_by_date": 0,
            "cache": {
                "banner": 1,
                "poster": 1
            },
            "language": "en",
            "network": "Fuji TV",
            "next_ep_airdate": "",
            "paused": 0,
            "quality": "HD",
            "show_name": "Rurouni Kenshin",
            "status": "Ended",
            "tvdbid": 70863,
            "tvrage_id": 5073,
            "tvrage_name": "Rurouni Kenshin (JP)"
        },
        "72885": {
            "air_by_date": 0,
            "cache": {
                "banner": 1,
                "poster": 1
            },
            "language": "en",
            "network": "ABC Family",
            "next_ep_airdate": "",
            "paused": 0,
            "quality": "SD",
            "show_name": "Gargoyles",
            "status": "Ended",
            "tvdbid": 72885,
            "tvrage_id": 3646,
            "tvrage_name": "Gargoyles"
        },
        "74543": {
            "air_by_date": 0,
            "cache": {
                "banner": 1,
                "poster": 1
            },
            "language": "en",
            "network": "HBO",
            "next_ep_airdate": "",
            "paused": 0,
            "quality": "SD",
            "show_name": "Entourage",
            "status": "Ended",
            "tvdbid": 74543,
            "tvrage_id": 3449,
            "tvrage_name": "Entourage"
        }
    },
    "message": "",
    "result": "success"
}
'''
        responses.add(responses.GET, 'http://test/api/test_key/?cmd=shows',
                      match_querystring=True,
                      body=body, status=200, content_type='application/json')

        result = sick_main(['--host', 'test', '--api_key', 'test_key'])
        self.assertEquals(result, 0)

        expected = sorted((data['show_name'], tvdbid) for tvdbid, data
                          in json.loads(body)['data'].items())
        self.assertEquals(len(expected), 3)

        output = sys.stdout.getvalue()
        lines = output.split('\n')
        self.assertEquals(len(lines), 4)

        for i, (name, tvdbid) in enumerate(expected):
            line = lines[i]
            self.assertIn(name, line)
            self.assertIn(tvdbid, line)
        self.assertEquals('', lines[3])

    @responses.activate
    def test_list_episodes(self):
        body = '''
{
    "data": {
        "0": {
            "1": {
                "airdate": "",
                "name": "Unaired Pilot",
                "quality": "N/A",
                "status": "Skipped"
            },
            "2": {
                "airdate": "2010-08-30",
                "name": "Unlocking Sherlock",
                "quality": "N/A",
                "status": "Skipped"
            },
            "3": {
                "airdate": "2012-02-07",
                "name": "Sherlock Uncovered",
                "quality": "N/A",
                "status": "Skipped"
            },
            "4": {
                "airdate": "2013-12-24",
                "name": "Many Happy Returns",
                "quality": "N/A",
                "status": "Skipped"
            },
            "5": {
                "airdate": "2013-12-25",
                "name": "Unlocking Sherlock (2013)",
                "quality": "N/A",
                "status": "Skipped"
            },
            "6": {
                "airdate": "2014-01-19",
                "name": "Sherlock Uncovered: The Return",
                "quality": "N/A",
                "status": "Skipped"
            },
            "7": {
                "airdate": "2014-01-26",
                "name": "Sherlock Uncovered: The Woman",
                "quality": "N/A",
                "status": "Skipped"
            },
            "8": {
                "airdate": "2014-02-02",
                "name": "Sherlock Uncovered: The Villains",
                "quality": "N/A",
                "status": "Skipped"
            }
        },
        "1": {
            "1": {
                "airdate": "2010-07-25",
                "name": "A Study in Pink",
                "quality": "N/A",
                "status": "Skipped"
            },
            "2": {
                "airdate": "2010-08-01",
                "name": "The Blind Banker",
                "quality": "N/A",
                "status": "Skipped"
            },
            "3": {
                "airdate": "2010-08-08",
                "name": "The Great Game",
                "quality": "N/A",
                "status": "Skipped"
            }
        },
        "2": {
            "1": {
                "airdate": "2012-01-01",
                "name": "A Scandal in Belgravia",
                "quality": "N/A",
                "status": "Skipped"
            },
            "2": {
                "airdate": "2012-01-08",
                "name": "The Hounds of Baskerville",
                "quality": "N/A",
                "status": "Skipped"
            },
            "3": {
                "airdate": "2012-01-15",
                "name": "The Reichenbach Fall",
                "quality": "N/A",
                "status": "Skipped"
            }
        },
        "3": {
            "1": {
                "airdate": "2014-01-01",
                "name": "The Empty Hearse",
                "quality": "SD TV",
                "status": "Downloaded"
            },
            "2": {
                "airdate": "2014-01-05",
                "name": "The Sign of Three",
                "quality": "SD TV",
                "status": "Downloaded"
            },
            "3": {
                "airdate": "2014-01-12",
                "name": "His Last Vow",
                "quality": "SD TV",
                "status": "Downloaded"
            }
        }
    },
    "message": "",
    "result": "success"
}
'''
        url = 'http://test/api/test_key/?cmd=show.seasons&tvdbid=176941'
        responses.add(responses.GET, url,
                      match_querystring=True,
                      body=body, status=200, content_type='application/json')

        result = sick_main(['--host', 'test', '--api_key', 'test_key', '176941'])
        self.assertEquals(result, 0)

        expected = []
        for season_num, season in sorted(json.loads(body)['data'].items(),
                                         key=lambda p: int(p[0])):
            season_num = int(season_num)
            for episode_num, episode in sorted(season.items(),
                                               key=lambda p: int(p[0])):
                if episode.get('status') == 'Downloaded':
                    ep = 's{:02}e{:02}'.format(season_num, int(episode_num))
                    expected.append((ep, episode['name']))
        self.assertEquals(len(expected), 3)

        output = sys.stdout.getvalue()
        lines = output.split('\n')
        self.assertEquals(len(lines), 4)

        for i, (ep, name) in enumerate(expected):
            line = lines[i]
            self.assertIn(ep, line)
            self.assertIn(name, line)
        self.assertEquals('', lines[3])

if __name__ == '__main__':
    unittest.main()
