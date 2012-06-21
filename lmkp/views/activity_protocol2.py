from geoalchemy import WKBSpatialElement
from geoalchemy.functions import functions
from lmkp.config import config_file_path
from lmkp.models.database_objects import *
from lmkp.views.protocol import Feature
from lmkp.views.protocol import Protocol
from lmkp.views.protocol import Tag
from lmkp.views.protocol import TagGroup
import logging
from pyramid.httpexceptions import HTTPBadRequest
from pyramid.httpexceptions import HTTPCreated
from pyramid.httpexceptions import HTTPFound
from pyramid.httpexceptions import HTTPNotFound
from pyramid.i18n import get_localizer
from shapely.geometry import asShape
from shapely.geometry.polygon import Polygon
import simplejson as json
from sqlalchemy import alias
from sqlalchemy import distinct
from sqlalchemy import func
from sqlalchemy import join
from sqlalchemy import select
from sqlalchemy.orm.util import AliasedClass
from sqlalchemy.orm.util import class_mapper
from sqlalchemy.sql.expression import and_
from sqlalchemy.sql.expression import asc
from sqlalchemy.sql.expression import cast
from sqlalchemy.sql.expression import desc
from sqlalchemy.sql.expression import or_
from sqlalchemy.types import Float
import uuid
import yaml

log = logging.getLogger(__name__)

class ActivityFeature2(Feature):
    """
    Overwrites the super class Feature and adds the geometry property
    """

    def __init__(self, guid, order_value, geometry=None, version=None, diff_info=None, ** kwargs):
        self._taggroups = []
        self._guid = guid
        self._order_value = order_value
        self._geometry = geometry
        self._version = version
        self._diff_info = diff_info

    def to_table(self):
        """
        Returns a JSON compatible representation of this object
        """
        tg = []
        for t in self._taggroups:
            tg.append(t.to_table())

        geometry = None

        try:
            geom = wkb.loads(str(self._geometry.geom_wkb))
            geometry = {}
            geometry['type'] = 'Point'
            geometry['coordinates'] = [geom.x, geom.y]
        except AttributeError:
            pass

        ret = {'id': self._guid, 'taggroups': tg}

        if geometry is not None:
            ret['geometry'] = geometry

        if self._version is not None:
            ret['version'] = self._version
        if self._diff_info is not None:
            for k in self._diff_info:
                ret[k] = self._diff_info[k]

        return ret

