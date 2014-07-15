#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

# This is a placeholder for Icehouse backports.
# Do not use this number for new Juno work.  New Juno work starts after
# all the placeholders.
#
# See blueprint backportable-db-migrations-juno
# http://lists.openstack.org/pipermail/openstack-dev/2013-March/006827.html

from migrate.changeset import UniqueConstraint
from migrate import ForeignKeyConstraint
from sqlalchemy import Boolean, BigInteger, Column, DateTime, Enum, Float
from sqlalchemy import dialects
from sqlalchemy import ForeignKey, Index, Integer, MetaData, String, Table
from sqlalchemy import Text
from sqlalchemy.types import NullType

from nova.openstack.common.gettextutils import _
from nova.openstack.common import log as logging

LOG = logging.getLogger(__name__)

def upgrade(migrate_engine):
    meta = MetaData()
    meta.bind = migrate_engine
    
    traffic_info = Table('traffic_info',meta,
		Column('id',Integer,primary_key=True,nullable=False),
		Column('src',Integer,nullable=False),
		Column('dst',Integer,nullable=False),
		Column('bandwidth',Float,nullable=False),
		Column('time',DateTime,nullable=False),
		mysql_engine='InnoDB',
		mysql_charset='utf8'
    )
    try:
	traffic_info.create()
    except Exception:
	LOG.info(repr(traffic_info))
	LOG.exception(_('Exception while creating table.'))
        raise

    # TO DO
    # Create indicies	


def downgrade(migrate_engine):
	traffic_info = Table('traffic_info')
	try:
            traffic_info.drop()
	except Exception:
	    LOG.info(repr(traffic_info))
	    LOG.exception(_('Exception while creating table.'))
            raise
