Contribution Guidelines
=======================

All types of contributions are welcome: suggestions, ideas, commits
with new features, bug fixes, refactoring, docs, tests, translations, etc...

If you have any questions:

* Use the `Discussion board <https://github.com/uralbash/sqlalchemy_mptt/discussions>`_
* Contact the maintainer via email: fayaz.yusuf.khan@gmail.com
* Contact the author via email: sacrud@uralbash.ru or #sacrud IRC channel |IRC Freenode|

Development Setup
-----------------

To set up the development environment, you can run:

.. code-block:: bash

    # Install uv
    $ pip install uv
    # Run the noxfile.py script
    $ uv run noxfile.py -s dev

By default, this will create a virtual environment with Python 3.8 and install all the required dependencies.
If you need to setup the development environment with a specific Python version, you can run:

.. code-block:: bash

    $ uv run noxfile.py -s dev -P 3.10

Running Tests
-------------

To run the tests and linters, you can use the following command:

.. code-block:: bash

    $ uv run noxfile.py

For futher details, refer to the ``noxfile.py`` script.

.. |IRC Freenode| image:: https://img.shields.io/badge/irc-freenode-blue.svg
   :target: https://webchat.freenode.net/?channels=sacrud
