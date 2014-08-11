import os
import re
from setuptools import setup


with open(os.path.join('sqlalchemy_mptt', '__init__.py'), 'r') as fh:
    __version__ = (re.search(r'__version__\s*=\s*u?"([^"]+)"', fh.read())
                   .group(1).strip())


setup(
    name='sqlalchemy_mptt',
    version=__version__,
    url='http://github.com/ITCase/sqlalchemy_mptt/',
    author='Svintsov Dmitry',
    author_email='root@uralbash.ru',

    packages=['sqlalchemy_mptt', ],
    include_package_data=True,
    zip_safe=False,
    test_suite="nose.collector",
    license="MIT",
    description='SQLAlchemy MPTT mixins (Nested Sets)',
    package_data={
        '': ['*.txt', '*.rst', '*.md'],
    },
    long_description="http://github.com/ITCase/sqlalchemy_mptt/",
    install_requires=[
        "sqlalchemy",
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Natural Language :: Russian',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Framework :: Pyramid ",
        "Framework :: Flask",
        "Topic :: Internet",
        "Topic :: Database",
        'License :: OSI Approved :: MIT License',
    ],
)
