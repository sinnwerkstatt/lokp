import sys

from ..models.database_objects import *
from ..models.meta import Base
from ..models.meta import DBSession
from datetime import datetime
import os
from pyramid.paster import get_appsettings
from pyramid.paster import setup_logging
from sqlalchemy import engine_from_config
from sqlalchemy.orm.exc import MultipleResultsFound
from sqlalchemy.orm.exc import NoResultFound
import transaction

def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri>\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)

def main(argv=sys.argv):
    if len(argv) != 2:
        usage(argv)
    config_uri = argv[1]
    setup_logging(config_uri)
    settings = get_appsettings(config_uri)
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.create_all(engine)
    
    _populate(engine, settings)

def _addIfNotExists_ID(object):
    q = DBSession.query(object.__mapper__).get(object.id)
    if q is None:
        # object does not yet exist -> create
        DBSession.add(object)
        return object
    else:
        return q

def _addIfNotExists_NoIDUnique(object, filterColumn, filterAttr):
    try:
        q = DBSession.query(User).filter(filterColumn == filterAttr).one()
        return q
    except NoResultFound:
        return object
    except MultipleResultsFound:
        return None

def _populate(engine, settings):
    """
    Populate the database with some initial values and triggers.
    """
    
    # add triggers
    engine.execute("CREATE OR REPLACE FUNCTION data.check_uniqueVersionActive() RETURNS TRIGGER AS $check_uniqueVersionActive$ \
                        DECLARE \
                            active_count integer; \
                            version_count integer; \
                        BEGIN \
                            IF (NEW.fk_status = 2) THEN \
                                IF (TG_TABLE_NAME = 'activities') THEN \
                                    SELECT INTO active_count COUNT(*) FROM data.activities WHERE activity_identifier = NEW.activity_identifier AND fk_status = 2; \
                                ELSIF (TG_TABLE_NAME = 'stakeholders') THEN \
                                    SELECT INTO active_count COUNT(*) FROM data.stakeholders WHERE stakeholder_identifier = NEW.stakeholder_identifier AND fk_status = 2; \
                                END IF; \
                            END IF; \
                            IF (active_count >= 1) THEN \
                                IF NOT (active_count = 1 AND TG_OP = 'UPDATE' AND OLD.fk_status = NEW.fk_status) THEN \
                                    RAISE EXCEPTION 'There can be only one! Only one entry per identifier is allowed to be active in tables stakeholders and activities.'; \
                                END IF; \
                            END IF; \
                            IF (TG_TABLE_NAME = 'activities') THEN \
                                SELECT INTO version_count COUNT(*) FROM data.activities WHERE activity_identifier = NEW.activity_identifier AND version = NEW.version; \
                            ELSIF (TG_TABLE_NAME = 'stakeholders') THEN \
                                SELECT INTO version_count COUNT(*) FROM data.stakeholders WHERE stakeholder_identifier = NEW.stakeholder_identifier AND version = NEW.version; \
                            END IF; \
                            IF (version_count >= 1) THEN \
                                IF NOT (version_count = 1 AND TG_OP = 'UPDATE' AND OLD.version = NEW.version) THEN \
                                    RAISE EXCEPTION 'Not a unique version! Each version number within an identifier must be unique in tables stakeholders and activities.'; \
                                END IF; \
                            END IF; \
                            RETURN NEW; \
                        END; \
                        $check_uniqueVersionActive$ LANGUAGE plpgsql;")
    engine.execute("DROP TRIGGER IF EXISTS check_uniqueVersionActive ON data.activities;")
    engine.execute("DROP TRIGGER IF EXISTS check_uniqueVersionActive ON data.stakeholders;")
    engine.execute("CREATE TRIGGER check_uniqueVersionActive \
                    BEFORE UPDATE OR INSERT ON data.activities \
                    FOR EACH ROW \
                    EXECUTE PROCEDURE data.check_uniqueVersionActive();")
    engine.execute("CREATE TRIGGER check_uniqueVersionActive \
                    BEFORE UPDATE OR INSERT ON data.stakeholders \
                    FOR EACH ROW \
                    EXECUTE PROCEDURE data.check_uniqueVersionActive();")
    
    # add initial values
    with transaction.manager:
        # language
        lang1 = _addIfNotExists_ID(Language(id=1, english_name='English', local_name='English', locale='en'))
        # status
        status1 = _addIfNotExists_ID(Status(id=1, name='pending', description='Review pending. Not published yet.'))
        status2 = _addIfNotExists_ID(Status(id=2, name='active', description='Reviewed and accepted. Currently published.'))
        status3 = _addIfNotExists_ID(Status(id=3, name='inactive', description='Inactive. Previously active.'))
        status4 = _addIfNotExists_ID(Status(id=4, name='deleted', description='Deleted. Not published anymore.'))
        status5 = _addIfNotExists_ID(Status(id=5, name='rejected', description='Reviewed and rejected. Never published.'))
        status6 = _addIfNotExists_ID(Status(id=6, name='edited', description='Edited. Previously pending.'))
        # permissions
        permission1 = _addIfNotExists_ID(Permission(id=1, name='administer', description='Can add key/values and do batch translations.'))
        permission2 = _addIfNotExists_ID(Permission(id=2, name='moderate', description='Can make review decisions on reported information.'))
        permission3 = _addIfNotExists_ID(Permission(id=3, name='edit', description='Can report information.'))
        permission4 = _addIfNotExists_ID(Permission(id=4, name='view', description='Can see information. (basic permission - granted to everyone)'))
        permission5 = _addIfNotExists_ID(Permission(id=5, name='translate', description='Can add and modify translations.'))
        # groups (with permissions)
        group1 = _addIfNotExists_ID(Group(id=1, name='administrators'))
        group1.permissions.append(permission1)
        group1.permissions.append(permission3)
        group1.permissions.append(permission4)
        group2 = _addIfNotExists_ID(Group(id=2, name='moderators'))
        group2.permissions.append(permission2)
        group2.permissions.append(permission3)
        group2.permissions.append(permission4)
        group3 = _addIfNotExists_ID(Group(id=3, name='editors'))
        group3.permissions.append(permission3)
        group3.permissions.append(permission4)
        group4 = _addIfNotExists_ID(Group(id=4, name='translators'))
        group4.permissions.append(permission5)
        # users (only 1 admin user)
        admin_password = settings['lmkp.admin_password']
        admin_email = settings['lmkp.admin_email']
        user1 = _addIfNotExists_NoIDUnique(User(username='admin',
                                           password=admin_password,
                                           email=admin_email,
                                           is_active=True,
                                           is_approved=True,
                                           registration_timestamp=datetime.now()), User.username, 'admin')
        if user1 is not None:
            user1.groups = [group1, group2, group3, group4]
        # connected with profile1 (global)
        #user2 = _addIfNotExists_NoIDUnique(User(username='user2', password='pw', email='user2@cde.unibe.ch'), User.username, 'user2')
        #user2.groups.append(group2)
        # connected with profile1 (global)
        #user3 = _addIfNotExists_NoIDUnique(User(username='user3', password='pw', email='user3@cde.unibe.ch'), User.username, 'user3')
        #user3.groups.append(group3)
