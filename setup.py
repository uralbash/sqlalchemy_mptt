from sqlalchemy_mptt import __version__
from setuptools import setup

try:
    from pypandoc import convert
    read_md = lambda f: convert(f, 'rst')
except ImportError:
    print("warning: pypandoc module not found, could not convert Markdown to RST")
    read_md = lambda f: open(f, 'r').read()

setup(
    name='sqlalchemy_mptt',
    version=__version__,
    url='http://github.com/ITCase/sqlalchemy_mptt/',
    author='Svintsov Dmitry',
    author_email='root@uralbash.ru',

    packages=['sqlalchemy_mptt'],
    include_package_data=True,
    zip_safe=False,
    test_suite="nose.collector",
    license="GPL",
    description='SQLAlchemy MPTT mixins (Nested Sets)',
    long_description=read_md('README.md'),
    install_requires=[
        "sqlalchemy",
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
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
        "License :: Repoze Public License",
    ],
)
