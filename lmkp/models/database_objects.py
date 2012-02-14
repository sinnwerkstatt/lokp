from lmkp.models.meta import Base

from sqlalchemy.dialects.postgresql import UUID
import datetime

# registering of uuid needed, done in meta.py
import uuid

from sqlalchemy import (
    Table,
    Column,
    Integer,
    Text,
    String,
    DateTime,
    ForeignKey
)

from sqlalchemy.orm import (
    relationship,
    backref
)

# ...
from shapely import wkb
import geojson

# imports needed for geometry table (A_Events)
from geoalchemy.geometry import (
    GeometryColumn,
    Geometry
)

class A_Key(Base):
    __tablename__ = 'a_keys'
    __table_args__ = {'schema': 'data'}
    id = Column(Integer, primary_key = True)
    fk_a_key = Column(Integer, ForeignKey('data.a_keys.id'))
    fk_language = Column(Integer, ForeignKey('data.languages.id'))
    key = Column(String(255), nullable = False)
    
    translations = relationship('A_Key', backref = backref('original', remote_side = [id]))
    tags = relationship('A_Tag', backref = 'key')
    
    def __init__(self, key):
        self.key = key
    
    def __repr__(self):
        return "<A_Key> id [ %s ] | fk_a_key [ %s ] | fk_language [ %s ] | key [ %s ]" % (self.id, self.fk_a_key, self.fk_language, self.key)

class SH_Key(Base):
    __tablename__ = 'sh_keys'
    __table_args__ = {'schema': 'data'}
    id = Column(Integer, primary_key = True)
    fk_sh_key = Column(Integer, ForeignKey('data.sh_keys.id'))
    fk_language = Column(Integer, ForeignKey('data.languages.id'))
    key = Column(String(255), nullable = False)
    
    translations = relationship('SH_Key', backref = backref('original', remote_side = [id]))
    tags = relationship('SH_Tag', backref = 'key')
    
    def __init__(self, key):
        self.key = key
    
    def __repr__(self):
        return "<SH_Key> id [ %s ] | fk_sh_key [ %s ] | fk_language [ %s ] | key [ %s ]" % (self.id, self.fk_sh_key, self.fk_language, self.key)

class A_Value(Base):
    __tablename__ = 'a_values'
    __table_args__ = {'schema': 'data'}
    id = Column(Integer, primary_key = True)
    fk_a_value = Column(Integer, ForeignKey('data.a_values.id'))
    fk_language = Column(Integer, ForeignKey('data.languages.id'))
    value = Column(Text, nullable = False)
    
    translations = relationship('A_Value', backref = backref('original', remote_side = [id]))
    tags = relationship('A_Tag', backref = 'value')
    
    def __init__(self, value):
        self.value = value
    
    def __repr__(self):
        return "<A_Value> id [ %s ] | fk_a_value [ %s ] | fk_language [ %s ] | value [ %s ]" % (self.id, self.fk_a_value, self.fk_language, self.value)

class SH_Value(Base):
    __tablename__ = 'sh_values'
    __table_args__ = {'schema': 'data'}
    id = Column(Integer, primary_key = True)
    fk_sh_value = Column(Integer, ForeignKey('data.sh_values.id'))
    fk_language = Column(Integer, ForeignKey('data.languages.id'))
    value = Column(Text, nullable = False)
    
    translations = relationship('SH_Value', backref = backref('original', remote_side = [id]))
    tags = relationship('SH_Tag', backref = 'value')
    
    def __init__(self, value):
        self.value = value
    
    def __repr__(self):
        return "<SH_Value> id [ %s ] | fk_sh_value [ %s ] | fk_language [ %s ] | value [ %s ]" % (self.id, self.fk_sh_value, self.fk_language, self.value)

