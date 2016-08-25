===============================
rock
===============================

OpenStack Instance HA

Please fill here a long description which must be at least 3 lines wrapped on
80 cols, so that distribution package maintainers can use it in their packages.
Note that this is a hard requirement.

* Free software: Apache license
* Documentation: http://docs.openstack.org/developer/rock
* Source: http://git.openstack.org/cgit/mathematrix/rock
* Bugs: http://bugs.launchpad.net/rock

Features
--------

* TODO

Getting Start
-------------

* Initialize Database
  1. Change working directory to ../rock/db/sqlalchemy
       $ cd ../rock/db/sqlalchemy
  2. Modify alembic.ini, setup the `sqlalchemy.url` in section [alembic]
  3. Initialize database:
       $ alembic upgrade head
  4. Downgrade database:
       $ alembic downgrade base

