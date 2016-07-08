Flask
=====

Initialize Flask app and sqlalchemy

.. code-block:: python

   from pprint import pprint
   from flask import Flask
   from flask_sqlalchemy import SQLAlchemy

   from sqlalchemy_mptt.mixins import BaseNestedSets

   app = Flask(__name__)
   app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
   db = SQLAlchemy(app)

Make models.

.. code-block:: python
   :emphasize-lines: 1

   class Category(db.Model, BaseNestedSets):
       __tablename__ = 'categories'
       id = db.Column(db.Integer, primary_key=True)
       name = db.Column(db.String(400), index=True, unique=True)
       items = db.relationship("Product", backref='item', lazy='dynamic')

       def __repr__(self):
           return '<Category {}>'.format(self.name)


   class Product(db.Model):
       __tablename__ = 'products'
       id = db.Column(db.Integer, primary_key=True)
       category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
       name = db.Column(db.String(475), index=True)

Represent data of tree in table
-------------------------------

Add data to table with tree.

.. code-block:: python

   db.session.add(Category(name="root"))  # root node
   db.session.add_all(  # first branch of tree
       [
           Category(name="foo", parent_id=1),
           Category(name="bar", parent_id=2),
           Category(name="baz", parent_id=3),
       ]
   )
   db.session.add_all(  # second branch of tree
       [
           Category(name="foo1", parent_id=1),
           Category(name="bar1", parent_id=5),
           Category(name="baz1", parent_id=5),
       ]
   )

   db.drop_all()
   db.create_all()
   db.session.commit()

The database entries are added:

.. code-block:: text

    "id"  "name"  "lft"  "rgt"  "level"  "parent_id"  "tree_id"
    1     "root"  1      14     1        1
    2     "foo"   2      7      2        1            1
    3     "bar"   3      6      3        2            1
    4     "baz"   4      5      4        3            1
    5     "foo1"  8      13     2        1            1
    6     "bar1"  9      10     3        5            1
    7     "baz1"  11     12     3        5            1


``Lft`` of root element every time :math:`1`.

:math:`root_{lft} = 1`

``Rgt`` of root element always equal 2 * quantity of tree nodes.

:math:`root_{rgt} = 2 * | P |`

:math:`root_{rgt} = 2 * 7 = 14`

The tree that displays the records in the database is represented schematically
below:

.. code-block:: text

   level
     1                  1(root)14
                            |
                   ---------------------
                   |                   |
     2          2(foo)7             8(foo1)13
                   |               /         \
     3          3(bar)6        9(bar1)10   11(baz1)12
                   |
     4          4(baz)5

Drilldown
---------

Drilldown tree for a given node.

A drilldown tree consists of a node’s ancestors, itself and its immediate
children. For example, a drilldown tree for a ``foo1`` category might look
something like:

.. code-block:: text

   Drilldown for foo1 node

   level
     1                  1(root)14
                            |
                   ---------------------
                   |         ----------|---------------
     2          2(foo)7      |      8(foo1)13         |
                   |         |     /         \        |
     3          3(bar)6      | 9(bar1)10   11(baz1)12 |
                   |         --------------------------
     4          4(baz)5

.. code-block:: python

   categories = Category.query.all()

   for item in categories:
       print(item)
       pprint(item.drilldown_tree())
       print()

.. code-block:: text

    <Category root>
    [{'children': [{'children': [{'children': [{'node': <Category baz>}],
                                  'node': <Category bar>}],
                    'node': <Category foo>},
                   {'children': [{'node': <Category bar1>},
                                 {'node': <Category baz1>}],
                    'node': <Category foo1>}],
      'node': <Category root>}]

    <Category foo>
    [{'children': [{'children': [{'node': <Category baz>}],
                    'node': <Category bar>}],
      'node': <Category foo>}]

    <Category bar>
    [{'children': [{'node': <Category baz>}], 'node': <Category bar>}]

    <Category baz>
    [{'node': <Category baz>}]

    <Category foo1>
    [{'children': [{'node': <Category bar1>}, {'node': <Category baz1>}],
      'node': <Category foo1>}]

    <Category bar1>
    [{'node': <Category bar1>}]

    <Category baz1>
    [{'node': <Category baz1>}]

Represent it to JSON format:

.. code-block:: python

   def cat_to_json(item):
       return {
           'id': item.id,
           'name': item.name
       }

   for item in categories:
       pprint(item.drilldown_tree(json=True, json_fields=cat_to_json))
       print()

.. code-block:: text

    [{'children': [{'children': [{'children': [{'id': 4,
                                                'label': '<Category baz>',
                                                'name': 'baz'}],
                                  'id': 3,
                                  'label': '<Category bar>',
                                  'name': 'bar'}],
                    'id': 2,
                    'label': '<Category foo>',
                    'name': 'foo'},
                   {'children': [{'id': 6,
                                  'label': '<Category bar1>',
                                  'name': 'bar1'},
                                 {'id': 7,
                                  'label': '<Category baz1>',
                                  'name': 'baz1'}],
                    'id': 5,
                    'label': '<Category foo1>',
                    'name': 'foo1'}],
      'id': 1,
      'label': '<Category root>',
      'name': 'root'}]

    [{'children': [{'children': [{'id': 4,
                                  'label': '<Category baz>',
                                  'name': 'baz'}],
                    'id': 3,
                    'label': '<Category bar>',
                    'name': 'bar'}],
      'id': 2,
      'label': '<Category foo>',
      'name': 'foo'}]

    [{'children': [{'id': 4, 'label': '<Category baz>', 'name': 'baz'}],
      'id': 3,
      'label': '<Category bar>',
      'name': 'bar'}]

    [{'id': 4, 'label': '<Category baz>', 'name': 'baz'}]

    [{'children': [{'id': 6, 'label': '<Category bar1>', 'name': 'bar1'},
                   {'id': 7, 'label': '<Category baz1>', 'name': 'baz1'}],
      'id': 5,
      'label': '<Category foo1>',
      'name': 'foo1'}]

    [{'id': 6, 'label': '<Category bar1>', 'name': 'bar1'}]

    [{'id': 7, 'label': '<Category baz1>', 'name': 'baz1'}]

