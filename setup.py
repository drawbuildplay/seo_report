import os
import re
from setuptools import setup, find_packages

pip_requires = os.path.join(os.getcwd(), 'requirements.txt')

REQUIRES=[
    'BeautifulSoup4',
    'requests',
    'six'
]

setup(
    name='seoreport',
    version='0.0.1',
    license='MIT License',
    author='Amit Gandhi (DrawBuildPlay, LLC)',
    author_email='amit@drawbuildplay.com',
    keywords='seo analyzer, search engine optimization, on page seo analyzer',
    description='A Python client for analyzing webpages for SEO issues.',
    url='https://github.com/drawbuildplay/seo-report',
    install_requires=REQUIRES,
    packages = find_packages(),
    entry_points={
        'console_scripts': [
            'seoreport = seo_report.cmd:main'
        ]
    }
)
    
