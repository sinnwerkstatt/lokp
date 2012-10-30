from lmkp.models.meta import (
    Base,
    DBSession
)

from geoalchemy.utils import from_wkt

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import column_property
import datetime
from sqlalchemy.ext.hybrid import hybrid_property

# registering of uuid needed, done in meta.py
import uuid

from sqlalchemy import (
    Table,
    Column,
    Integer,
    Text,
    String,
    DateTime,
    Unicode,
    ForeignKey
)

from sqlalchemy.orm import (
    relationship,
    backref,
    validates,
    synonym
)

from sqlalchemy.schema import (
    ForeignKeyConstraint,
    PrimaryKeyConstraint,
    UniqueConstraint
)

from sqlalchemy.schema import (
    ForeignKeyConstraint,
    PrimaryKeyConstraint,
    UniqueConstraint
)
from sqlalchemy.orm.exc import NoResultFound

# ...
from shapely import wkb
import geojson

# imports needed for geometry table (A_Events)
from geoalchemy.geometry import Geometry
from geoalchemy.geometry import GeometryColumn
from geoalchemy.geometry import GeometryDDL
from geoalchemy.geometry import Point
from geoalchemy.geometry import Polygon

# Password encyption (drawn from the Pylons project 'Shootout': https://github.com/Pylons/shootout/blob/master/shootout/)
# Contrary to the example above, cryptacular.bcrypt could not be used (problem with Windows?). Instead, cryptacular.pbkdf2 is used.
# As a consequence, the length of the password field had to be extended (60 to 64) compared to example.
# Package description: http://pypi.python.org/pypi/cryptacular/0.5.1
import cryptacular.pbkdf2
crypt = cryptacular.pbkdf2.PBKDF2PasswordManager()
def hash_password(password):
    return unicode(crypt.encode(password))

class A_Key(Base):
    __tablename__ = 'a_keys'
    __table_args__ = (
            ForeignKeyConstraint(['fk_a_key'], ['data.a_keys.id']),
            ForeignKeyConstraint(['fk_language'], ['data.languages.id']),
            {'schema': 'data'}
            )
    id = Column(Integer, primary_key = True)
    fk_a_key = Column(Integer)
    fk_language = Column(Integer)
    key = Column(String(255), nullable = False)

    fk_key = column_property(fk_a_key)
    
    translations = relationship('A_Key', backref = backref('original', remote_side = [id]))
    tags = relationship('A_Tag', backref = 'key')
    
    def __init__(self, key):
        self.key = key
    
    def __repr__(self):
        return "<A_Key> id [ %s ] | fk_a_key [ %s ] | fk_language [ %s ] | key [ %s ]" % (self.id, self.fk_a_key, self.fk_language, self.key)

    def to_json(self):
        return self.key

class SH_Key(Base):
    __tablename__ = 'sh_keys'
    __table_args__ = (
            ForeignKeyConstraint(['fk_sh_key'], ['data.sh_keys.id']),
            ForeignKeyConstraint(['fk_language'], ['data.languages.id']),
            {'schema': 'data'}
            )
    id = Column(Integer, primary_key = True)
    fk_sh_key = Column(Integer)
    fk_language = Column(Integer)
    key = Column(String(255), nullable = False)

    fk_key = column_property(fk_sh_key)
    
    translations = relationship('SH_Key', backref = backref('original', remote_side = [id]))
    tags = relationship('SH_Tag', backref = 'key')
    
    def __init__(self, key):
        self.key = key
    
    def __repr__(self):
        return "<SH_Key> id [ %s ] | fk_sh_key [ %s ] | fk_language [ %s ] | key [ %s ]" % (self.id, self.fk_sh_key, self.fk_language, self.key)

class A_Value(Base):
    __tablename__ = 'a_values'
    __table_args__ = (
            ForeignKeyConstraint(['fk_a_value'], ['data.a_values.id']),
            ForeignKeyConstraint(['fk_language'], ['data.languages.id']),
            {'schema': 'data'}
            )
    id = Column(Integer, primary_key = True)
    fk_a_value = Column(Integer)
    fk_language = Column(Integer, nullable = False)
    value = Column(Text)

    fk_value = column_property(fk_a_value)
    
    translations = relationship('A_Value', backref = backref('original', remote_side = [id]))
    tags = relationship('A_Tag', backref = 'value')
    
    def __init__(self, value):
        self.value = value
    
    def __repr__(self):

        return "<A_Value> id [ %s ] | fk_a_value [ %s ] | fk_language [ %s ] | value [ %s ]" % (self.id, self.fk_a_value, self.fk_language, self.value)

