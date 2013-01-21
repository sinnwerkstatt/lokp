from geoalchemy import functions
from lmkp.models.database_objects import Activity
from lmkp.models.database_objects import Changeset
from lmkp.models.database_objects import Involvement
from lmkp.models.database_objects import Profile
from lmkp.models.database_objects import Stakeholder
from lmkp.models.database_objects import Status
from lmkp.models.database_objects import User
from lmkp.models.meta import DBSession as Session
from lmkp.views.config import get_mandatory_keys
from lmkp.views.translation import statusMap
from lmkp.views.views import BaseView
import logging
from pyramid.httpexceptions import HTTPForbidden
from pyramid.httpexceptions import HTTPBadRequest
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm.exc import MultipleResultsFound
from sqlalchemy.sql.expression import and_
from sqlalchemy.sql.expression import not_
from sqlalchemy.sql.expression import or_
from sqlalchemy.sql.functions import min
import string
import json

log = logging.getLogger(__name__)

class BaseReview(BaseView):

    def __init__(self, request):
        super(BaseReview, self).__init__(request)
        self._handle_parameters()

    def _compare_taggroups(self, old, new):

        table = []

        if old is None and new is not None:
            return self._write_new_taggroups(new)

        if old is not None and new is None:
            return self._write_old_taggroups(old)

        # TODO: Compare also the geometry!!

        # Loop the old and check for the same taggroup in the new one
        for old_taggroup in old.get_taggroups():
            new_taggroup = new.find_taggroup_by_tg_id(old_taggroup.get_tg_id())

            # The taggroup does not exist anymore:
            if new_taggroup is None:
                current_row = {}
                old_tags = []
                for t in old_taggroup.get_tags():
                    old_tags.append({'key': t.get_key(),
                                    'value': t.get_value()})
                    current_row['ref'] = {'class': 'remove', 'tags': old_tags}
                    current_row['new'] = {'class': '', 'tags': []}
                table.append(current_row)

            # The taggroup does still exist:
            elif new_taggroup is not None:
                # Compare the old taggroup with the new one
                taggroup_has_changed = False

                if new_taggroup is None:
                    taggroup_has_changed = True

                old_tags = []
                for t in old_taggroup.get_tags():

                    if new_taggroup.get_tag_by_key(t.get_key()) is None:
                        taggroup_has_changed = True
                    elif new_taggroup.get_tag_by_key(t.get_key()).get_value() != t.get_value():
                        taggroup_has_changed = True

                # Test also the other way round
                for t in new_taggroup.get_tags():
                    if old_taggroup.get_tag_by_key(t.get_key()) is None:
                        taggroup_has_changed = True

                current_row = {}
                old_tags_class = new_tags_class = ''
                if taggroup_has_changed:
                    old_tags_class = 'remove'
                    new_tags_class = 'add'

                # Write the old one
                old_tags = []
                for t in old_taggroup.get_tags():
                    old_tags.append({'key': t.get_key(),
                                    'value': t.get_value()})
                current_row['ref'] = {'class': old_tags_class, 'tags': old_tags}
                # Write the new one
                new_tags = []
                for t in new_taggroup.get_tags():
                    new_tags.append({'key': t.get_key(),
                                    'value': t.get_value()})
                current_row['new'] = {'class': new_tags_class, 'tags': new_tags}

                table.append(current_row)

        # Search for new taggroups
        for new_taggroup in new.get_taggroups():

            if old.find_taggroup_by_tg_id(new_taggroup.get_tg_id()) is None:
                current_row = {}
                current_row['ref'] = {'class': '', 'tags': []}
                # Write the new one
                new_tags = []
                for t in new_taggroup.get_tags():
                    new_tags.append({'key': t.get_key(),
                                    'value': t.get_value()})
                current_row['new'] = {'class': 'add', 'tags': new_tags}

                table.append(current_row)

        # TODO Compare the involvements properly

        involvements_table = []

        # Finally compare also the involvments but NOT the tags of the involved stakeholders
        for inv in old.get_involvements():

            new_inv = new.find_involvement_by_guid(inv.get_guid())

            # Involvement has been deleted
            if new_inv == None:
                current_row = {}

                # Write the old one
                old_tags = []
                for t in inv._feature.to_tags():
                    old_tags.append(t)
                current_row['ref'] = {'class': 'remove involvement', 'tags': old_tags}
                # Write the new one
                current_row['new'] = {'class': 'involvement', 'tags': []}

                involvements_table.append(current_row)

            # Role has changed
            elif inv.get_role_id() != new_inv.get_role_id():
                current_row = {}

                # Write the old one
                old_tags = []
                for t in inv._feature.to_tags():
                    old_tags.append(t)
                current_row['ref'] = {'class': 'remove involvement', 'tags': old_tags}
                # Write the new one
                new_tags = []
                new_tags = []
                for t in new_inv._feature.to_tags():
                    new_tags.append(t)
                current_row['new'] = {'class': 'add involvement', 'tags': new_tags}

                involvements_table.append(current_row)

            else:
                current_row = {}
                # Write the old one
                old_tags = []
                for t in inv._feature.to_tags():
                    old_tags.append(t)
                current_row['ref'] = {'class': 'involvement', 'tags': old_tags}
                # Write the new one
                new_tags = []
                for t in new_inv._feature.to_tags():
                    new_tags.append(t)
                current_row['new'] = {'class': 'involvement', 'tags': new_tags}

                involvements_table.append(current_row)


        # Find new involvements:
        for inv in new.get_involvements():

            old_inv = old.find_involvement_by_guid(inv.get_guid())

            if old_inv is None:

                current_row = {}

                # Write the old one
                current_row['ref'] = {'class': '', 'tags': []}
                # Write the new one
                new_tags = []

                for t in inv._feature.to_tags():
                    new_tags.append(t)

                reviewable = 0
                reviewable = self._review_check_involvement(new, inv._feature)

                current_row['new'] = {
                    'class': 'add involvement',
                    'tags': new_tags,
                    'reviewable': reviewable
                }

                involvements_table.append(current_row)


        return {'taggroups': table, 'involvements': involvements_table}

    def _review_check_involvement(self, this_feature, other_feature):
        """
        Function to check if an involvement (other feature) can be reviewed or not. It can be
        reviewed if
        [1]: it is brand new
        [2]: it is based on an active version (set to active)
        [3]: it is based on a version which is not active (recalculate new)
        It can NOT be reviewed if
        [-1]: there are multiple involvements to pending versions on the other
             side (the feature ID has multiple pending versions which have involvements)
        [0]: any other reasons
        """

        # Case 1: Feature is brand new
        if other_feature.get_version() == 1:
            return 1

        thisMappedClass = this_feature.getMappedClass()
        otherMappedClass = other_feature.getMappedClass()

        # Case 2: There are multiple versions of the same feature pending with
        # involvements to this feature.
        # For example, there are multiple Activity versions pending (same GUID
        # and status 'pending') linked through involvements to the same
        # Stakeholder version (identified by GUID and version)
        multiple_pending_query = Session.query(
                otherMappedClass.id
            ).\
            join(Involvement).\
            join(thisMappedClass).\
            filter(thisMappedClass.identifier == this_feature.get_guid()).\
            filter(thisMappedClass.version == this_feature.get_version()).\
            filter(otherMappedClass.fk_status == 1).\
            filter(otherMappedClass.identifier == other_feature.get_guid())
        if multiple_pending_query.count() > 1:
            return -1

        previous_version_query = Session.query(
                otherMappedClass.previous_version
            ).\
            filter(otherMappedClass.identifier == other_feature.get_guid()).\
            filter(otherMappedClass.version == other_feature.get_version()).\
            subquery()
        
        previous_version_status = Session.query(
                otherMappedClass.fk_status
            ).\
            join(previous_version_query,
                previous_version_query.c.previous_version
                == otherMappedClass.version).\
            filter(otherMappedClass.identifier == other_feature.get_guid())

        try:
            status = previous_version_status.one()
        except NoResultFound:
            return 0
        except MultipleResultsFound:
            # This should never happen
            return 0

        if status.fk_status == 2:
            # Case 2: Feature is based on an active version
            return 2
        else:
            # Case 3: Feature is not based on an active version
            return 3

    def _review_one_version(self, obj, uid, version):

        table = []

        # First write the headers
        header_row = []
        header_row.append({'class': 'title', 'tags': [
                          {'key': 'version', 'value': obj.get_version()},
                          {'key': 'status', 'value': obj.get_status()}
                          ]})

        table.append(header_row)

        for taggroup in obj.get_taggroups():

            tags = []
            
            for t in taggroup.get_tags():
                tags.append({'key': t.get_key(), 'value': t.get_value()})
            table.append([{'class': '', 'tags': tags}])

        return {'taggroups': table}

    def _write_old_taggroups(self, old):

        table = []

        # Search for new taggroups
        for old_taggroup in old.get_taggroups():

            current_row = {}
            old_tags = []
            for t in old_taggroup.get_tags():
                old_tags.append({'key': t.get_key(),
                                'value': t.get_value()})
            current_row['ref'] = {'class': '', 'tags': old_tags}

            current_row['new'] = {'class': '', 'tags': []}

            table.append(current_row)

        involvements_table = []

        # Find new involvements:
        for inv in old.get_involvements():

            current_row = {}

            old_inv_tags = []
            for t in inv._feature.to_tags():
                old_inv_tags.append(t)

            # Write the old one
            current_row['ref'] = {'class': '', 'tags': old_inv_tags}
            # Write the new one

            current_row['new'] = {'class': '', 'tags': []}

            involvements_table.append(current_row)

        return {'taggroups': table, 'involvements': involvements_table}

    def _write_new_taggroups(self, new):

        table = []

        # Search for new taggroups
        for new_taggroup in new.get_taggroups():

            current_row = {}
            current_row['ref'] = {'class': '', 'tags': []}
            # Write the new one
            new_tags = []
            for t in new_taggroup.get_tags():
                new_tags.append({'key': t.get_key(),
                                'value': t.get_value()})
            current_row['new'] = {'class': 'add', 'tags': new_tags}

            table.append(current_row)

        # Write involvements:
        involvements_table = []
        for inv in new.get_involvements():

            current_row = {}

            current_row['ref'] = {'class': '', 'tags': []}

            new_inv_tags = []
            for t in inv._feature.to_tags():
                new_inv_tags.append(t)

            reviewable = 0
            reviewable = self._review_check_involvement(new, inv._feature)

            current_row['new'] = {
                'class': 'add involvement',
                'tags': new_inv_tags,
                'reviewable': reviewable
            }
            involvements_table.append(current_row)

        return {'taggroups': table, 'involvements': involvements_table}

    def _get_active_pending_versions(self, mappedClass, uid):
        """
        Returns the current active version and the pending version to review
        """

        def _check_mandatory_keys():
            mandatory_keys = get_mandatory_keys(self.request, 'a')
            log.debug(mandatory_keys)

        # Get the current active version number
        av = Session.query(mappedClass.version).filter(mappedClass.identifier == uid).filter(mappedClass.fk_status == 2).first()

        try:
            active_version = int(av[0])
        except TypeError:
            return None, 1

        # Get the lowest pending version
        pv = Session.query(min(mappedClass.version)).\
            filter(mappedClass.identifier == uid).\
            filter(mappedClass.fk_status == 1).\
            first()

        try:
            pending_version = int(pv[0])
        except TypeError:
            pending_version = None

        # Some logging
        log.debug("active version: %s" % active_version)
        log.debug("pending version: %s" % pending_version)

        return active_version, pending_version

    def _get_metadata(self, mappedClass, uid, refVersion, newVersion):

        refTimestamp = newTimestamp = None

        refQuery = Session.query(
                Changeset.timestamp
            ).\
            join(mappedClass).\
            filter(mappedClass.identifier == uid).\
            filter(mappedClass.version == refVersion).\
            first()

        if refQuery is not None:
            refTimestamp = refQuery.timestamp

        newQuery = Session.query(
                Changeset.timestamp
            ).\
            join(mappedClass).\
            filter(mappedClass.identifier == uid).\
            filter(mappedClass.version == newVersion).\
            first()

        if newQuery is not None:
            newTimestamp =  newQuery.timestamp

        metadata = {
            'ref_version': refVersion,
            'ref_timestamp': str(refTimestamp),
            'new_version': newVersion,
            'new_timestamp': str(newTimestamp),
            'identifier': uid,
            'type': mappedClass.__table__.name,
        }

        return metadata

    def _get_available_versions(self, mappedClass, uid, review=False):
        """
        Returns an array with all versions that are available to the current
        user. Moderators get all versions for Stakeholders and Activity if later
        lies within the moderator's profile. Editors get all active and inactive
        versions as well as their own edits. Public users only get inactive and
        active versions.
        If 'review' is true, only return the active and any pending versions.
        """

        def _get_query_for_editors():
            """
            Returns a query that selects versions available to editors.
            """
            active_versions = Session.query(
                    mappedClass.version,
                    mappedClass.fk_status
                ).\
                filter(mappedClass.identifier == uid).\
                filter(or_(mappedClass.fk_status == 2, mappedClass.fk_status == 3))

            own_filters = and_(mappedClass.identifier == uid, \
                               not_(mappedClass.fk_status == 2), \
                               not_(mappedClass.fk_status == 3), \
                               User.username == self.request.user.username)
            own_versions = Session.query(
                    mappedClass.version,
                    mappedClass.fk_status
                ).\
                join(Changeset).\
                join(User).\
                filter(*own_filters)
            return active_versions.union(own_versions)


        # Query that selects available versions
        versions_query = None

        log.debug("effective principals: %s" % self.request.effective_principals)

        # An administrator sees in any cases all versions
        if self.request.effective_principals is not None and 'group:administrators' in self.request.effective_principals:
            versions_query = Session.query(
                    mappedClass.version,
                    mappedClass.fk_status
                ).filter(mappedClass.identifier == uid)

        # An user with moderator privileges can see all versions within his profile
        elif self.request.effective_principals is not None and 'group:moderators' in self.request.effective_principals:

            # Try if mappedClass is an Activity and lies within the moderator's profile
            try:
                profile_filters = []
                # Get all profiles for the current moderator
                profiles = Session.query(Profile).filter(Profile.users.any(username=self.request.user.username))
                for p in profiles.all():
                    profile_filters.append(functions.intersects(mappedClass.point, p.geometry))

                # Check if current Activity is within the moderator's profile
                count = Session.query(mappedClass).filter(mappedClass.identifier == uid).filter(or_(*profile_filters)).count()
                # Activity is within the moderator's profile, then show all versions
                if count > 0:
                    versions_query = Session.query(
                            mappedClass.version,
                            mappedClass.fk_status
                        ).filter(mappedClass.identifier == uid)
                # If not the moderator gets normal editor privileges
                else:
                    versions_query = _get_query_for_editors()
            # In case mappedClass is a Stakeholder, show anyway all versions
            except AttributeError:
                versions_query = Session.query(
                        mappedClass.version,
                        mappedClass.fk_status
                    ).filter(mappedClass.identifier == uid)

        # An user with at least editor privileges can see all public versions_query
        # and his own edits
        elif self.request.effective_principals is not None and 'group:editors' in self.request.effective_principals:
            versions_query = _get_query_for_editors()

        # Public users i.e. not logged in users see only active and inactive versions
        else:
            versions_query = Session.query(
                    mappedClass.version,
                    mappedClass.fk_status
                ).\
                filter(mappedClass.identifier == uid).\
                filter(or_(mappedClass.fk_status == 2, mappedClass.fk_status == 3))

        # Create a list of available versions
        available_versions = []
        for i in versions_query.order_by(mappedClass.version).all():
            if review is False or i[1] == 1 or i[1] == 2:
                available_versions.append({
                    'version': i[0],
                    'status': i[1]
                })

        log.debug("Available Versions for object %s:\n%s" % (uid, available_versions))

        return available_versions

    def _get_valid_versions(self, mappedClass, uid, review=False):
        """
        Returns two version numbers:
        - the base version number: if not indicated explicitely, the active
          version is returned if available, else version 1
        - the version number to compare with: if not indicated explicitely, the
          first pending version is returned else version 1
        """

        # Check permissions
        available_versions = self._get_available_versions(
            mappedClass, uid, review=review
        )

        # Find out available versions and if possible active and first pending
        # version
        v = []
        active_version = pending_version = None
        for av in available_versions:
            v.append(av.get('version'))
            if av.get('status') == 2:
                active_version = av.get('version')
            if av.get('status') == 1:
                if pending_version is None or pending_version > av.get('version'):
                    pending_version = av.get('version')

        # Try to get the versions or set reference and new version
        versions = self.request.matchdict.get('versions')
        try:
            ref_version = int(versions[0])
        except IndexError:
            #
            ref_version = active_version if active_version is not None else 1
        except ValueError as e:
            raise HTTPBadRequest("ValueError: %s" % e)

        try:
            new_version = int(versions[1])
        except IndexError:
            if pending_version is not None:
                new_version = pending_version
            elif active_version is not None:
                new_version = active_version
            else:
                new_version = 1
        except ValueError as e:
            raise HTTPBadRequest("ValueError: %s" % e)

        if ((ref_version == 0 and new_version not in v)
            or (ref_version != 0 and ref_version not in v or new_version not in v)):
            raise HTTPForbidden()

        return ref_version, new_version

    def _apply_diff(self, item, diff):
        from lmkp.views.protocol import Tag

        if 'taggroups' in diff:
            for tg in diff['taggroups']:
                tg_id = tg['tg_id'] if 'tg_id' in tg else None
                add_tags = []
                delete_tags = []

                for t in tg['tags']:
                    if t['op'] == 'add':
                        add_tags.append(
                            {'key': t['key'], 'value': t['value']}
                        )
                    if t['op'] == 'delete':
                        delete_tags.append(
                            {'key': t['key'], 'value': t['value'], 'id': t['id']}
                        )

                #TODO: clean up ...
                print "*** add"
                print len(add_tags)
                print add_tags
                print "*** delete"
                print len(delete_tags)
                print delete_tags
                print "*** tg_id: %s" % tg_id

                new_tg = item.find_taggroup_by_tg_id(tg_id)
                print "*** new_tg: %s" % new_tg
                if new_tg is not None:
                    # Delete tags
                    for dt in delete_tags:
                        # Try to find the tag by its key. If found, remove it
                        deleted_tag = new_tg.get_tag_by_key(dt['key'])
                        if deleted_tag:
                            print "*** removed tag with key: %s and value: %s" % (dt['key'], dt['value'])
                            new_tg.remove_tag(deleted_tag)
                    # Add tags
                    for at in add_tags:
                        if new_tg.get_tag_by_key(at['key']) is None:
                            print "*** added tag with key: %s and value: %s" % (at['key'], str(at['value']))
                            new_tg.add_tag(Tag(None, at['key'], str(at['value'])))

        return item

    def _recalculate_version(self, mappedClass, ref, new):

        #TODO
        asdf

        ref_version = ref.get_version()
        new_previousversion = new.get_previous_version()

        if (new_previousversion is not None
            and new_previousversion != ref_version):
            # The new_version is not based on the ref_version, it is therefore
            # necessary to get the changes made to ref_version and calculate
            # them into new_version

            diff_query = Session.query(Changeset.diff).\
                join(mappedClass).\
                filter(mappedClass.identifier == ref.get_guid()).\
                filter(mappedClass.version == ref.get_version())

            diff = diff_query.first()

            diff_json = json.loads(diff.diff.replace('\'', '"'))

            # TODO: compare also involvements

            if mappedClass == Activity:
                diff_keyword = 'activities'
            elif mappedClass == Stakeholder:
                diff_keyword = 'stakeholders'
            else:
                diff_keyword = None
            
            d = None
            if (diff_keyword is not None and diff_keyword in diff_json
                and diff_json[diff_keyword] is not None):
                activities = diff_json[diff_keyword]
                for a in activities:
                    if ('id' in a and a['id'] is not None
                        and a['id'] == ref.get_guid()):
                        d = a

            if d is not None:
                new = self._apply_diff(new, d)

        return new

    def recalc(self, mappedClass, item, diff):

        if mappedClass == Activity:
            diff_keyword = 'activities'
        elif mappedClass == Stakeholder:
            diff_keyword = 'stakeholders'
        else:
            diff_keyword = None

        if (diff_keyword is not None and diff_keyword in diff
            and diff[diff_keyword] is not None):
            for x in diff[diff_keyword]:
                if ('id' in x and x['id'] is not None
                    and x['id'] == item.get_guid()):
                    item = self._apply_diff(item, x)

        return item

    def get_comparison(self, mappedClass, uid, ref_version_number,
        new_version_number, review=False):
        """
        Function to do the actual comparison and return a json
        """

        if (ref_version_number == 0
            or (new_version_number == 1 and ref_version_number == 1)):
            ref_object = None
            ref_version_number = None
        else:
            # Get the reference object
            ref_object = self.protocol.read_one_by_version(
                self.request, uid, ref_version_number
            )

        # Check if a diff is needed to recalculate the new object
        ref_diff, base_version_number = self.get_diff(
            mappedClass, uid, new_version_number, ref_version_number
        )

        print "****"
        print ref_diff