class A_Tag(Base):
    __tablename__ = 'a_tags'
    __table_args__ = {'schema': 'data'}
    id = Column(Integer, primary_key = True)
    uuid = Column(UUID, nullable = False, unique = True)
    fk_a_event = Column(Integer, ForeignKey('data.a_events.id'), nullable=False)
    fk_key = Column(Integer, ForeignKey('data.a_keys.id'), nullable = False)
    fk_value = Column(Integer, ForeignKey('data.a_values.id'), nullable = False)

    def __init__(self):
        self.uuid = uuid.uuid4()

    def __repr__(self):
        return "<A_Tag> id [ %s ] | uuid [ %s ] | fk_a_event [ %s ] | fk_key [ %s ] | fk_value [ %s ]" % (self.id, self.uuid, self.fk_a_event, self.fk_key, self.fk_value)

class SH_Tag(Base):
    __tablename__ = 'sh_tags'
    __table_args__ = {'schema': 'data'}
    id = Column(Integer, primary_key = True)
    uuid = Column(UUID, nullable = False, unique = True)
    fk_sh_event = Column(Integer, ForeignKey('data.sh_events.id'), nullable=False)
    fk_key = Column(Integer, ForeignKey('data.sh_keys.id'), nullable = False)
    fk_value = Column(Integer, ForeignKey('data.sh_values.id'), nullable = False)

    def __init__(self):
        self.uuid = uuid.uuid4()

    def __repr__(self):
        return "<SH_Tag> id [ %s ] | uuid [ %s ] | fk_sh_event [ %s ] | fk_key [ %s ] | fk_value [ %s ]" % (self.id, self.uuid, self.fk_sh_event, self.fk_key, self.fk_value)

class A_Event(Base):
    __tablename__ = 'a_events'
    __table_args__ = {'schema': 'data'}
    id = Column(Integer, primary_key = True)
    uuid = Column(UUID, nullable = False, unique = True)
    fk_activity = Column(Integer, ForeignKey('data.activities.id'))
    fk_user = Column(Integer, ForeignKey('data.users.id'), nullable=False)
    timestamp = Column(DateTime, nullable = False)
    fk_status = Column(Integer, ForeignKey('data.status.id'), nullable=False)
    geometry = GeometryColumn('geometry', Geometry(dimension = 2, srid = 4326, spatial_index = True))
    source = Column(Text)

    tags = relationship("A_Tag", backref = backref('event', order_by = id), cascade='all') # cascade to delete tags when event is deleted.
    reviews = relationship("A_Event_Review", backref='event')

    def __init__(self, geometry=None, source=None):
        self.uuid = uuid.uuid4()
        self.timestamp = datetime.datetime.now()
        self.geometry = geometry
        self.source = source

    def __repr__(self):
        return "<A_Event> id [ %s ] | uuid [ %s ] | activity [ %s ] | fk_user [ %s ] | timestamp [ %s ] | fk_status [ %s ] | geometry [ %s ] | source [ %s ]" % (self.id, self.uuid, self.fk_activity, self.fk_user, self.timestamp, self.fk_status, wkb.loads(str(self.geometry.geom_wkb)).wkt, self.source)

    @property
    def __geo_interface__(self):
       id = self.id
       if hasattr(self, '_shape') and self._shape is not None:
           geometry = self._shape
       else:
           geometry = wkb.loads(str(self.geometry.geom_wkb))
       properties = dict(source=self.source)
       return geojson.Feature(id=id, geometry=geometry, properties=properties)

class SH_Event(Base):
    __tablename__ = 'sh_events'
    __table_args__ = {'schema': 'data'}
    id = Column(Integer, primary_key = True)
    uuid = Column(UUID, nullable = False, unique = True)
    fk_stakeholder = Column(Integer, ForeignKey('data.stakeholders.id'))
    fk_user = Column(Integer, ForeignKey('data.users.id'), nullable=False)
    timestamp = Column(DateTime, nullable = False)
    fk_status = Column(Integer, ForeignKey('data.status.id'), nullable=False)
    source = Column(Text)

    tags = relationship("SH_Tag", backref = backref('event', order_by = id), cascade='all') # cascade to delete tags when attribute is deleted.
    reviews = relationship("SH_Event_Review", backref='event')

    def __init__(self, source=None):
        self.uuid = uuid.uuid4()
        self.timestamp = datetime.datetime.now()
        self.source = source

    def __repr__(self):
        return "<SH_Event> id [ %s ] | uuid [ %s ] | fk_stakeholder [ %s ] | fk_user [ %s ] | timestamp [ %s ] | fk_status [ %s ] | source [ %s ]" % (self.id, self.uuid, self.fk_stakeholder, self.fk_user, self.timestamp, self.fk_status, self.source)

