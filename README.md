sick - a command line tool for finding your [SickBeard](http://sickbeard.com/) shows

### Installation

```
pip install git+git://github.com/clofresh/sick#egg=sick
```

It's testing in python 2.7 and 3.4, but may work in other versions.

### Usage

To list the shows in your SickBeard

```
$ sick --host <sickbeard host> --api_key <api key>
81189   Breaking Bad
275557  Broad City
94571   Community
193131  Downton Abbey
281618  Fresh Off the Boat
121361  Game of Thrones
155201  Louie (2010)
80337   Mad Men
275274  Rick and Morty
176941  Sherlock
283468  Star Wars Rebels
153021  The Walking Dead
79126   The Wire
192061  Young Justice
```

If you don't want to keep entering in your host and api key, you can put it in
a config file:

```
$ cat > ~/.sick.ini
[sick]
host=127.0.0.1:8081
api_key=68b329da9893e34099c7d8ad5cb9c940
```

To view your downloaded episodes for a show, you can pass in the id:

```
$ sick 79126
s01e05  The Pager
s01e06  The Wire
s01e07  One Arrest
s01e08  Lessons
s01e09  Game Day
s01e10  The Cost
```

If you don't know the id, you can also pass in the name. It's case-insensitive and ignores spaces:

```
$ sick youngjustice
s01e01  Independence Day
s01e02  Fireworks
s01e03  Welcome to Happy Harbor
s01e04  Drop-Zone
s01e05  Schooled
s01e06  Infiltrator
```

To get the filename for that episode, pass in the episode id:

```
$ sick youngjustice s01e03
/home/me/tv_shows/Young Justice/Season 1/Young Justice - 1x03 - Welcome to Happy Harbor.mkv
```

It works great for launching shows from command line with vlc or mplayer:

```
smplayer $(sick sherlock s3e3)
```

### Contributing

Fork the repo, make your change, then run the tests with [tox](https://tox.readthedocs.org/en/latest/):

```
tox
```

If they pass, submit a pull request.