#        asdf

        if ref_diff is None:
            # The easy case: the new object can be shown as it is in the
            # database.
            if new_version_number is not None:
                new_object = self.protocol.read_one_by_version(
                    self.request, uid, new_version_number
                )
            else:
                new_object = None

        else:
            # The hard case: It is necessary to recalculate the new object so
            # that it includes the same changes made to the reference object. To
            # do this, the diff of the ref object and of the new object need to
            # be merged.

            # TODO: Check if this needs to be recursive ...

            # Query the base object
            print "-- ref_diff"
            print ref_diff
            ref_object_query = self.protocol.read_one_by_version(
                self.request, uid, base_version_number
            )
            ref_object = self.recalc(mappedClass, ref_object_query, ref_diff)

            asdf

            # Find the diff
            new_diff_query = Session.query(
                    Changeset.diff).\
                join(mappedClass).\
                filter(mappedClass.identifier == uid).\
                filter(mappedClass.version == new_version_number).\
                first()
            new_diff = json.loads(new_diff_query.diff.replace('\'', '"'))
            print "-- new_diff"
            print new_diff
            calculated_diff = self.recalculate_diffs(
                mappedClass, uid, new_diff, ref_diff
            )
            print "-- calculated_diff"
            print calculated_diff

            asdf

            # Apply the diff to the base_object
            new_object_query = self.protocol.read_one_by_version(
                self.request, uid, base_version_number
            )
            new_object = self.recalc(mappedClass, new_object_query, calculated_diff)


            # Recalculate a new diff based on the new_diff and the ref_diff

        # Request also the metadata
        metadata = self._get_metadata(
            mappedClass, uid, ref_version_number, new_version_number
        )

        # Add flag of recalculation to metadata
        recalculated = False
        if ref_diff is not None and ref_version_number != new_version_number:
            recalculated = True

        metadata['recalculated'] = recalculated

        result = dict(
            self._compare_taggroups(ref_object, new_object).items() +
            {'metadata': metadata}.items() +
            {'versions': self._get_available_versions(
                mappedClass, uid, review=review)
            }.items()
        )

        return result

    def get_diff(self, mappedClass, uid, new_version_number,
        ref_version_number=None):
        """
        Returns the diff between the reference version item and its previous 
        version. This diff can then be used to recalculate the new version item 
        to include the changes made to the reference version item.

        - If no ref_version_number was specified or no reference version item
          was found, return None.
        - If the new version item is based directly on the reference version
          item, return None.
        """

        def _query_previous_version(mappedClass, uid, version):
            q = Session.query(mappedClass.previous_version).\
                filter(mappedClass.identifier == uid).\
                filter(mappedClass.version == version)
            return q.first()

        def _query_diff(mappedClass, uid, version):
            q = Session.query(Changeset.diff).\
                join(mappedClass).\
                filter(mappedClass.identifier == uid).\
                filter(mappedClass.version == version)
            return q.first()

        # If no old version was provided, return empty
        if ref_version_number is None:
            return None, None

        # Query the previous version of the new version item
        new_previous_version_number = _query_previous_version(
            mappedClass, uid, new_version_number
        )
        # Query the previous version of the ref version item
        ref_previous_version_number = _query_previous_version(
            mappedClass, uid, ref_version_number
        )
        if ref_previous_version_number.previous_version is None:
            # If the ref version is not based on a previous_version (brandnew),
            # use the version itself
            ref_previous_version_number.previous_version = ref_version_number

        # If no previous version was found, return empty
        if (new_previous_version_number is None
            or new_previous_version_number.previous_version is None):
            return None, None

        # If the new version item is based directly on the reference version
        # item, return empty
        if new_previous_version_number.previous_version == ref_version_number:
            return None, None


        temp_new_version = new_version_number
        new_version_list = [temp_new_version]
        while (temp_new_version is not None):
            temp_new_query = _query_previous_version(mappedClass, uid, temp_new_version)
            temp_new_version = temp_new_query.previous_version
            if temp_new_version is not None:
                new_version_list.append(temp_new_version)

        temp_ref_version = ref_version_number
        ref_version_list = [temp_ref_version]
        while (temp_ref_version is not None):
            temp_ref_query = _query_previous_version(mappedClass, uid, temp_ref_version)
            temp_ref_version = temp_ref_query.previous_version
            if temp_ref_version is not None:
                ref_version_list.append(temp_ref_version)

        common_version = 0
        for i in new_version_list:
            if i in ref_version_list and common_version < i:
                common_version = i
        print "*** common_version ***: %s" % common_version

        if common_version == 0:
            # Could / should this ever happen? What to do if it does happen?
            asdf
        else:

            print "--- starting to merge all diffs between ref version and common version"

            """
            Merge all diffs between the ref version item and the common version
            """
            temp_ref_version_number = ref_version_number
            temp_ref_previous_version = _query_previous_version(mappedClass, uid, ref_version_number)

            diff = None
            if temp_ref_previous_version is not None and temp_ref_previous_version.previous_version is not None:
                # Only take a diff if it has a previous_version
                temp_diff = _query_diff(mappedClass, uid, temp_ref_version_number)
                diff = json.loads(temp_diff.diff.replace('\'', '"'))
                print "*** first diff:"
                print diff
                while temp_ref_previous_version.previous_version != common_version:
                    temp_ref_version_number = temp_ref_previous_version.previous_version
                    temp_ref_previous_version = _query_previous_version(mappedClass, uid, temp_ref_previous_version.previous_version)

                    if temp_ref_previous_version is not None and temp_ref_previous_version.previous_version is not None:
                        # Only take a diff if it has a previous_version
                        print "*** added diff for version: %s" % temp_ref_version_number
                        temp_diff = _query_diff(mappedClass, uid, temp_ref_version_number)
                        temp_diff_json = json.loads(temp_diff.diff.replace('\'', '"'))
                        diff = self.recalculate_diffs(mappedClass, uid, temp_diff_json, diff)





            print "*** diff after mergin all diffs between ref version and common version:"
            print diff

            """
            Merge all diffs between the previous_version of the new version item and the common version
            """

            print "--- starting to merge all diffs between the new version and common version"

            temp_new_previous_version = _query_previous_version(mappedClass, uid, new_version_number)
