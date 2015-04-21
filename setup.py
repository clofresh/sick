try:
    from setuptools import setup

    install_requires = ['requests']

    try:
        import argparse
    except ImportError:
        install_requires.append('argparse')

    kws = {
        'install_requires': install_requires,
        'entry_points': {
            'console_scripts': ['sick = sick:main']
        },
    }
except ImportError:
    from distutils.core import setup
    kws = {}

kws['py_modules'] = ['sick']
setup(name='sick', version=open('VERSION').read().strip(), **kws)
