from setuptools import setup, find_packages
import os
import pathlib
import sys
sys.path.append('scheduler')

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# README file contents
README = (HERE / "README.md").read_text()

# Capture required modules in requirements.txt
with open(os.path.join(HERE, 'requirements.txt'), encoding='utf-8') as f:
    all_reqs = f.read().split('\n')

install_requires = [x.strip() for x in all_reqs if ('git+' not in x) and (not x.startswith('#')) and (not x.startswith('-'))]
dependency_links = [x.strip().replace('git+', '') for x in all_reqs if 'git+' not in x]

setup(
    name='tournament-scheduler',
    version='0.1.1',
    description='A command-line tool to generate a tournament schedule',
    license = 'LICENSE.txt',
    packages=find_packages(),
    install_requires=install_requires,
    include_package_data=True,
    entry_points='''
        [console_scripts]
        scheduler=scheduler.__main__:main
    ''',
    author='Foucauld de Bellabre',
    author_email='fdebellabre@gmail.com',
    keywords='tournament,league,schedule,timetable',
    long_description=README,
    long_description_content_type="text/markdown",
    url='https://github.com/fdebellabre/tournament-scheduler',
    dependency_links=dependency_links,
    classifiers=[
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ]
)