#            temp_new_previous_version = _query_previous_version(mappedClass, uid, temp_new_previous_version.previous_version)

            while temp_new_previous_version.previous_version != common_version:



                temp_diff = _query_diff(mappedClass, uid, temp_new_previous_version.previous_version)
                temp_diff_json = json.loads(temp_diff.diff.replace('\'', '"'))
                print "*** added diff for version: %s" % temp_new_previous_version.previous_version
                print temp_diff_json
                print "***"

                diff = self.recalculate_diffs(mappedClass, uid, temp_diff_json, diff)

                temp_new_previous_version = _query_previous_version(mappedClass, uid, temp_new_previous_version.previous_version)

#                empty_diff = False

            print "*** diff after mergin all diffs between new version and common version:"
            print diff

        asdf

        if empty_diff is True:
            return None, None

        return diff, common_version

        """
#        else:
        if (1 == 1):
            If the new_version is based on the

            # get_diff() returns the changes made to the ref version item

            It returns the difference between the ref version item and the previous_version of the new version item.



            # Approach: Add and merge all diffs from the previous_version of the
            # new version item until the one that is based on the
            # ref_version_number





            # Starter: The previous_version of the new_version (do not merge this if it is the same the ref_version is based upon)




            # Stopper: the previous_version of the ref version item (or the ref_version_numer if it is brand new and has no previous_version)

            print "--- new_previous_version_number: %s" % new_previous_version_number.previous_version
            # 1 | 2
            print "--- ref_previous_version_number: %s" % ref_previous_version_number.previous_version
            # 1 | 1 (None)

            # Initial diff: the diff of the previous_version of the new version
            # item.
            ref_diff = _query_diff(mappedClass, uid, new_previous_version_number.previous_version)
#            diff = _query_diff(mappedClass, uid, ref_version_number)

            temp_previous_version_q = new_previous_version_number # 1 | 2
            while (temp_previous_version_q.previous_version > ref_previous_version_number.previous_version):

                x = _query_diff(mappedClass, uid, temp_previous_version_q.previous_version)
                x2 = json.loads(x.diff.replace('\'', '"'))

                ref_diff = self.recalculate_diffs(mappedClass, uid, x2, ref_diff)

                print "**********************"
                print "temp_previous_version_q: %s" % temp_previous_version_q
                print ref_diff
#                print x

                temp_previous_version_q = _query_previous_version(mappedClass, uid, temp_previous_version_q.previous_version)
#                x = x_q.previous_version


#            if  == new_previous_version_number.previous_version:
                # Return the diff between the reference version item and its
                # previous version

            print "......................"
            print ref_diff
            print "......................"
            temp_diff = _query_diff(mappedClass, uid, ref_version_number)
            temp_diff2 = json.loads(temp_diff.diff.replace('\'', '"'))
            print "--2--"
#            print temp_diff2
#            temp_diff3 = {'activities': [temp_diff2]}
            print "--3--"
#            print temp_diff3
            diff = self.recalculate_diffs(mappedClass, uid, temp_diff2, None)
            print "-----------"
            print diff

            asdf
            return json.loads(diff.diff.replace('\'', '"'))
#            else:
#                print "******************"
#                asdf
        """

    def recalculate_diffs(self, mappedClass, uid, new_diff, old_diff=None):

        #TODO: clean up ...

