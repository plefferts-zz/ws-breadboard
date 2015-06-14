from setuptools import setup

APP = ['py-ws-server/app.py']
DATA_FILES = []
OPTIONS = {'argv_emulation': True}

setup(
    name='pywsserver',
    version='0.0.1',
    description="A simple extendable python3 server to host websocket connections.",
    author="Peter Lefferts",
    author_email="peterlefferts@gmail.com",
    install_requires=[],
    url='http://github.com/plefferts/py-ws-server',
    license="MIT",
    packages=['pywsserver'],
    platforms=['Any'],
    tests_require=['ws4py'],
    test_suite="tests",
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app']
)