class SH_Value(Base):
    __tablename__ = 'sh_values'
    __table_args__ = (
            ForeignKeyConstraint(['fk_sh_value'], ['data.sh_values.id']),
            ForeignKeyConstraint(['fk_language'], ['data.languages.id']),
            {'schema': 'data'}
            )
    id = Column(Integer, primary_key = True)
    fk_sh_value = Column(Integer)
    fk_language = Column(Integer)
    value = Column(Text, nullable = False)

    fk_value = column_property(fk_sh_value)
    
    translations = relationship('SH_Value', backref = backref('original', remote_side = [id]))
    tags = relationship('SH_Tag', backref = 'value')
    
    def __init__(self, value):
        self.value = value
    
    def __repr__(self):
        return "<SH_Value> id [ %s ] | fk_sh_value [ %s ] | fk_language [ %s ] | value [ %s ]" % (self.id, self.fk_sh_value, self.fk_language, self.value)

class A_Tag(Base):
    __tablename__ = 'a_tags'
    __table_args__ = (
            ForeignKeyConstraint(['fk_a_tag_group'], ['data.a_tag_groups.id']),
            ForeignKeyConstraint(['fk_a_key'], ['data.a_keys.id']),
            ForeignKeyConstraint(['fk_a_value'], ['data.a_values.id']),
            {'schema': 'data'}
            )
    id = Column(Integer, primary_key = True)
    fk_a_tag_group = Column(Integer, nullable = False)
    fk_a_key = Column(Integer, nullable = False)
    fk_a_value = Column(Integer, nullable = False)

    fk_tag_group = column_property(fk_a_tag_group)
    fk_key = column_property(fk_a_key)
    fk_value = column_property(fk_a_value)

    def __init__(self):
        pass

    def __repr__(self):
        return "<A_Tag> id [ %s ] | fk_a_tag_group [ %s ] | fk_a_key [ %s ] | fk_a_value [ %s ]" % (self.id, self.fk_a_tag_group, self.fk_a_key, self.fk_a_value)

    def to_json(self):
        return {'id': self.id, 'key': self.key.key, 'value': self.value.value }

class SH_Tag(Base):
    __tablename__ = 'sh_tags'
    __table_args__ = (
            ForeignKeyConstraint(['fk_sh_tag_group'], ['data.sh_tag_groups.id']),
            ForeignKeyConstraint(['fk_sh_key'], ['data.sh_keys.id']),
            ForeignKeyConstraint(['fk_sh_value'], ['data.sh_values.id']),
            {'schema': 'data'}
            )
    id = Column(Integer, primary_key = True)
    fk_sh_tag_group = Column(Integer, nullable = False)
    fk_sh_key = Column(Integer, nullable = False)
    fk_sh_value = Column(Integer, nullable = False)

    fk_tag_group = column_property(fk_sh_tag_group)
    fk_key = column_property(fk_sh_key)
    fk_value = column_property(fk_sh_value)

    def __init__(self):
        pass

    def __repr__(self):
        return "<SH_Tag> id [ %s ] | fk_sh_tag_group [ %s ] | fk_sh_key [ %s ] | fk_sh_value [ %s ]" % (self.id, self.fk_sh_tag_group, self.fk_sh_key, self.fk_sh_value)

    def to_json(self):
        return {'id': self.id, 'key': self.key.key, 'value': self.value.value }

