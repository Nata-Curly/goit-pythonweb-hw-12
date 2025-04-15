.. Contacts App documentation master file, created by
   sphinx-quickstart on Mon Apr 14 22:30:40 2025.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Contacts App documentation
==========================

Welcome to the documentation for the Contacts App project built with FastAPI.  
This project allows users to manage their contacts with features such as user authentication, CRUD operations on contacts, and birthday notifications.

Features
--------

- User registration and authentication
- Contact management (Create, Read, Update, Delete)
- Filtering contacts by birthday
- Integration with database via repository pattern
- JWT-based access tokens


.. toctree::
   :maxdepth: 2
   :caption: Contents:

Contacts App main
===================
.. automodule:: main
  :members:
  :undoc-members:
  :show-inheritance:


App Endpoints
-------------

Authentication

.. automodule:: src.api.auth
   :members:
   :undoc-members:
   :show-inheritance:

Contacts

.. automodule:: src.api.contacts
   :members:
   :undoc-members:
   :show-inheritance:

Users

.. automodule:: src.api.users
   :members:
   :undoc-members:
   :show-inheritance:

Models
------

Database Models
^^^^^^^^^^^^^^^
.. automodule:: src.database.models
   :members:
   :undoc-members:
   :show-inheritance:

Schemas
^^^^^^^
.. automodule:: src.schemas
   :members:
   :undoc-members:
   :show-inheritance:

Services
--------

Contacts Service

.. automodule:: src.services.contacts
   :members:
   :undoc-members:
   :show-inheritance:

Users Service

.. automodule:: src.services.users
   :members:
   :undoc-members:
   :show-inheritance:

Auth Service

.. automodule:: src.services.auth
   :members:
   :undoc-members:
   :show-inheritance:

Repositories
------------

Contacts Repository

.. automodule:: src.repository.contacts
   :members:
   :undoc-members:
   :show-inheritance:

Users Repository

.. automodule:: src.repository.users
   :members:
   :undoc-members:
   :show-inheritance:

Configuration
-------------

App Configuration

.. automodule:: src.conf.config
   :members:
   :undoc-members:
   :show-inheritance:


Indices and Search
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