Path to root
------------

Returns a list containing the ancestors and the node itself in tree order.

.. code-block:: text

   Path to root of bar node

   level      ---------------------
     1        |         1(root)14 |
              |             |     |
              |    ---------------|-----
              |    |    -----------    |
     2        | 2(foo)7 |           8(foo1)13
              |    |    |          /         \
     3        | 3(bar)6 |      9(bar1)10   11(baz1)12
              -----|-----
     4          4(baz)5

.. code-block:: python

   for item in categories:
       print(item)
       print(item.path_to_root()[-1])  # get root
                                       # last element in list
       pprint(item.path_to_root().all())
       print()

.. code-block:: text

    <Category root>
    <Category root>
    [<Category root>]

    <Category foo>
    <Category root>
    [<Category foo>, <Category root>]

    <Category bar>
    <Category root>
    [<Category bar>, <Category foo>, <Category root>]

    <Category baz>
    <Category root>
    [<Category baz>, <Category bar>, <Category foo>, <Category root>]

    <Category foo1>
    <Category root>
    [<Category foo1>, <Category root>]

    <Category bar1>
    <Category root>
    [<Category bar1>, <Category foo1>, <Category root>]

    <Category baz1>
    <Category root>
    [<Category baz1>, <Category foo1>, <Category root>]

Full code
---------

.. code-block:: python3

    from pprint import pprint
    from flask import Flask
    from flask_sqlalchemy import SQLAlchemy

    from sqlalchemy_mptt.mixins import BaseNestedSets

    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
    db = SQLAlchemy(app)


    class Category(db.Model, BaseNestedSets):
        __tablename__ = 'categories'
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(400), index=True, unique=True)
        items = db.relationship("Product", backref='item', lazy='dynamic')

        def __repr__(self):
            return '<Category {}>'.format(self.name)


    class Product(db.Model):
        __tablename__ = 'products'
        id = db.Column(db.Integer, primary_key=True)
        category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
        name = db.Column(db.String(475), index=True)

    db.session.add(Category(name="root"))  # root node
    db.session.add_all(  # first branch of tree
        [
            Category(name="foo", parent_id=1),
            Category(name="bar", parent_id=2),
            Category(name="baz", parent_id=3),
        ]
    )
    db.session.add_all(  # second branch of tree
        [
            Category(name="foo1", parent_id=1),
            Category(name="bar1", parent_id=5),
            Category(name="baz1", parent_id=5),
        ]
    )

    '''
    "id"  "name"  "lft"  "rgt"  "level"  "parent_id"  "tree_id"
    1     "root"  1      14     1        1
    2     "foo"   2      7      2        1            1
    3     "bar"   3      6      3        2            1
    4     "baz"   4      5      4        3            1
    5     "foo1"  8      13     2        1            1
    6     "bar1"  9      10     3        5            1
    7     "baz1"  11     12     3        5            1

    root lft everytime = 1
    root rgt = qty_nodes * 2

    level
      1                  1(root)14
                             |
                    ---------------------
                    |                   |
      2          2(foo)7             8(foo1)13
                    |               /         \
      3          3(bar)6        9(bar1)10   11(baz1)12
                    |
      4          4(baz)5
    '''

    db.drop_all()
    db.create_all()
    db.session.commit()

    categories = Category.query.all()

    for item in categories:
        print(item)
        pprint(item.drilldown_tree())
        print()

    '''
    <Category root>
    [{'children': [{'children': [{'children': [{'node': <Category baz>}],
                                  'node': <Category bar>}],
                    'node': <Category foo>},
                   {'children': [{'node': <Category bar1>},
                                 {'node': <Category baz1>}],
                    'node': <Category foo1>}],
      'node': <Category root>}]

    <Category foo>
    [{'children': [{'children': [{'node': <Category baz>}],
                    'node': <Category bar>}],
      'node': <Category foo>}]

    <Category bar>
    [{'children': [{'node': <Category baz>}], 'node': <Category bar>}]

    <Category baz>
    [{'node': <Category baz>}]

    <Category foo1>
    [{'children': [{'node': <Category bar1>}, {'node': <Category baz1>}],
      'node': <Category foo1>}]

    <Category bar1>
    [{'node': <Category bar1>}]

    <Category baz1>
    [{'node': <Category baz1>}]
    '''

    for item in categories:
        print(item)
        print(item.path_to_root()[-1])
        pprint(item.path_to_root().all())
        print()

    '''
    <Category root>
    <Category root>
    [<Category root>]

    <Category foo>
    <Category root>
    [<Category foo>, <Category root>]

    <Category bar>
    <Category root>
    [<Category bar>, <Category foo>, <Category root>]

    <Category baz>
    <Category root>
    [<Category baz>, <Category bar>, <Category foo>, <Category root>]

    <Category foo1>
    <Category root>
    [<Category foo1>, <Category root>]

    <Category bar1>
    <Category root>
    [<Category bar1>, <Category foo1>, <Category root>]

    <Category baz1>
    <Category root>
    [<Category baz1>, <Category foo1>, <Category root>]
    '''