class A_Tag_Group(Base):
    __tablename__ = 'a_tag_groups'
    __table_args__ = (
            ForeignKeyConstraint(['fk_activity'], ['data.activities.id']),
            ForeignKeyConstraint(['fk_a_tag'], ['data.a_tags.id'], use_alter = True, name = 'fk_a_tag'),
            {'schema': 'data'}
            )
    id = Column(Integer, primary_key = True)
    tg_id = Column(Integer, nullable = False)
    fk_activity = Column(Integer, nullable = False)
    fk_a_tag = Column(Integer, nullable = True)
    geometry = GeometryColumn('geometry', Geometry(dimension = 2, srid = 4326, spatial_index = True))
    valid_from = Column(DateTime)
    valid_to = Column(DateTime)

    fk_tag = column_property(fk_a_tag)

    tags = relationship("A_Tag", backref = backref('tag_group', order_by = id), primaryjoin = id==A_Tag.fk_a_tag_group)
    main_tag = relationship("A_Tag", primaryjoin = fk_a_tag==A_Tag.id, post_update = True)

    def __init__(self, tg_id, geometry=None, valid_from=None, valid_to=None):
        self.tg_id = tg_id
        self.geometry = geometry
        self.valid_from = (valid_from if valid_from is not None
            else datetime.datetime.now())
        self.valid_to = valid_to
    
    def __repr__(self):
        if self.geometry == None:
            geom = '-'
        else:
            geom = wkb.loads(str(self.geometry.geom_wkb)).wkt
        return (
            '<A_Tag_Group> id [ %s ] | tg_id [%s] | fk_activity [ %s ] | ' +
            'fk_a_tag [ %s ] | geometry [ %s ] | valid_from [ %s ] | ' +
            'valid_to [ %s ]' %
            (self.id, self.tg_id, self.fk_activity, self.fk_a_tag, geom,
            self.valid_from, self.valid_to)
        )

    def to_json(self):
        geometry = None
        if self.geometry is not None:
            shape = wkb.loads(str(self.geometry.geom_wkb))
            geometry = from_wkt(shape.wkt)
        return {'id': self.id, 'geometry': geometry, 'tags': [t.to_json() for t in self.tags]}

GeometryDDL(A_Tag_Group.__table__)

class SH_Tag_Group(Base):
    __tablename__ = 'sh_tag_groups'
    __table_args__ = (
            ForeignKeyConstraint(['fk_stakeholder'], ['data.stakeholders.id']),
            ForeignKeyConstraint(['fk_sh_tag'], ['data.sh_tags.id'], use_alter = True, name = 'fk_sh_tag'),
            {'schema': 'data'}
            )
    id = Column(Integer, primary_key = True)
    tg_id = Column(Integer, nullable = False)
    fk_stakeholder = Column(Integer, nullable = False)
    fk_sh_tag = Column(Integer, nullable = True)
    valid_from = Column(DateTime)
    valid_to = Column(DateTime)
    
    tags = relationship("SH_Tag", backref = backref('tag_group', order_by = id), primaryjoin = id==SH_Tag.fk_sh_tag_group)
    main_tag = relationship("SH_Tag", primaryjoin = fk_sh_tag==SH_Tag.id, post_update = True)

    fk_tag = column_property(fk_sh_tag)

    def __init__(self, tg_id, valid_from=None, valid_to=None):
        self.tg_id = tg_id
        self.valid_from = (valid_from if valid_from is not None
            else datetime.datetime.now())
        self.valid_to = valid_to

    def __repr__(self):
        return (
            '<SH_Tag_Group> id [ %s ] | tg_id [%s] | fk_stakeholder [ %s ] | ' +
            'fk_sh_tag [ %s ] | valid_from [ %s ] | valid_to [ %s ]' %
            (self.id, self.tg_id, self.fk_stakeholder, self.fk_sh_tag,
            self.valid_from, self.valid_to)
        )

    def to_json(self):
        return {'id': self.id, 'tags': [t.to_json() for t in self.tags]}