#        print "------------------------"
#        print "new_diff: %s" % new_diff
#        print "old_diff: %s" % old_diff

        def _merge_tgs(diff_keyword, uid, old_diff, taggroup):
            """
            Merge / Append a taggroup into a diff
            """

            print "** FUNCTION _merge_tgs"
            print "old_diff: %s" % old_diff
            """
            Approach: Loop through all taggroups in the old_diff and check if it
            needs to be merged. If not found, append it to the diff.
            """
            if diff_keyword in old_diff and old_diff[diff_keyword] is not None:
                for a in old_diff[diff_keyword]:

                    print "----loooppp------"

                    if 'id' in a and a['id'] == str(uid):
                        # It is the correct Activity / Stakeholder, loop through its taggroups
                        tag_found = False
                        for tg in a['taggroups']:
                            print "tg: %s" % tg
                            print "a[taggroups]: %s" % a['taggroups']
                            if 'tg_id' in tg and 'tg_id' in taggroup and tg['tg_id'] == taggroup['tg_id']:
                                # If the same taggroup has changes, the newer is
                                # used and the old is replaced.
                                print "**** REPLACE ****"
                                a['taggroups'].remove(tg)
#                                print a['taggroups']
                                a['taggroups'].append(taggroup)
#                                print a['taggroups']
                                tag_found = True

                        if tag_found is False:
                            # Not found, append
