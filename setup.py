from setuptools import setup

from wpactrl import version

setup(
    name='gevent-wpactrl',
    version='%d.%d.%d' % version(),
    author='Pontus Karlsson',
    author_email='pontuscarlsson@live.se',
    packages=['wpactrl'],
    license='LICENSE',
    description='A native implementation of python-wpactrl using gevent.',
    long_description=open('README.rst').read(),
    url='https://github.com/wolfhechel/gevent-wpactrl',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: System :: Networking'
    ]
)