class Activity(Base):
    __tablename__ = 'activities'
    __table_args__ = (
            ForeignKeyConstraint(['fk_status'], ['data.status.id']),
            ForeignKeyConstraint(['fk_changeset'], ['data.changesets.id']),
            ForeignKeyConstraint(['fk_user_review'], ['data.users.id']),
            {'schema': 'data'}
            )
    id = Column(Integer, primary_key = True)
    activity_identifier = Column(UUID, nullable = False)
    fk_changeset = Column(Integer, nullable = False)
    point = GeometryColumn('point', Point(dimension = 2, srid = 4326, spatial_index = True))
    fk_status = Column(Integer, nullable = False)
    version = Column(Integer, nullable = False)
    previous_version = Column(Integer)
    fk_user_review = Column(Integer)
    timestamp_review = Column(DateTime)
    comment_review = Column(Text)

    tag_groups = relationship("A_Tag_Group", backref = backref('activity', order_by = id))
    involvements = relationship("Involvement", backref = backref('activity', order_by = id))

    #identifier = column_property(activity_identifier)
    @hybrid_property
    def identifier(self):
        return self.activity_identifier

    def __init__(self, activity_identifier, version, previous_version=None, 
        point=None, timestamp_review=None, comment_review=None):
        self.activity_identifier = activity_identifier
        self.version = version
        self.previous_version = previous_version
        self.point = point
        self.timestamp_review = timestamp_review
        self.comment_review = comment_review

    def __repr__(self):
        if self.point == None:
            geom = '-'
        else:
            geom = wkb.loads(str(self.point.geom_wkb)).wkt
        return (
            '<Activity> id [ %s ] | activity_identifier [ %s ] | ' +
            'fk_changeset [ %s ] | point [ %s ] | fk_status [ %s ] | ' +
            'version [ %s ] | previous_version [ %s ] | fk_user_review [ %s ] '+
            '| timestamp_review [ %s ] | comment_review [ %s ]' %
            (self.id, self.activity_identifier, self.fk_changeset, geom,
            self.fk_status, self.version, self.previous_version,
            self.fk_user_review, self.timestamp_review, self.comment_review)
        )
    
    @property
    def __geo_interface__(self):
       id = self.id
       if hasattr(self, '_shape') and self._shape is not None:
           geometry = self._shape
       else:
           geometry = wkb.loads(str(self.point.geom_wkb))
       properties = dict(source=self.source)
       return geojson.Feature(id=id, geometry=geometry, properties=properties)

    def get_comments(self):
        return DBSession.query(Comment).filter(Comment.activity_identifier == self.activity_identifier).all()

    def to_json(self):
        # The geometry as Shapely object
        geometry = None
        if self.point is not None:
            shape = wkb.loads(str(self.point.geom_wkb))
            geometry = from_wkt(shape.wkt)
        return {'id': str(self.activity_identifier), 'version': self.version, 'geometry': geometry, 'taggroups': [t.to_json() for t in self.tag_groups]}

GeometryDDL(Activity.__table__)

class Stakeholder(Base):
    __tablename__ = 'stakeholders'
    __table_args__ = (
            ForeignKeyConstraint(['fk_status'], ['data.status.id']),
            ForeignKeyConstraint(['fk_changeset'], ['data.changesets.id']),
            ForeignKeyConstraint(['fk_user_review'], ['data.users.id']),
            {'schema': 'data'}
            )
    id = Column(Integer, primary_key = True)
    stakeholder_identifier = Column(UUID, nullable = False)
    fk_changeset = Column(Integer, nullable = False)
    fk_status = Column(Integer, nullable = False)
    version = Column(Integer, nullable = False)
    previous_version = Column(Integer)
    fk_user_review = Column(Integer)
    timestamp_review = Column(DateTime)
    comment_review = Column(Text)

    tag_groups = relationship("SH_Tag_Group", backref = backref('stakeholder', order_by = id))
    involvements = relationship("Involvement", backref = backref('stakeholder', order_by = id))

    @hybrid_property
    def identifier(self):
        return self.stakeholder_identifier

    def __init__(self, activity_identifier, version, previous_version=None,
        timestamp_review=None, comment_review=None):
        self.activity_identifier = activity_identifier
        self.version = version
        self.previous_version = previous_version
        self.timestamp_review = timestamp_review
        self.comment_review = comment_review

    def __repr__(self):
        return (
            '<Activity> id [ %s ] | activity_identifier [ %s ] | ' +
            'fk_changeset [ %s ] | fk_status [ %s ] | version [ %s ] | ' +
            'previous_version [ %s ] | fk_user_review [ %s ] | '+
            'timestamp_review [ %s ] | comment_review [ %s ]' %
            (self.id, self.activity_identifier, self.fk_changeset,
            self.fk_status, self.version, self.previous_version,
            self.fk_user_review, self.timestamp_review, self.comment_review)
        )

    def get_comments(self):
        return DBSession.query(Comment).filter(Comment.stakeholder_identifier == self.stakeholder_identifier).all()

    def to_json(self):
        return {'id': str(self.stakeholder_identifier), 'version': self.version, 'taggroups': [t.to_json() for t in self.tag_groups]}