class Activity(Base):
    __tablename__ = 'activities'
    __table_args__ = {'schema': 'data'}
    id = Column(Integer, primary_key = True)
    uuid = Column(UUID, nullable = False, unique = True)

    events = relationship("A_Event", backref="activity")

    def __init__(self):
        self.uuid = uuid.uuid4()

    def __repr__(self):
        return "<Activity> id [ %s ] | uuid [ %s ]" % (self.id, self.uuid)

class Stakeholder(Base):
    __tablename__ = 'stakeholders'
    __table_args__ = {'schema': 'data'}
    id = Column(Integer, primary_key = True)
    uuid = Column(UUID, nullable = False, unique = True)

    events = relationship("SH_Event", backref="stakeholder")

    def __init__(self):
        self.uuid = uuid.uuid4()

    def __repr__(self):
        return "<Stakeholder> id [ %s ] | uuid [ %s ]" % (self.id, self.uuid)

class Status(Base):
    __tablename__ = 'status'
    __table_args__ = {'schema': 'data'}
    id = Column(Integer, primary_key = True)
    name = Column(String(255), nullable = False, unique = True)
    description = Column(Text)

    a_events = relationship('A_Event', backref='status')
    sh_events = relationship('SH_Event', backref='status')

    def __init__(self, id, name, description=None):
        self.id = id
        self.name = name
        self.description = description

    def __repr__(self):
        return "<Status> id [ %s ] | name [ %s ] | description [ %s ]" % (self.id, self.name, self.description)

class Language(Base):
    __tablename__ = 'languages'
    __table_args__ = {'schema': 'data'}
    id = Column(Integer, primary_key = True)
    english_name = Column(String(255), nullable = False)
    local_name = Column(String(255), nullable = False)
    
    a_keys = relationship('A_Key', backref='language')
    a_values = relationship('A_Value', backref='language')
    sh_keys = relationship('SH_Key', backref='language')
    sh_values = relationship('SH_Value', backref='language')
    
    def __init__(self, id, english_name, local_name):
        self.id = id
        self.english_name = english_name
        self.local_name = local_name
    
    def __repr__(self):
        return "<Language> id [ %s ] | english_name [ %s ] | local_name [ %s ]" % (self.id, self.english_name, self.local_name)

class Involvement(Base):
    __tablename__ = 'involvements'
    __table_args__ = {'schema': 'data'}
    id = Column(Integer, primary_key = True)
    uuid = Column(UUID, nullable = False, unique = True)
    fk_activity = Column(Integer, ForeignKey('data.activities.id'), nullable = False)
    fk_stakeholder = Column(Integer, ForeignKey('data.stakeholders.id'), nullable = False)
    fk_stakeholder_role = Column(Integer, ForeignKey('data.stakeholder_roles.id'), nullable = False)
    
    activity = relationship("Activity", backref=backref("involvements", order_by = id))
    stakeholder = relationship("Stakeholder", backref=backref("involvements", order_by = id))
    reviews = relationship("Involvement_Review", backref='involvement')

    def __init__(self):
        self.uuid = uuid.uuid4()

    def __repr__(self):
        return "<Involvement> id [ %s ] | uuid [ %s ] | fk_activity [ %s ] | fk_stakeholder [ %s ] | fk_stakeholder_role [ %s ]" % (self.id, self.uuid, self.fk_activity, self.fk_stakeholder, self.fk_stakeholder_role)

