from setuptools import setup
import os, re

setup(
    name='py-ws-server',
    version='0.0.1',
    description="A simple extendable python3 server to host websocket connections.",
    author="Peter Lefferts",
    author_email="peterlefferts@gmail.com",
    install_requires=[],
    url='http://github.com/plefferts/py-ws-server',
    license="MIT",
    packages=['py-ws-server'],
    platforms=['Any'],
    tests_require=['ws4py'],
    test_suite="tests"
)