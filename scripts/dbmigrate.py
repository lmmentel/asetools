# coding: utf-8

from etlalchemy import ETLAlchemySource, ETLAlchemyTarget

# source and targe addresses
pgsql = 'postgresql+psycopg2://smn_kvantekjemi_test_user:9bad82f6@dbpg-hotel-utv.uio.no/smn_kvantekjemi_test'
sqlite = 'sqlite:////usit/abel/u1/lukaszme/nanoreactor.db'

# set the target and source
source = ETLAlchemySource(pgsql)
target = ETLAlchemyTarget(sqlite)

# do the migration
target.addSource(source)
target.migrate(migrate_data=True, migrate_schema=True)