class Changeset(Base):
    __tablename__ = 'changesets'
    __table_args__ = (
            ForeignKeyConstraint(['fk_user'], ['data.users.id']),
            {'schema': 'data'}
            )
    id = Column(Integer, primary_key = True)
    fk_user = Column(Integer, nullable = False)
    timestamp = Column(DateTime, nullable = False)
    source = Column(Text)
    diff = Column(Text)

    activities = relationship('Activity', backref='changeset')
    stakeholders = relationship('Stakeholder', backref='changeset')

    def __init__(self, source=None, diff=None):
        self.timestamp = datetime.datetime.now()
        self.source = source
        self.diff = diff

    def __repr__(self):
        return (
            '<Changeset> id [ %s ] | fk_user [ %s ] | timestamp [ %s ] | ' +
            'source [ %s ] | diff [ %s ]' %
            (self.id, self.fk_user, self.timestamp, self.source, self.diff)
        )

"""
class SH_Changeset(Base):
    __tablename__ = 'sh_changesets'
    __table_args__ = (
            ForeignKeyConstraint(['fk_user'], ['data.users.id']),
            ForeignKeyConstraint(['fk_stakeholder'], ['data.stakeholders.id']),
            {'schema': 'data'}
            )
    id = Column(Integer, primary_key = True)
    fk_user = Column(Integer, nullable = False)
    timestamp = Column(DateTime, nullable = False)
    source = Column(Text)
    fk_stakeholder = Column(Integer, nullable = False)
    previous_version = Column(Integer)

    reviews = relationship("SH_Changeset_Review", backref='changeset')

    def __init__(self, source=None, previous_version=None):
        self.timestamp = datetime.datetime.now()
        self.source = source
        self.previous_version = previous_version

    def __repr__(self):
        return "<SH_Changeset> id [ %s ] | fk_user [ %s ] | timestamp [ %s ] | source [ %s ] | fk_stakeholder [ %s ] | previous_version [ %s ]" % (self.id, self.fk_user, self.timestamp, self.source, self.fk_stakeholder, self.previous_version)
"""

class Status(Base):
    __tablename__ = 'status'
    __table_args__ = (
            {'schema': 'data'}
            )
    id = Column(Integer, primary_key = True)
    name = Column(String(255), nullable = False, unique = True)
    description = Column(Text)

    activities = relationship('Activity', backref='status')
    stakeholders = relationship('Stakeholder', backref='status')

    def __init__(self, id, name, description=None):
        self.id = id
        self.name = name
        self.description = description

    def __repr__(self):
        return "<Status> id [ %s ] | name [ %s ] | description [ %s ]" % (self.id, self.name, self.description)

class Language(Base):
    __tablename__ = 'languages'
    __table_args__ = (
            {'schema': 'data'}
            )
    id = Column(Integer, primary_key = True)
    english_name = Column(String(255), nullable = False)
    local_name = Column(String(255), nullable = False)
    locale = Column(String(31), nullable = False)
    
    a_keys = relationship('A_Key', backref='language')
    a_values = relationship('A_Value', backref='language')
    sh_keys = relationship('SH_Key', backref='language')
    sh_values = relationship('SH_Value', backref='language')
    
    def __init__(self, id, english_name, local_name, locale):
        self.id = id
        self.english_name = english_name
        self.local_name = local_name
        self.locale = locale
    
    def __repr__(self):
        return "<Language> id [ %s ] | english_name [ %s ] | local_name [ %s ] | locale [ %s ]" % (self.id, self.english_name, self.local_name, self.locale)

class Involvement(Base):
    __tablename__ = 'involvements'
    __table_args__ = (
            ForeignKeyConstraint(['fk_activity'], ['data.activities.id']),
            ForeignKeyConstraint(['fk_stakeholder'], ['data.stakeholders.id']),
            ForeignKeyConstraint(['fk_stakeholder_role'], ['data.stakeholder_roles.id']),
            {'schema': 'data'}
            )
    id = Column(Integer, primary_key = True)
    fk_activity = Column(Integer, nullable = False)
    fk_stakeholder = Column(Integer, nullable = False)
    fk_stakeholder_role = Column(Integer, nullable = False)
      
    comments = relationship("Comment", backref='involvement')

    def __init__(self):
        pass

    def __repr__(self):
        return "<Involvement> id [ %s ] | fk_activity [ %s ] | fk_stakeholder [ %s ] | fk_stakeholder_role [ %s ]" % (self.id, self.fk_activity, self.fk_stakeholder, self.fk_stakeholder_role)