class Stakeholder_Role(Base):
    __tablename__ = 'stakeholder_roles'
    __table_args__ = {'schema': 'data'}
    id = Column(Integer, primary_key = True)
    name = Column(String(255), nullable = False, unique = True)
    description = Column(Text)

    involvements = relationship("Involvement", backref="stakeholder_role")

    def __init__(self, id, name, description=None):
        self.id = id
        self.name = name
        self.description = description

    def __repr__(self):
        return "<Stakeholder_Role> id [ %s ] | name [ %s ] | description [ %s ]" % (self.id, self.name, self.description)

users_groups = Table('users_groups', Base.metadata,
                     Column('id', Integer, primary_key = True),
                     Column('fk_user', Integer, ForeignKey('data.users.id'), nullable = False),
                     Column('fk_group', Integer, ForeignKey('data.groups.id'), nullable = False),
                     schema = 'data'
                     )

class User(Base):
    __tablename__ = 'users'
    __table_args__ = {'schema': 'data'}
    id = Column(Integer, primary_key = True)
    uuid = Column(UUID, nullable = False, unique = True)
    username = Column(String(255), nullable = False, unique = True)
    password = Column(String(255), nullable = False)
    email = Column(String(255), nullable = False, unique = True)

    a_events = relationship('A_Event', backref='user')
    sh_events = relationship('SH_Event', backref='user')
    groups = relationship('Group', secondary=users_groups, backref=backref('users', order_by = id))
    a_event_reviews = relationship('A_Event_Review', backref='user')
    sh_event_reviews = relationship('SH_Event_Review', backref='user')
    involvement_review = relationship('Involvement_Review', backref='user')

    def __init__(self, username, password, email):
        self.uuid = uuid.uuid4()
        self.username = username
        self.password = password
        self.email = email

    def __repr__(self):
        return "<User> id [ %s ] | uuid [ %s ] | username [ %s ] | password [ *** ] | email [ %s ]" % (self.id, self.uuid, self.username, self.email)

groups_permissions = Table('groups_permissions', Base.metadata,
                           Column('id', Integer, primary_key = True),
                           Column('fk_group', Integer, ForeignKey('data.groups.id'), nullable = False),
                           Column('fk_permission', Integer, ForeignKey('data.permissions.id'), nullable = False),
                           schema = 'data'
                           )

class Group(Base):
    __tablename__ = 'groups'
    __table_args__ = {'schema': 'data'}
    id = Column(Integer, primary_key = True)
    name = Column(String(255), nullable = False, unique = True)
    description = Column(Text)
    
    permissions = relationship('Permission', secondary=groups_permissions, backref=backref('groups', order_by = id))
    
    def __init__(self, id, name, description=None):
        self.id = id
        self.name = name
        self.description = description

    def __repr__(self):
        return "<Group> id [ %s ] | name [ %s ] | description [ %s ]" % (self.id, self.name, self.description)

class Permission(Base):
    __tablename__ = 'permissions'
    __table_args__ = {'schema': 'data'}
    id = Column(Integer, primary_key = True)
    name = Column(String(255), nullable = False, unique = True)
    description = Column(Text)
    
    def __init__(self, id, name, description=None):
        self.id = id
        self.name = name
        self.description = description

    def __repr__(self):
        return "<Permission> id [ %s ] | name [ %s ] | description [ %s ]" % (self.id, self.name, self.description)

