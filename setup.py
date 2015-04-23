from sick.version import __version__

try:
    from setuptools import setup

    install_requires = ['requests']
    try:
        import argparse
    except ImportError:
        install_requires.append('argparse')

    kws = {
        'install_requires': install_requires,
        'entry_points': {'console_scripts': ['sick = sick.core:main']},
    }
except ImportError:
    from distutils.core import setup
    kws = {}

kws['packages'] = ['sick']
kws['py_modules'] = ['sick.core', 'sick.test', 'sick.version']
setup(name='sick', version=__version__, **kws)