#                            print "**** APPEND ****"
                            a['taggroups'].append(taggroup)
#                            print a['taggroups']

            return old_diff

        if mappedClass == Activity:
            diff_keyword = 'activities'
        elif mappedClass == Stakeholder:
            diff_keyword = 'stakeholders'
        else:
            diff_keyword = None

        ret = {}

        if old_diff is None and diff_keyword is not None:
            # Extract only interesting stuff out of new_diff
            if diff_keyword in new_diff and new_diff[diff_keyword] is not None:
                for a in new_diff[diff_keyword]:
                    if 'id' in a and a['id'] == str(uid):
                        ret = a

        elif old_diff is not None and diff_keyword is not None:
            # Recalculate diff out of old and new diff
            if diff_keyword in new_diff and new_diff[diff_keyword] is not None:
                """
                Approach: Loop through taggroups of new diff and merge them into the old diff
                """
                for a in new_diff[diff_keyword]:
                    if 'id' in a and a['id'] == str(uid):
                        # Merge with existing
#                        print "____M*EERERGE____"
                        if 'taggroups' in a:
                            for tg in a['taggroups']:
                                print "____M*EERERGE____ tg: %s" %tg
                                old_diff = _merge_tgs(diff_keyword, uid, old_diff, tg)
                ret = old_diff

        return ret