class ActivityProtocol2(Protocol):

    def __init__(self, Session):

        self.Session = Session

    def read(self, request, filter=None, uid=None):

        # Query the database
        activities, count = self._query(request, limit=self._get_limit(request), offset=self._get_offset(request), filter=filter, uid=uid)

        return {'total': count, 'data': [a.to_table() for a in activities]}

    def history(self, request, uid, status_list=None):
        
        # Query the database
        activities, count = self._history(request, uid, status_list)
        
        return {'total': count, 'data': [a.to_table() for a in activities]}

    def create(self, request):
        """
        Add or update activities
        """
        
        raw = request.json_body

        # Check if the json body is a valid diff file
        #if 'create' not in raw and 'modify' not in raw and 'delete' not in raw:
        if 'activities' not in raw:
            return HTTPBadRequest(detail="Not a valid format")

        for activity in raw['activities']:
            self._handle_activity(request, activity)

        # Return the newly created object with 201 Created HTTP code status
        return HTTPCreated(detail="ok")

    def _handle_activity(self, request, activity_dict, status='pending'):
        """
        """

        # If this activity does not have an id then create a new activity
        if 'id' not in activity_dict:
            self._create_activity(request, activity_dict, status=status)
            return

        # Get the identifier from the request
        identifier = activity_dict['id']
        old_version = activity_dict['version'] if 'version' in activity_dict else None

        # Try to get the activity from the database with this id
        db_a = self.Session.query(Activity).\
            filter(Activity.activity_identifier == identifier).\
            filter(Activity.version == old_version).\
            first()

        # If no activity is found, create a new activity
        if db_a == None:
            self._create_activity(request, activity_dict, identifier=identifier, status=status)
            return
        
        # Update the activity:
        # The basic idea is to deep copy the previous version and control during
        # the copying if a tag needs to be deleted or not. At the end new tags
        # and new taggroups are added.
        
        # Query latest version of current activity (used to increase version by 1)
        latest_version = self.Session.query(Activity).\
            filter(Activity.activity_identifier == identifier).\
            order_by(desc(Activity.version)).\
            first()
            
        new_activity = Activity(activity_identifier=db_a.activity_identifier,
                                version=(latest_version.version + 1),
                                point=db_a.point)
        new_activity.tag_groups = []
        # Set the activity status to pending
        new_activity.status = self.Session.query(Status).filter(Status.name == status).first()
        # Add it to the database
        self.Session.add(new_activity)

        # Loop the tag groups from the previous version and copy it to the new
        # version with its tags
        for db_taggroup in self.Session.query(A_Tag_Group).filter(A_Tag_Group.fk_activity == db_a.id):

            # Create a new tag group and add it to the new activity version
            new_taggroup = A_Tag_Group()
            new_activity.tag_groups.append(new_taggroup)

            # And loop the tags
            for db_tag in self.Session.query(A_Tag).filter(A_Tag.fk_a_tag_group == db_taggroup.id):

                # Before copying the tag, make sure that it is not to delete
                copy_tag = True
                for taggroup_dict in activity_dict['taggroups']:
                    if 'id' in taggroup_dict and taggroup_dict['id'] == db_taggroup.id:
                        # Check which tags we have to edit
                        for tag_dict in taggroup_dict['tags']:
                            if 'id' in tag_dict and tag_dict['id'] == db_tag.id:
                                # Yes, it is THIS tag
                                if tag_dict['op'] == 'delete':
                                    copy_tag = False

                # Create and append the new tag only if requested
                if copy_tag:
                    # Get the key and value SQLAlchemy object
                    k = self.Session.query(A_Key).get(db_tag.fk_a_key)
                    v = self.Session.query(A_Value).get(db_tag.fk_a_value)
                    new_tag = A_Tag()
                    new_taggroup.tags.append(new_tag)
                    new_tag.key = k
                    new_tag.value = v

                    # Set the main tag
                    if db_taggroup.main_tag == db_tag:
                        new_taggroup.main_tag = new_tag

            # Next step is to add new tags to this tag group without existing ids
            for taggroup_dict in activity_dict['taggroups']:
                if 'id' in taggroup_dict and taggroup_dict['id'] == db_taggroup.id:
                    for tag_dict in taggroup_dict['tags']:
                        if 'id' not in tag_dict and tag_dict['op'] == 'add':
                            new_tag = self._create_tag(request, new_taggroup.tags, tag_dict['key'], tag_dict['value'])
                            # Set the main tag
                            if 'main_tag' in taggroup_dict:
                                if taggroup_dict['main_tag']['key'] == new_tag.key.key and taggroup_dict['main_tag']['value'] == new_tag.value.value:
                                    new_taggroup.main_tag = new_tag

        # Finally new tag groups (without id) needs to be added
        # (and loop all again)
        for taggroup_dict in activity_dict['taggroups']:
            if taggroup_dict['id'] is None and taggroup_dict['op'] == 'add':
                new_taggroup = A_Tag_Group()
                new_activity.tag_groups.append(new_taggroup)
                for tag_dict in taggroup_dict['tags']:
                    new_tag = self._create_tag(request, new_taggroup.tags, tag_dict['key'], tag_dict['value'])
                    # Set the main tag
                    if 'main_tag' in taggroup_dict:
                        if taggroup_dict['main_tag']['key'] == new_tag.key.key and taggroup_dict['main_tag']['value'] == new_tag.value.value:
                            new_taggroup.main_tag = new_tag

        self._add_changeset(request, new_activity, old_version)

    def _create_tag(self, request, parent, key, value):
        """
        Creates a new SQLAlchemy tag object and appends it to the parent list.
        """
        # The key has to be already in the database
        k = self.Session.query(A_Key).filter(A_Key.key == key).first()

        # If the value is not yet in the database, create a new value
        v = self.Session.query(A_Value).filter(A_Value.value == unicode(value)).first()
        if v is None:
            v = A_Value(value=value)
            v.fk_language = 1

        # Create a new tag with key and value and append it to the parent tag group
        a_tag = A_Tag()
        parent.append(a_tag)
        a_tag.key = k
        a_tag.value = v

        # Return the newly created tag
        return a_tag

    def _create_activity(self, request, activity, ** kwargs):
        """
        Creates a new activity. As keyword arguments 'identifier' and 'status'
        are allowed.
        """

        if 'identifier' in kwargs:
            identifier = kwargs['identifier']
        status = 'pending'
        if 'status' in kwargs:
            status = kwargs['status']

        # Create a new unique identifier if not set
        if identifier is None:
            identifier = uuid.uuid4()
        # The initial version is 1 of course
        version = 1

        # Try to get the geometry
        try:
            geom = geojson.loads(json.dumps(activity['geometry']),
                                 object_hook=geojson.GeoJSON.to_instance)

            # The geometry
            shape = asShape(geom)
            # Create a new activity and add a representative point to the activity
            new_activity = Activity(activity_identifier=identifier, version=version, point=shape.representative_point().wkt)
        except KeyError:
            # If no geometry is submitted, create a new activity without a geometry
            new_activity = Activity(activity_identifier=identifier, version=version)

        new_activity.tag_groups = []
        # Set the activity status to pending
        new_activity.status = self.Session.query(Status).filter(Status.name == status).first()
        # Add it to the database
        self.Session.add(new_activity)

        # Loop all tag groups
        for taggroup in activity['taggroups']:

            db_taggroup = A_Tag_Group()
            new_activity.tag_groups.append(db_taggroup)

            # Reset the main_tag string
            main_tag = None
            main_tag_key = None
            main_tag_value = None
            # Try to get the main_tag and its key and value from the input JSON
            # file. The main_tag is not mandatory.
            try:
                main_tag = taggroup['main_tag']
                main_tag_key = main_tag['key']
                main_tag_value = main_tag['value']
            except KeyError:
                pass

            # Loop all tags within a tag group
            for tag in taggroup['tags']:

                # Add the tag only if the op property is set to add
                if 'op' not in tag:
                    continue
                elif tag['op'] != 'add':
                    continue

                # Get the key and the value of the current tag
                key = tag['key']
                value = tag['value']

                # Check if the key and value are allowed by the global yaml
                if not self._key_value_is_valid(request, key, value):
                    continue

                # The key has to be already in the database
                k = self.Session.query(A_Key).filter(A_Key.key == key).first()

                # If the value is not yet in the database, create a new value
                v = self.Session.query(A_Value).filter(A_Value.value == unicode(value)).first()
                if v is None:
                    v = A_Value(value=value)
                    v.fk_language = 1

                # Create a new tag with key and value and append it to the tag group
                a_tag = A_Tag()
                db_taggroup.tags.append(a_tag)
                a_tag.key = k
                a_tag.value = v

                # Check if the current tag is the main tag of this tag group. If
                # yes, set the main_tag attribute to this tag
                if a_tag.key.key == main_tag_key and a_tag.value.value == main_tag_value:
                    db_taggroup.main_tag = a_tag

        self._add_changeset(request, new_activity, None)

    def _add_changeset(self, request, activity, old_version):
        """
        Log the activity
        """
        # Create a new changeset
        changeset = A_Changeset(source='[%s] %s' % (activity.status.name, activity), previous_version=old_version)
        # Get the user from the request
        changeset.user = self.Session.query(User).filter(User.username == request.user.username).first()
        changeset.activity = activity
        self.Session.add(changeset)

    def _query(self, request, limit=None, offset=None, filter=None, uid=None):
        """
        Do the query. Returns
        - a list of (filtered) Activities
        - an Integer with the count of Activities
        """
        
        # If no custom filter was provided, get filters from request
        if filter is None:
            # Get the status status
            status_filter = self.Session.query(Status.id).filter(Status.name == self._get_status(request))
            # Get the attribute filter
            tag_filter, filter_length = self._filter(request, A_Tag, A_Key, A_Value)
        
        # Get the order
        order_query, order_numbers = self._get_order(request, Activity, A_Tag_Group, A_Tag, A_Key, A_Value)
        
        # Find id's of relevant activities by joining with prepared filters.
        # If result is ordered, do an Outer Join to attach ordered attributes.
        # 'order_value' contains the values to order by.
        if order_query is not None:
            relevant_activities = self.Session.query(
                                                     Activity.id.label('order_id'),
                                                     order_query.c.value.label('order_value')
                                                     ).\
            join(A_Tag_Group).\
            join(tag_filter, tag_filter.c.filter_tag_id == A_Tag_Group.id).\
            outerjoin(order_query).\
            group_by(Activity.id, order_query.c.value)
            # order the list (needed to correctly apply limit and offset below)
            if self._get_order_direction(request) == 'DESC':
                if order_numbers:
                    relevant_activities = relevant_activities.order_by(desc(cast(order_query.c.value, Float)))
                else:
                    relevant_activities = relevant_activities.order_by(desc(order_query.c.value))
            else:
                if order_numbers:
                    relevant_activities = relevant_activities.order_by(asc(cast(order_query.c.value, Float)))
                else:
                    relevant_activities = relevant_activities.order_by(asc(order_query.c.value))
        # If result is not ordered, only join with prepared filters is necessary.
        else:
            relevant_activities = self.Session.query(
                                                     Activity.id.label('order_id'),
                                                     func.char_length('').label('order_value') # dummy value
                                                     ).\
            join(A_Tag_Group).\
            join(tag_filter, tag_filter.c.filter_tag_id == A_Tag_Group.id).\
            group_by(Activity.id)

        # Apply status filter
        if status_filter:
            relevant_activities = relevant_activities.filter(Activity.fk_status == status_filter)
        
        # Apply custom filter if one was provided
        if filter:
            relevant_activities = relevant_activities.filter(filter)

        # Apply the geographical bounding box filter
        if self._create_geom_filter(request) is not None:
            relevant_activities = relevant_activities.filter(self._create_geom_filter(request))
        
        # Apply logical operator
        if self._get_logical_operator(request) == 'or' or filter_length == 0:
            pass
        else:
            # 'AND': all filtered values must be available
            relevant_activities = relevant_activities.having(func.count() >= filter_length)

        # Special case: UID was provided, create new 'relevant_activities'
        if uid is not None:
            relevant_activities = self.Session.query(Activity.id.label('order_id'),
                                                     func.char_length('').label('order_value')).\
                filter(Activity.activity_identifier == uid)

        # Count relevant activities (before applying limit and offset)
        count = relevant_activities.count()
        
        # Apply limit and offset
        relevant_activities = relevant_activities.limit(limit).offset(offset)

        # Prepare query to translate keys and values
        localizer = get_localizer(request)
        lang = None if localizer.locale_name == 'en' \
            else self.Session.query(Language).filter(Language.locale == localizer.locale_name).first()
        key_translation, value_translation = self._get_translatedKV(lang, A_Key, A_Value)

        # Collect all attributes (TagGroups) of relevant activities
        relevant_activities = relevant_activities.subquery()
        query = self.Session.query(Activity.id.label("id"),
                                   Activity.activity_identifier.label("activity_identifier"),
                                   Activity.point.label("geometry"),
                                   Activity.timestamp.label("timestamp"),
                                   Activity.version.label("version"),
                                   A_Tag_Group.id.label("taggroup"),
                                   A_Tag_Group.fk_a_tag.label("main_tag"),
                                   A_Tag.id.label("tag"),
                                   A_Key.key.label("key"),
                                   A_Value.value.label("value"), \
                                   relevant_activities.c.order_value.label("order_value"),
                                   key_translation.c.key_translated.label("key_translated"),
                                   value_translation.c.value_translated.label("value_translated")).\
            join(relevant_activities, relevant_activities.c.order_id == Activity.id).\
            join(A_Tag_Group).\
            join(A_Tag, A_Tag_Group.id == A_Tag.fk_a_tag_group).\
            join(A_Key).\
            join(A_Value).\
            outerjoin(key_translation, key_translation.c.key_original_id == A_Key.id).\
            outerjoin(value_translation, value_translation.c.value_original_id == A_Value.id)
        
        
        # Do the ordering again
        if order_query is not None:
            if self._get_order_direction(request) == 'DESC':
                query = query.order_by(desc(relevant_activities.c.order_value))
            else:
                query = query.order_by(asc(relevant_activities.c.order_value))

        # Put the activities together
        activities = []
        for i in query.all():

            # The activity identifier
            uid = str(i[1])

            # The geometry
            g = i[2]

            # The version
            version = i[4]

            # The current tag group id (not global unique)
            taggroup_id = int(i[5])

            key = i[11] if i[11] is not None else i[8]
            value = i[12] if i[12] is not None else i[9]

            order_value = i[10]
            
            activity = None
            for a in activities:
                # Use UID to find existing ActivityFeature or create new one
                if a.get_guid() == uid:
                    # If list is ordered (order_value != int), use order_value as well
                    # to find existing ActivityFeature or create new one
                    if not isinstance(order_value, int):
                        if a.get_order_value() == order_value:
                            activity = a
                    else:
                        activity = a

            # If no existing ActivityFeature found, create new one
            if activity == None:
                activity = ActivityFeature2(uid, order_value, geometry=g, version=version)
                activities.append(activity)

            # Check if there is already this tag group present in the current
            # activity
            taggroup = None
            if activity.find_taggroup_by_id(taggroup_id) is not None:
                taggroup = activity.find_taggroup_by_id(taggroup_id)
            else:
                taggroup = TagGroup(taggroup_id, i[6])
                activity.add_taggroup(taggroup)

            taggroup.add_tag(Tag(i[7], key, value))

        return activities, count

    def _history(self, request, uid, status_list=None):
        
        if status_list is None:
            status_list = ['active', 'overwritten', 'deleted']
        
        status_filter = self.Session.query(Status).\
            filter(Status.name.in_(status_list)).\
            subquery()

        query = self.Session.query(Activity.id.label("id"),
                                   Activity.activity_identifier.label("activity_identifier"),
                                   Activity.point.label("geometry"),
                                   Activity.timestamp.label("timestamp"),
                                   Activity.version.label("version"),
                                   A_Tag_Group.id.label("taggroup"),
                                   A_Tag_Group.fk_a_tag.label("main_tag"),
                                   A_Tag.id.label("tag"),
                                   A_Key.key.label("key"),
                                   A_Value.value.label("value"),
                                   A_Changeset.previous_version.label("previous_version"),
                                   A_Changeset.source.label("source"),
                                   User.id.label("userid"),
                                   User.username.label("username"),
                                   status_filter.c.name.label("status")).\
            join(status_filter).\
            join(A_Changeset).\
            join(User).\
            join(A_Tag_Group).\
            join(A_Tag, A_Tag_Group.id == A_Tag.fk_a_tag_group).\
            join(A_Key).\
            join(A_Value).\
            filter(Activity.activity_identifier == uid).\
            order_by(Activity.version)
        
        # Collect the data from query
        data = []
        for i in query.all():
            
            # The activity identifier
            uid = str(i.activity_identifier)

            # The geometry
            g = i.geometry

            # The current tag group id (not global unique)
            taggroup_id = int(i.taggroup)

            key = i.key
            value = i.value

            # use version as order value
            order_value = i.version
            
            diff_info = {
                'status': i.status,
                'previous_version': i.previous_version,
                'userid': i.userid,
                'username': i.username,
                'source': i.source
            }
            
            activity = None
            for a in data:
                # Use order_value (version) to find existing ActivityFeature or create new one
                if a.get_order_value() == order_value:
                    activity = a
            
            # If no existing ActivityFeature found, create new one
            if activity == None:
                activity = ActivityFeature2(uid, order_value, geometry=g, diff_info=diff_info)
                data.append(activity)
            
            # Check if there is already this tag group present in the current
            # activity
            taggroup = None
            if activity.find_taggroup_by_id(taggroup_id) is not None:
                taggroup = activity.find_taggroup_by_id(taggroup_id)
            else:
                taggroup = TagGroup(taggroup_id, i[6])
                activity.add_taggroup(taggroup)

            taggroup.add_tag(Tag(i[7], key, value))
        
        # Loop again through all versions to create diff
        for a in data:
            # If version has no previous version, create empty diff
            if a.get_previous_version() is None:
                a.create_diff()
            # Else look for previous version
            else:
                for ov in data:
                    if ov.get_order_value() == a.get_previous_version():
                        a.create_diff(ov)
                        break
        
        return data, len(data)

    def _create_geom_filter(self, request):
        """
        Create a geometry filter and return the subquery
        """

        # Get the EPSG code from the input geometry
        epsg = functions.srid(Activity.point)
        try:
            epsg = int(request.params.get('epsg', 4326))
        except ValueError:
            pass

        # Get the bbox parameter, this is currently the only supported geometry
        # input
        bbox = request.params.get('bbox', None)
        if bbox is not None:
            box = map(float, bbox.split(','))
            geometry = Polygon((
                               (box[0], box[1]),
                               (box[0], box[3]),
                               (box[2], box[3]),
                               (box[2], box[1]),
                               (box[0], box[1]))
                               )

            # Create the intersection geometry
            wkb_geometry = WKBSpatialElement(buffer(geometry.wkb), epsg)

            # Get the SRID used in the Activity class
            activity_srid = functions.srid(Activity.point)

            # Return a subquery
            return functions.intersects(Activity.point, functions.transform(wkb_geometry, activity_srid))

        return None


    def _key_value_is_valid(self, request, key, value):
        # Read the global configuration file
        global_stream = open(config_file_path(request), 'r')
        global_config = yaml.load(global_stream)

        log.debug(global_config)

        return True