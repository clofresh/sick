import json
import sys
import unittest

import responses

from sick.core import main as sick_main


class TestSickShows(unittest.TestCase):
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

if __name__ == '__main__':
    unittest.main()