class A_Event_Review(Base):
    __tablename__ = 'a_event_review'
    __table_args__ = {'schema': 'data'}
    id = Column(Integer, primary_key = True)
    uuid = Column(UUID, nullable = False, unique = True)
    fk_a_event = Column(Integer, ForeignKey('data.a_events.id'), nullable = False)
    fk_user = Column(Integer, ForeignKey('data.users.id'), nullable = False)
    timestamp = Column(DateTime, nullable = False)
    fk_review_decision = Column(Integer, ForeignKey('data.review_decisions.id'), nullable = False)
    comment = Column(Text)
    
    def __init__(self, comment=None):
        self.uuid = uuid.uuid4()
        self.timestamp = datetime.datetime.now()
        self.comment = comment
    
    def __repr__(self):
        return "<A_Event_Review> id [ %s ] | uuid [ %s ] | fk_a_event [ %s ] | fk_user [ %s ] | timestamp [ %s ] | fk_review_decision [ %s ] | comment [ %s ]" % (self.id, self.uuid, self.fk_a_event, self.fk_user, self.timestamp, self.fk_review_decision, self.comment)

class SH_Event_Review(Base):
    __tablename__ = 'sh_event_reviews'
    __table_args__ = {'schema': 'data'}
    id = Column(Integer, primary_key = True)
    uuid = Column(UUID, nullable = False, unique = True)
    fk_sh_event = Column(Integer, ForeignKey('data.sh_events.id'), nullable = False)
    fk_user = Column(Integer, ForeignKey('data.users.id'), nullable = False)
    timestamp = Column(DateTime, nullable = False)
    fk_review_decision = Column(Integer, ForeignKey('data.review_decisions.id'), nullable = False)
    comment = Column(Text)
    
    def __init__(self, comment=None):
        self.uuid = uuid.uuid4()
        self.timestamp = datetime.datetime.now()
        self.comment = comment
    
    def __repr__(self):
        return "<SH_Event_Review> id [ %s ] | uuid [ %s ] | fk_sh_event [ %s ] | fk_user [ %s ] | timestamp [ %s ] | fk_review_decision [ %s ] | comment [ %s ]" % (self.id, self.uuid, self.fk_sh_event, self.fk_user, self.timestamp, self.fk_review_decision, self.comment)

class Involvement_Review(Base):
    __tablename__ = 'involvement_reviews'
    __table_args__ = {'schema': 'data'}
    id = Column(Integer, primary_key = True)
    uuid = Column(UUID, nullable = False, unique = True)
    fk_involvement = Column(Integer, ForeignKey('data.involvements.id'), nullable = False)
    fk_user = Column(Integer, ForeignKey('data.users.id'), nullable = False)
    timestamp = Column(DateTime, nullable = False)
    fk_review_decision = Column(Integer, ForeignKey('data.review_decisions.id'), nullable = False)
    comment = Column(Text)
    
    def __init__(self, comment=None):
        self.uuid = uuid.uuid4()
        self.timestamp = datetime.datetime.now()
        self.comment = comment
    
    def __repr__(self):
        return "<Involvement_Review> id [ %s ] | uuid [ %s ] | fk_involvement [ %s ] | fk_user [ %s ] | timestamp [ %s ] | fk_review_decision [ %s ] | comment [ %s ]" % (self.id, self.uuid, self.fk_involvement, self.fk_user, self.timestamp, self.fk_review_decision, self.comment)

class Review_Decision(Base):
    __tablename__ = 'review_decisions'
    __table_args__ = {'schema': 'data'}
    id = Column(Integer, primary_key = True)
    name = Column(String(255), nullable = False, unique = True)
    description = Column(Text)

    a_event_review = relationship('A_Event_Review', backref='review_decision')
    sh_event_review = relationship('SH_Event_Review', backref='review_decision')
    involvement_review = relationship('Involvement_Review', backref='review_decision')

    def __init__(self, id, name, description=None):
        self.id = id
        self.name = name
        self.description = description

    def __repr__(self):
        return "<Review_Decision> id [ %s ] | name [ %s ] | description [ %s ]" % (self.id, self.name, self.description)


#===============================================================================
# class Test_Point(Base):
#    __tablename__ = 'a_events'
#    __table_args__ = {'schema': 'data'}
#    __mapper_args__ = {
#        'include_properties': ['id', 'source']
#    }
#    
#    def __repr__(self):
#        return "<Test_Point> id [ %s ] | source [ %s ]" % (self.id, self.source)
#===============================================================================