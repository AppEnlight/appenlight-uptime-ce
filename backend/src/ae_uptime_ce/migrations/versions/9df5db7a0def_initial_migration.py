# -*- coding: utf-8 -*-

# Copyright (C) 2010-2016  RhodeCode GmbH
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License, version 3
# (only), as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# This program is dual-licensed. If you wish to learn more about the
# AppEnlight Enterprise Edition, including its added features, Support
# services, and proprietary license terms, please see
# https://rhodecode.com/licenses/

"""initial_migration

Revision ID: 9df5db7a0def
Revises: 
Create Date: 2016-03-24 12:55:47.148578

"""

# revision identifiers, used by Alembic.
revision = '9df5db7a0def'
down_revision = None
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table

def upgrade():
    version_table = table('rc_versions',
                          sa.Column('name', sa.Unicode(40)),
                          sa.Column('value', sa.Unicode(40))
                          )

    insert = version_table.insert().values(name='appenlight_es_uptime_metrics')
    op.execute(insert)

    op.create_table(
        'ae_uptime_ce_metrics',
        sa.Column('resource_id', sa.Integer(),
                  sa.ForeignKey('resources.resource_id',
                                onupdate='cascade',
                                ondelete='cascade'), index=True),
        sa.Column('start_interval', sa.DateTime, nullable=False, index=True),
        sa.Column('response_time', sa.types.REAL, nullable=False, server_default="0"),
        sa.Column('status_code', sa.Integer),
        sa.Column('owner_user_id', sa.Integer),
        sa.Column('tries', sa.Integer, nullable=False, server_default="0"),
        sa.Column('is_ok', sa.Boolean, nullable=False, server_default="True"),
        sa.Column('location', sa.Integer, nullable=False, server_default="1"),
        sa.Column('id', sa.BigInteger, nullable=False, primary_key=True),
    )

    op.execute('''
CREATE OR REPLACE FUNCTION partition_ae_uptime_ce_metrics()
  RETURNS trigger AS
$BODY$
    DECLARE
        main_table         varchar := 'ae_uptime_ce_metrics';
        partitioned_table  varchar := '';
    BEGIN

        partitioned_table := main_table || '_p_' || date_part('year', NEW.start_interval)::TEXT || '_' || DATE_part('month', NEW.start_interval);

        BEGIN
            EXECUTE 'INSERT INTO ' || partitioned_table || ' SELECT(' || TG_TABLE_NAME || ' ' || quote_literal(NEW) || ').*;';
        EXCEPTION
        WHEN undefined_table THEN
            RAISE NOTICE 'A partition has been created %', partitioned_table;
            EXECUTE format('CREATE TABLE  IF NOT EXISTS %s ( CHECK( start_interval >= DATE %s AND start_interval < DATE %s )) INHERITS (%s)',
                partitioned_table,
                quote_literal(date_trunc('month', NEW.start_interval)::date) ,
                quote_literal((date_trunc('month', NEW.start_interval)::date  + interval '1 month')::text),
                main_table);
            EXECUTE format('ALTER TABLE %s ADD CONSTRAINT ix_%s PRIMARY KEY(id);', partitioned_table, partitioned_table);
            EXECUTE format('CREATE INDEX ix_%s_start_interval  ON %s USING btree (start_interval);', partitioned_table, partitioned_table);
            EXECUTE format('CREATE INDEX ix_%s_resource_id ON %s USING btree (resource_id);', partitioned_table, partitioned_table);
            EXECUTE 'INSERT INTO ' || partitioned_table || ' SELECT(' || TG_TABLE_NAME || ' ' || quote_literal(NEW) || ').*;';
        END;
        RETURN NULL;
    END
    $BODY$
  LANGUAGE plpgsql VOLATILE SECURITY DEFINER
  COST 100;
    ''')

    op.execute('''
    CREATE TRIGGER ae_uptime_ce_metrics BEFORE INSERT ON ae_uptime_ce_metrics FOR EACH ROW EXECUTE PROCEDURE partition_ae_uptime_ce_metrics();
    ''')


def downgrade():
    pass