class Stakeholder_Role(Base):
    __tablename__ = 'stakeholder_roles'
    __table_args__ = (
            {'schema': 'data'}
            )
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

users_profiles = Table('users_profiles', Base.metadata,
                        Column('id', Integer, primary_key = True),
                        Column('fk_user', Integer, ForeignKey('data.users.id'), nullable = False),
                        Column('fk_profile', Integer, ForeignKey('data.profiles.id'), nullable = False),
                        schema = 'data'
                        )

class User(Base):
    __tablename__ = 'users'
    __table_args__ = (
            {'schema': 'data'}
            )
    id = Column(Integer, primary_key = True)
    uuid = Column(UUID, nullable = False, unique = True)
    username = Column(String(255), nullable = False)
    email = Column(String(255), nullable = False)

    changesets = relationship('Changeset', backref='user')
    groups = relationship('Group', secondary=users_groups, backref=backref('users', order_by = id))
    profiles = relationship('Profile', secondary=users_profiles, backref=backref('users', order_by = id))
    comments = relationship('Comment', backref='user')
    a_reviews = relationship('Activity', backref='user_review')
    sh_reviews = relationship('Stakeholder', backref='user_review')

    # password encryption
    _password = Column('password', Unicode(64))
    
    def _get_password(self):
        return self._password
    
    def _set_password(self, password):
        self._password = hash_password(password)

    password = property(_get_password, _set_password)
    password = synonym('_password', descriptor=password)

    @classmethod
    def get_by_username(cls, username):
        return DBSession.query(cls).filter(cls.username == username).first()

    """
    Call this method to check if login credentials are correct.
    Returns TRUE if correct.
    """
    @classmethod
    def check_password(cls, username, password):
        user = cls.get_by_username(username)
        if not user:
            return False
        return crypt.check(user.password, password)

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
    __table_args__ = (
            {'schema': 'data'}
            )
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
    __table_args__ = (
            {'schema': 'data'}
            )
    id = Column(Integer, primary_key = True)
    name = Column(String(255), nullable = False, unique = True)
    description = Column(Text)
    
    def __init__(self, id, name, description=None):
        self.id = id
        self.name = name
        self.description = description

    def __repr__(self):
        return "<Permission> id [ %s ] | name [ %s ] | description [ %s ]" % (self.id, self.name, self.description)

class Profile(Base):
    __tablename__ = 'profiles'
    __table_args__ = {'schema': 'data'}
    id = Column(Integer, primary_key = True)
    code = Column(String(255), nullable = False, unique = True)
    geometry = GeometryColumn('polygon', Polygon(dimension = 2, srid = 4326, spatial_index = True))

    def __init__(self, code, geometry):
        self.code = code
        self.geometry = geometry
    
    def __repr__(self):
        if self.geometry == None:
            geom = '-'
        else:
            geom = wkb.loads(str(self.geometry.geom_wkb)).wkt
        return '<Profile> id [ %s ] | code [ %s ] | geometry [ %s ]' % (self.id, self.code, geom)

    def to_json(self):
        geometry = None
        if self.geometry is not None:
            shape = wkb.loads(str(self.geometry.geom_wkb))
            geometry = from_wkt(shape.wkt)
        return {'id': self.id, 'code': self.code, 'geometry': geometry}

GeometryDDL(Profile.__table__)

