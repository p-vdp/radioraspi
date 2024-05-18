from setuptools import setup

setup(
    name='westinghouse',
    version='1.0.0',
    install_requires=[
        'gpiod',
        'python-mpd2;python_version<"3.11"',
    ],
)
