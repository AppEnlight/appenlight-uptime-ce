# -*- coding: utf-8 -*-

# Copyright 2010 - 2017 RhodeCode GmbH and the AppEnlight project authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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