"""
class A_Changeset_Review(Base):
    __tablename__ = 'a_changeset_review'
    __table_args__ = (
            ForeignKeyConstraint(['fk_a_changeset'], ['data.a_changesets.id']),
            ForeignKeyConstraint(['fk_user'], ['data.users.id']),
            ForeignKeyConstraint(['fk_review_decision'], ['data.review_decisions.id']),
            {'schema': 'data'}
            )
    id = Column(Integer, primary_key = True)
    fk_a_changeset = Column(Integer, nullable = False)
    fk_user = Column(Integer, nullable = False)
    timestamp = Column(DateTime, nullable = False)
    fk_review_decision = Column(Integer, nullable = False)
    comment = Column(Text)
    
    def __init__(self, comment=None):
        self.timestamp = datetime.datetime.now()
        self.comment = comment
    
    def __repr__(self):
        return "<A_Changeset_Review> id [ %s ] | fk_a_changeset [ %s ] | fk_user [ %s ] | timestamp [ %s ] | fk_review_decision [ %s ] | comment [ %s ]" % (self.id, self.fk_a_changeset, self.fk_user, self.timestamp, self.fk_review_decision, self.comment)

class SH_Changeset_Review(Base):
    __tablename__ = 'sh_changeset_reviews'
    __table_args__ = (
            ForeignKeyConstraint(['fk_sh_changeset'], ['data.sh_changesets.id']),
            ForeignKeyConstraint(['fk_user'], ['data.users.id']),
            ForeignKeyConstraint(['fk_review_decision'], ['data.review_decisions.id']),
            {'schema': 'data'}
            )
    id = Column(Integer, primary_key = True)
    fk_sh_changeset = Column(Integer, nullable = False)
    fk_user = Column(Integer, nullable = False)
    timestamp = Column(DateTime, nullable = False)
    fk_review_decision = Column(Integer, nullable = False)
    comment = Column(Text)
    
    def __init__(self, comment=None):
        self.timestamp = datetime.datetime.now()
        self.comment = comment
    
    def __repr__(self):
        return "<SH_Changeset_Review> id [ %s ] | fk_sh_changeset [ %s ] | fk_user [ %s ] | timestamp [ %s ] | fk_review_decision [ %s ] | comment [ %s ]" % (self.id, self.fk_sh_changeset, self.fk_user, self.timestamp, self.fk_review_decision, self.comment)

class Review_Decision(Base):
    __tablename__ = 'review_decisions'
    __table_args__ = (
            {'schema': 'data'}
            )
    id = Column(Integer, primary_key = True)
    name = Column(String(255), nullable = False, unique = True)
    description = Column(Text)

    a_changeset_reviews = relationship('A_Changeset_Review', backref='review_decision')
    sh_changeset_reviews = relationship('SH_Changeset_Review', backref='review_decision')

    def __init__(self, id, name, description=None):
        self.id = id
        self.name = name
        self.description = description

    def __repr__(self):
        return "<Review_Decision> id [ %s ] | name [ %s ] | description [ %s ]" % (self.id, self.name, self.description)
"""
    
class Comment(Base):
    __tablename__ = 'comments'
    __table_args__ = (
        ForeignKeyConstraint(['fk_user'], ['data.users.id']),
        ForeignKeyConstraint(['fk_involvement'], ['data.involvements.id']),
        {'schema': 'data'}
        )
    id = Column(Integer, primary_key = True)
    comment = Column(Text, nullable = False)
    timestamp = Column(DateTime, nullable = False)
    fk_user = Column(Integer)
    activity_identifier = Column(UUID)
    stakeholder_identifier = Column(UUID)
    fk_involvement = Column(Integer)

    def __init__(self, comment, activity_identifier = None, stakeholder_identifier = None):
        self.timestamp = datetime.datetime.now()
        self.comment = comment
        self.activity_identifier = activity_identifier
        self.stakeholder_identifier = stakeholder_identifier
    
    def __repr__(self):
        return "<Comment> id [ %s ] | comment [ %s ] | timestamp [ %s ] | fk_user [ %s ] | fk_activity [ %s ] | fk_stakeholder [ %s ] | fk_involvement [ %s ]" % (self.id, self.comment, self.timestamp, self.fk_user, self.fk_activity, self.fk_stakeholder, self.fk_involvement)

    def get_activity(self):
        try:
            return DBSession.query(Activity).filter(Activity.activity_identifier == self.activity_identifier).filter(Activity.fk_status == 2).one()
        except NoResultFound:
            return None
    
    def get_stakeholder(self):
        try:
            return DBSession.query(Stakeholder).filter(Stakeholder.stakeholder_identifier == self.stakeholder_identifier).filter(Stakeholder.fk_status == 2).one()
        except NoResultFound:
            return None
