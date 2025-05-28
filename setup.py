import os
from setuptools import setup

this = os.path.dirname(os.path.realpath(__file__))


def read(name):
    with open(os.path.join(this, name)) as f:
        return f.read()


setup(
    name="sqlalchemy_mptt",
    version="0.4.0",
    url="http://github.com/uralbash/sqlalchemy_mptt/",
    author="Svintsov Dmitry",
    author_email="sacrud@uralbash.ru",
    maintainer="Fayaz Khan",
    maintainer_email="fayaz.yusuf.khan@gmail.com",
    packages=["sqlalchemy_mptt"],
    include_package_data=True,
    zip_safe=False,
    license="MIT",
    description="SQLAlchemy mixins for implementing tree-like models using Modified Pre-order Tree Traversal (MPTT) / Nested Sets",
    long_description=read("README.rst") + "\n" + read("CHANGES.rst"),
    install_requires=read("requirements.txt"),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Framework :: Pyramid",
        "Framework :: Flask",
        "Topic :: Internet",
        "Topic :: Database",
        "License :: OSI Approved :: MIT License",
    ],
)
