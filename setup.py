from setuptools import setup

APP = ['wsbreadboard/app.py']
DATA_FILES = []
OPTIONS = {
    'argv_emulation': False,
    'iconfile':'ws-breadboard.icns'
}

setup(
    name='Websocket Breadboard',
    version='0.0.1',
    description="A simple extendable python3 server to host websocket connections.",
    author="Peter Lefferts",
    author_email="peterlefferts@gmail.com",
    install_requires=[],
    url='http://github.com/plefferts/ws-breadboard',
    license="MIT",
    packages=['wsbreadboard'],
    platforms=['Any'],
    tests_require=['ws4py'],
    test_suite="tests",
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app']
)
