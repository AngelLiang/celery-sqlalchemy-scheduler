"""
    celery-sqlalchemy-scheduler
    ~~~~~~~~~~~~~~
    A Scheduler Based SQLalchemy For Celery.
    :Copyright (c) 2018 AngelLiang
    :license: MIT, see LICENSE for more details.
"""
from os import path
from codecs import open
try:
    from setuptools import find_packages, setup
except ImportError:
    from distutils.core import setup, find_packages
# To use a consistent encoding

basedir = path.abspath(path.dirname(__file__))
# Get the long description from the README file
with open(path.join(basedir, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="celery_sqlalchemy_scheduler",

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version="0.0.2",
    # The project's main homepage.
    url="https://github.com/AngelLiang/celery-sqlalchemy-scheduler",
    # Choose your license

    license='MIT',

    description="A Scheduler Based SQLalchemy For Celery",
    long_description=long_description,
    long_description_content_type='text/markdown',  # 长描述内容类型

    platforms='any',
    # Author details
    author="AngelLiang",
    author_email='yannanxiu@126.com',
    home_page='https://github.com/AngelLiang/celery-sqlalchemy-scheduler',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],

    # What does your project relate to?
    keywords="celery scheduler sqlalchemy beat",

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),

    # Alternatively, if you want to distribute just a my_module.py, uncomment
    # this:
    #   py_modules=["my_module"],

    # List run-time dependencies here.  These will be installed by pip when
    # your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html

    install_requires=[
        "celery>=4.2.0",
        "sqlalchemy"
    ],
    zip_safe=False,
)
