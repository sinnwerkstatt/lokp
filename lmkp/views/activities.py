from lmkp.models.database_objects import *
from lmkp.models.meta import DBSession as Session
from lmkp.views.activity_protocol3 import ActivityProtocol3
from lmkp.views.comments import comments_sitekey
from lmkp.views.config import get_mandatory_keys
from lmkp.config import check_valid_uuid
from lmkp.config import getTemplatePath
import logging
import urllib
from pyramid.httpexceptions import HTTPBadRequest
from pyramid.httpexceptions import HTTPForbidden
from pyramid.httpexceptions import HTTPFound
from pyramid.httpexceptions import HTTPNotFound
from pyramid.httpexceptions import HTTPUnauthorized
from pyramid.httpexceptions import HTTPInternalServerError
from pyramid.i18n import get_localizer
from pyramid.i18n import TranslationStringFactory
from pyramid.renderers import render_to_response
from pyramid.response import Response
from pyramid.security import ACLAllowed
from pyramid.security import authenticated_userid
from pyramid.security import has_permission
from pyramid.view import view_config
import yaml
import json

from lmkp.views.activity_review import ActivityReview
from lmkp.renderers.renderers import translate_key
from lmkp.views.form import renderForm
from lmkp.views.form import renderReadonlyForm
from lmkp.views.form import renderReadonlyCompareForm
from lmkp.views.form import checkValidItemjson
from lmkp.views.form_config import getCategoryList
from lmkp.views.profile import get_current_profile
from lmkp.views.profile import get_current_locale
from lmkp.views.profile import get_spatial_accuracy_map
from lmkp.views.views import BaseView
from lmkp.authentication import checkUserPrivileges
from lmkp.views.translation import get_translated_status
from lmkp.views.translation import get_translated_db_keys

log = logging.getLogger(__name__)

_ = TranslationStringFactory('lmkp')

activity_protocol3 = ActivityProtocol3(Session)

def get_timestamp(request):
    """
    Gets the timestamp from the request url and returns it
    """
    pass

@view_config(route_name='activities_read_many')
def read_many(request):
    """
    Read many, returns also pending Activities by currently logged in user and
    all pending Activities if logged in as moderator.
    Default output format: JSON
    """

    # Handle the parameters (locale, profile)
    bv = BaseView(request)
    bv._handle_parameters()

    try:
        output_format = request.matchdict['output']
    except KeyError:
        output_format = 'json'

    if output_format == 'json':
        activities = activity_protocol3.read_many(request, public=False)
        return render_to_response('json', activities, request)
    elif output_format == 'html':
        """
        Show a HTML representation of the Activities in a grid.
        """

        # Get page parameter from request and make sure it is valid
        page = request.params.get('page', 1)
        try:
            page = int(page)
        except:
            page = 1
        page = max(page, 1) # Page should be >= 1

        # Get pagesize parameter from request and make sure it is valid
        pageSize = request.params.get('pagesize', 10)
        try:
            pageSize = int(pageSize)
        except:
            pageSize = 10
        pageSize = max(pageSize, 1) # Page size should be >= 1
        pageSize = min(pageSize, 50) # Page size should be <= 50

        # Spatial filter
        spatialfilter = _handle_spatial_parameters(request)

        # Query the items with the protocol
        items = activity_protocol3.read_many(request, public=False,
                                    limit=pageSize, offset=pageSize*page-pageSize)

        statusFilter = request.params.get('status', None)
        isLoggedIn, isModerator = checkUserPrivileges(request)

        return render_to_response(getTemplatePath(request, 'activities/grid.mak'), {
                                  'data': items['data'] if 'data' in items else [],
                                  'total': items['total'] if 'total' in items else 0,
                                  'profile': get_current_profile(request),
                                  'locale': get_current_locale(request),
                                  'spatialfilter': spatialfilter,
                                  'invfilter': None,
                                  'statusfilter': statusFilter,
                                  'currentpage': page,
                                  'pagesize': pageSize,
                                  'isModerator': isModerator
                                  }, request)

    elif output_format == 'form':
        # This is used to display a new and empty form for an Activity
        if request.user is None:
            # Make sure the user is logged in
            raise HTTPForbidden()
        newInvolvement = request.params.get('inv', None)
        templateValues = renderForm(request, 'activities', inv=newInvolvement)
        if isinstance(templateValues, Response):
            return templateValues
        templateValues.update({
                              'uid': '-',
                              'version': 0,
                              'profile': get_current_profile(request),
                              'locale': get_current_locale(request)
                              })
        return render_to_response(
                                  getTemplatePath(request, 'activities/form.mak'),
                                  templateValues,
                                  request
                                  )
    elif output_format == 'geojson':
        activities = activity_protocol3.read_many_geojson(request, public=False)
        return render_to_response('json', activities, request)
    else:
        # If the output format was not found, raise 404 error
        raise HTTPNotFound()

@view_config(route_name='activities_public_read_many')
def read_many_public(request):
    """
    Read many, does not return any pending Activities.
    Default output format: JSON
    """

    try:
        output_format = request.matchdict['output']
    except KeyError:
        output_format = 'json'

    if output_format == 'json':
        activities = activity_protocol3.read_many(request, public=True)
        return render_to_response('json', activities, request)
    elif output_format == 'html':
        #@TODO
        return render_to_response('json', {'HTML': 'Coming soon'}, request)
    elif output_format == 'geojson':
        activities = activity_protocol3.read_many_geojson(request, public=True)
        return render_to_response('json', activities, request)
    else:
        # If the output format was not found, raise 404 error
        raise HTTPNotFound()

@view_config(route_name='activities_read_many_pending', permission='moderate')
def read_many_pending(request):
    """
    Read many pending Activities based on the profile attached to the moderator.
    Default output format: JSON
    """

    try:
        output_format = request.matchdict['output']
    except KeyError:
        output_format = 'json'

    if output_format == 'json':
        activities = activity_protocol3.read_many_pending(request)
        return render_to_response('json', activities, request)
    elif output_format == 'html':
        #@TODO
        return render_to_response('json', {'HTML': 'Coming soon'}, request)
    else:
        # If the output format was not found, raise 404 error
        raise HTTPNotFound()

@view_config(route_name='activities_bystakeholders')
def by_stakeholders(request):
    """
    Read many Activities based on a Stakeholder ID. Also return pending
    Activities by currently logged in user and all pending Activities if logged
    in as moderator.
    In contrast to the similar method in views/stakeholders.py, at least one
    uid has to be specified in the matchdict "uids". To query *all* the
    Stakeholders, use route "activities_read_many".
    Default output format: JSON
    """

    try:
        output_format = request.matchdict['output']
    except KeyError:
        output_format = 'json'

    uids = []
    uidsMatchdict = request.matchdict.get('uids', None)
    if uidsMatchdict is not None:
        uids = uidsMatchdict.split(',')

    # Remove any invalid UIDs
    for uid in uids:
        if check_valid_uuid(uid) is not True:
            uids.remove(uid)

    if len(uids) == 0:
        raise HTTPNotFound()

    if output_format == 'json':
        activities = activity_protocol3.read_many_by_stakeholders(request,
                                                                  uids=uids, public=False)
        return render_to_response('json', activities, request)
    elif output_format == 'html':
        """
        Show a HTML representation of the Activities of a Stakeholder in a grid.
        """

        # Get page parameter from request and make sure it is valid
        page = request.params.get('page', 1)
        try:
            page = int(page)
        except:
            page = 1
        page = max(page, 1) # Page should be >= 1

        # Get pagesize parameter from request and make sure it is valid
        pageSize = request.params.get('pagesize', 10)
        try:
            pageSize = int(pageSize)
        except:
            pageSize = 10
        pageSize = max(pageSize, 1) # Page size should be >= 1
        pageSize = min(pageSize, 50) # Page size should be <= 50

        # No spatial filter is used if the activities are filtered by a
        # stakeholder
        spatialfilter = None

        # Query the items with the protocol
        items = activity_protocol3.read_many_by_stakeholders(request, uids=uids,
                                                             public=False, limit=pageSize, offset=pageSize * page-pageSize)

        return render_to_response(getTemplatePath(request, 'activities/grid.mak'), {
                                  'data': items['data'] if 'data' in items else [],
                                  'total': items['total'] if 'total' in items else 0,
                                  'profile': get_current_profile(request),
                                  'locale': get_current_locale(request),
                                  'spatialfilter': spatialfilter,
                                  'invfilter': uids,
                                  'currentpage': page,
                                  'pagesize': pageSize
                                  }, request)
    else:
        # If the output format was not found, raise 404 error
        raise HTTPNotFound()

@view_config(route_name='activities_bystakeholders_public')
def by_stakeholders_public(request):
    """
    Read many Activities based on a Stakeholder ID. Do not return any pending
    versions.
    Default output format: JSON
    """

    try:
        output_format = request.matchdict['output']
    except KeyError:
        output_format = 'json'

    uids = []
    uidsMatchdict = request.matchdict.get('uids', None)
    if uidsMatchdict is not None:
        uids = uidsMatchdict.split(',')

    # Remove any invalid UIDs
    for uid in uids:
        if check_valid_uuid(uid) is not True:
            uids.remove(uid)

    if len(uids) == 0:
        raise HTTPNotFound()

    if output_format == 'json':
        activities = activity_protocol3.read_many_by_stakeholders(request,
                                                                  uids=uids, public=True)
        return render_to_response('json', activities, request)
    elif output_format == 'html':
        #@TODO
        return render_to_response('json', {'HTML': 'Coming soon'}, request)
    else:
        # If the output format was not found, raise 404 error
        raise HTTPNotFound()

@view_config(route_name='activities_read_one')
def read_one(request):
    """
    Read one Activity based on ID and return all versions of this Activity. Also
    return pending versions by currently logged in user and all pending versions
    of this Activity if logged in as moderator.
    Default output format: JSON
    """

    # Handle the parameters (locale, profile)
    bv = BaseView(request)
    bv._handle_parameters()

    try:
        output_format = request.matchdict['output']
    except KeyError:
        output_format = 'json'

    uid = request.matchdict.get('uid', None)
    if check_valid_uuid(uid) is not True:
        raise HTTPNotFound()

    if output_format == 'json':
        activities = activity_protocol3.read_one(request, uid=uid, public=False)
        return render_to_response('json', activities, request)
    elif output_format == 'html':
        # Show the details of an Activity by rendering the form in readonly
        # mode.
        activities = activity_protocol3.read_one(request, uid=uid, public=False,
                                                 translate=False)
        version = request.params.get('v', None)
        if activities and 'data' in activities and len(activities['data']) != 0:
            for a in activities['data']:
                if 'version' in a:
                    if version is None:
                        # If there was no version provided, show the first
                        # version visible to the user
                        version = str(a['version'])
                    if str(a['version']) == version:
                        templateValues = renderReadonlyForm(request, 'activities', a)
                        templateValues['profile'] = get_current_profile(request)
                        templateValues['locale'] = get_current_locale(request)

                        # Append the short uid and the uid to the templates values
                        templateValues['uid'] = uid
                        templateValues['version'] = version
                        templateValues['shortuid'] = uid.split("-")[0]
                        # Append also the site key from the commenting system
                        templateValues['site_key'] = comments_sitekey(request)['site_key']
                        # and the url of the commenting system
                        templateValues['comments_url'] = request.registry.settings['lmkp.comments_url']

                        return render_to_response(
                                                  getTemplatePath(request, 'activities/details.mak'),
                                                  templateValues,
                                                  request
                                                  )
        return HTTPNotFound()
    elif output_format == 'form':
        if request.user is None:
            # Make sure the user is logged in
            raise HTTPForbidden()
        # Query the Activities wih the given identifier
        activities = activity_protocol3.read_one(request, uid=uid, public=False,
                                                 translate=False)
        version = request.params.get('v', None)
        if activities and 'data' in activities and len(activities['data']) != 0:
            for a in activities['data']:
                if 'version' in a:
                    if version is None:
                        # If there was no version provided, show the first
                        # version visible to the user
                        version = str(a['version'])
                    if str(a['version']) == version:
                        templateValues = renderForm(request, 'activities', itemJson=a)
                        if isinstance(templateValues, Response):
                            return templateValues
                        templateValues['profile'] = get_current_profile(request)
                        templateValues['locale'] = get_current_locale(request)
                        templateValues['uid'] = uid
                        templateValues['version'] = version
                        return render_to_response(
                                                  getTemplatePath(request, 'activities/form.mak'),
                                                  templateValues,
                                                  request
                                                  )
        return HTTPNotFound()
    elif output_format in ['review', 'compare']:
        if output_format == 'review':
            # Only moderators can see the review page.
            isLoggedIn, isModerator = checkUserPrivileges(request)
            if isLoggedIn is False or isModerator is False:
                raise HTTPForbidden()
        
        review = ActivityReview(request)
        availableVersions = None
        recalculated = False
        defaultRefVersion, defaultNewVersion = review._get_valid_versions(
                                                                          Activity, uid)
            
        refVersion = request.params.get('ref', None)
        if refVersion is not None:
            try:
                refVersion = int(refVersion)
            except:
                refVersion = None
        if refVersion is None or output_format == 'review':
            # No reference version indicated, use the default one
            # Also use the default one for review because it cannot be changed.
            refVersion = defaultRefVersion
        else:
            availableVersions = review._get_available_versions(Activity, uid, 
                                                               review=output_format == 'review')
            # Check if the indicated reference version is valid
            if refVersion not in [v.get('version') for v in availableVersions]:
                refVersion = defaultRefVersion
        
        newVersion = request.params.get('new', None)
        if newVersion is not None:
            try:
                newVersion = int(newVersion)
            except:
                newVersion = None
        if newVersion is None:
            # No new version indicated, use the default one
            newVersion = defaultNewVersion
        else:
            if availableVersions is None:
                availableVersions = review._get_available_versions(Activity, 
                                                                   uid, review=output_format == 'review')
            # Check if the indicated new version is valid
            if newVersion not in [v.get('version') for v in availableVersions]:
                newVersion = defaultNewVersion
        
        if output_format == 'review':
            # If the Activities are to be reviewed, only the changes which were
            # applied to the newVersion are of interest
            activities, recalculated = review.get_comparison(Activity, uid, 
                                                             refVersion, newVersion)
        else:
            # If the Activities are compared, the versions as they are stored
            # in the database are of interest, without any recalculation
            activities = [
                activity_protocol3.read_one_by_version(request, uid, refVersion,
                                                       geometry='full', translate=False
                                                       ),
                activity_protocol3.read_one_by_version(request, uid, newVersion,
                                                       geometry='full', translate=False
                                                       )
            ]
        templateValues = renderReadonlyCompareForm(request, 'activities', 
                                                   activities[0], activities[1], review=output_format == 'review')
        # Collect metadata for the reference version
        refMetadata = {}
        if activities[0] is not None:
            refMetadata = activities[0].get_metadata(request)
        # Collect metadata and missing keys for the new version
        newMetadata = {}
        missingKeys = []
        reviewable = False
        if activities[1] is not None:
            activities[1].mark_complete(get_mandatory_keys(request, 'a', False))
            missingKeys = activities[1]._missing_keys
            localizer = get_localizer(request)
            if localizer.locale_name != 'en':
                db_lang = Session.query(Language).filter(Language.locale == localizer.locale_name).first()
                missingKeys = get_translated_db_keys(A_Key, missingKeys, db_lang)
                missingKeys = [m[1] for m in missingKeys]
                
            newMetadata = activities[1].get_metadata(request)
            
            reviewable = (len(missingKeys) == 0 and 
                          'reviewableMessage' in templateValues and
                          templateValues['reviewableMessage'] is None)
        
        if output_format == 'review':
            pendingVersions = []
            if availableVersions is None:
                availableVersions = review._get_available_versions(Activity, 
                                                                   uid, review=output_format == 'review')
            for v in sorted(availableVersions, key=lambda v:v.get('version')):
                if v.get('status') == 1:
                    pendingVersions.append(v.get('version'))
            templateValues['pendingVersions'] = pendingVersions
        
        templateValues.update({
                              'identifier': uid,
                              'refVersion': refVersion,
                              'refMetadata': refMetadata,
                              'newVersion': newVersion,
                              'newMetadata': newMetadata,
                              'missingKeys': missingKeys,
                              'reviewable': reviewable,
                              'recalculated': recalculated,
                              'profile': get_current_profile(request),
                              'locale': get_current_locale(request)
                              })
        
        if output_format == 'review':
            return render_to_response(
                                      getTemplatePath(request, 'activities/review.mak'),
                                      templateValues,
                                      request
                                      )
        else:
            return render_to_response(
                                      getTemplatePath(request, 'activities/compare.mak'),
                                      templateValues,
                                      request
                                      )
    elif output_format == 'geojson':
        # A version is required
        version = request.params.get('v', None)
        if version is None:
            raise HTTPBadRequest('You must specify a version as parameter ?v=X')
        translate = request.params.get('translate', 'true').lower() == 'true'
        activities = activity_protocol3.read_one_geojson_by_version(request, 
                                                                    uid, version, translate=translate)
        return render_to_response('json', activities, request)
    elif output_format == 'formtest':
        # Test if an Activity is valid according to the form configuration
        activities = activity_protocol3.read_one(request, uid=uid, public=False,
                                                 translate=False)
        version = request.params.get('v', None)
        if activities and 'data' in activities and len(activities['data']) != 0:
            for a in activities['data']:
                if 'version' in a:
                    if version is None:
                        version = str(a['version'])
                    if str(a['version']) == version:
                        categorylist = getCategoryList(request, 'activities')
                        return render_to_response('json',
                                                  checkValidItemjson(categorylist, a), request)
        return HTTPNotFound()
    # Output the areal statistics for the requested activity based on the
    # Web Processing Service
    elif output_format == 'statistics':

        # Try to get the base URL to the web processing service which provides
        # the areal statistics.
        # If no web processing service is configured, it is assumed that the
        # platform does not provide the areal statistics
        try:
            wps_host = request.registry.settings['lmkp.base_wps']
        except KeyError:
            raise HTTPNotFound()

        spatial_accuracy_map = get_spatial_accuracy_map(request)

        # Check if the spatial accuracy map is configured in the application.yml
        # file
        if spatial_accuracy_map is None:
            raise HTTPNotFound()

        # Show the details of an Activity by rendering the form in readonly
        # mode.
        activities = activity_protocol3.read_one(request, uid=uid, public=False,
                                                 translate=False)

        activity = activities['data'][0]
        coords = activity['geometry']['coordinates']

        for taggroup in activity['taggroups']:
            if taggroup['main_tag']['key'] == _(u"Spatial Accuracy"):
                spatial_accuracy = taggroup['main_tag']['value']

                buffer = spatial_accuracy_map[spatial_accuracy]

        wps_parameters = {
        "ServiceProvider": "",
        "metapath": "",
        "Service": "WPS",
        "Request": "Execute",
        "Version": "1.0.0",
        "Identifier": "BufferStatistics",
        "DataInputs": "lon=%s;lat=%s;epsg=4326;buffer=%s" % (coords[0], coords[1], buffer),
        "RawDataOutput": 'bufferstatistics@mimeType=application/json'
        }

        if not wps_host.endswith("?"):
            wps_host = "%s?" % wps_host
        for k, v in wps_parameters.items():
            wps_host = "%s%s=%s&" % (wps_host, k, v)

        log.debug("Accessing: %s" % wps_host)

        try:
            handle = urllib.urlopen(wps_host)
        except IOError:
            return HTTPInternalServerError("Remote server not accessible.")
        templateValues = json.loads(handle.read())
        templateValues['uid'] = uid
        templateValues['shortuid'] = uid.split("-")[0]
        return render_to_response(
                                  getTemplatePath(request, 'activities/statistics.mak'),
                                  templateValues,
                                  request
                                  )
    else:
        # If the output format was not found, raise 404 error
        raise HTTPNotFound()

@view_config(route_name='activities_read_one_history')
def read_one_history(request):
    # Handle the parameters (locale, profile)
    bv = BaseView(request)
    bv._handle_parameters()

    try:
        output_format = request.matchdict['output']
    except KeyError:
        output_format = 'html'

    uid = request.matchdict.get('uid', None)
    if check_valid_uuid(uid) is not True:
        raise HTTPNotFound()

    isLoggedIn, isModerator = checkUserPrivileges(request)
    activities, count = activity_protocol3.read_one_history(
                                                            request, uid=uid)
    activeVersion = None
    for a in activities:
        if 'statusName' in a:
            a['statusName'] = get_translated_status(request, a['statusName'])
        if a.get('statusId') == 2:
            activeVersion = a.get('version')

    templateValues = {
        'versions': activities,
        'count': count,
        'activeVersion': activeVersion,
        'isModerator': isModerator
    }
    templateValues.update({
                          'profile': get_current_profile(request),
                          'locale': get_current_locale(request)
                          })

    if output_format == 'html':
        template = 'activities/history.mak'

    elif output_format == 'rss':
        template = 'activities/history_rss.mak'

    else:
        raise HTTPNotFound("Requested output format is not supported.")

    return render_to_response(getTemplatePath(request, template),
                            templateValues, request)

@view_config(route_name='activities_read_one_public')
def read_one_public(request):
    """
    Read one Activity based on ID and return all versions of this Activity. Do
    not return any pending versions.
    Default output format: JSON
    """

    uid = request.matchdict.get('uid', None)
    if check_valid_uuid(uid) is not True:
        raise HTTPNotFound()

    try:
        output_format = request.matchdict['output']
    except KeyError:
        output_format = 'json'

    if output_format == 'json':
        activities = activity_protocol3.read_one(request, uid=uid, public=True)
        return render_to_response('json', activities, request)
    elif output_format == 'html':
        #@TODO
        return render_to_response('json', {'HTML': 'Coming soon'}, request)
    else:
        # If the output format was not found, raise 404 error
        raise HTTPNotFound()

@view_config(route_name='activities_read_one_active')
def read_one_active(request):
    """
    Read one Activity based on ID and return only the active version of the
    Activity.
    Default output format: JSON
    """

    try:
        output_format = request.matchdict['output']
    except KeyError:
        output_format = 'json'

    uid = request.matchdict.get('uid', None)
    if check_valid_uuid(uid) is not True:
        raise HTTPNotFound()

    if output_format == 'json':
        activities = activity_protocol3.read_one_active(request, uid=uid)
        return render_to_response('json', activities, request)
    elif output_format == 'html':
        #@TODO
        return render_to_response('json', {'HTML': 'Coming soon'}, request)
    else:
        # If the output format was not found, raise 404 error
        raise HTTPNotFound()

@view_config(route_name='activities_review', renderer='json')
def review(request):
    """
    Insert a review decision for a pending Activity
    Required POST attributes:
    - identifier (string, uid)
    - version (int)
    - review_decision (string): approve / reject
    - review_comment (string): nullable
    """
    
    _ = request.translate

    # Check if the user is logged in and he/she has sufficient user rights
    userid = authenticated_userid(request)
    if userid is None:
        raise HTTPUnauthorized(_('User is not logged in.'))
    if not isinstance(has_permission('moderate', request.context, request),
                      ACLAllowed):
        raise HTTPUnauthorized(_('User has no permissions to add a review.'))
    #user = Session.query(User).filter(User.username == authenticated_userid(request)).first()
    user = request.user

    # Check for profile
    profile_filters = activity_protocol3._get_spatial_moderator_filter(request)
    if profile_filters is None:
        raise HTTPBadRequest(_('User has no profile attached'))
    activity = Session.query(Activity).\
        filter(Activity.activity_identifier == request.POST['identifier']).\
        filter(Activity.version == request.POST['version']).\
        filter(profile_filters).\
        first()
    if activity is None:
        raise HTTPUnauthorized(_("The Item was not found or is not situated within the user's profiles"))

    # If review decision is 'approved', make sure that all mandatory fields are
    # there, except if it is to be deleted
    review_decision = request.POST['review_decision']
    if review_decision == 'approve':
        review_decision = 1
    elif review_decision == 'reject':
        review_decision = 2
    else:
        raise HTTPBadRequest(_('No valid review decision'))
    
    review_comment = request.POST['review_comment']
    
    if review_decision == 1: # Approved
        # Only check for mandatory keys if new version is not to be deleted
        # (has no tag groups)
        if len(activity.tag_groups) > 0:
            mandatory_keys = get_mandatory_keys(request, 'a')
            # Query keys
            activity_keys = Session.query(A_Key.key).\
                join(A_Tag).\
                join(A_Tag_Group, A_Tag.fk_tag_group == A_Tag_Group.id).\
                filter(A_Tag_Group.activity == activity)
            keys = []
            for k in activity_keys.all():
                keys.append(k.key)
            for mk in mandatory_keys:
                if mk not in keys:
                    raise HTTPBadRequest(_('Not all mandatory keys are provided'))

    # The user can add a review
    ret = activity_protocol3._add_review(request, activity, Activity, user, 
                                         review_decision, review_comment)
    
    if 'success' not in ret or ret['success'] is False and 'msg' not in ret:
        raise HTTPBadRequest(_('Unknown error'))
    
    if ret['success'] is True:
        request.session.flash(ret['msg'], 'success')
    else:
        request.session.flash(ret['msg'], 'error')

    return HTTPFound(location=request.route_url('activities_read_one_history',
                     output='html', uid=activity.identifier))

@view_config(route_name='activities_create', renderer='json')
def create(request):
    """
    Add a new activity.
    Implements the create functionality (HTTP POST) in the CRUD model

    Test the POST request e.g. with
    curl -u "user1:pw" -d @addNewActivity.json -H "Content-Type: application/json" http://localhost:6543/activities

    """

    _ = request.translate

    # Check if the user is logged in and he/she has sufficient user rights
    userid = request.user.username if request.user is not None else None

    if userid is None:
        raise HTTPForbidden()
    if not isinstance(has_permission('edit', request.context, request), ACLAllowed):
        raise HTTPForbidden()

    ids = activity_protocol3.create(request)

    response = {}

    # TODO: Do we still need translations here? Who is using this function
    # (since it is not Ext anymore)?

    if ids is not None:
        response['data'] = [i.to_json() for i in ids]
        response['total'] = len(response['data'])
        response['created'] = True
        response['msg'] = 'The Activity was successfully created.'
        request.response.status = 201
    else:
        response['created'] = False
        response['msg'] = 'No Deal was created.'
        request.response.status = 200

    return response

#@view_config(route_name='taggroups_model', renderer='string')
def model(request):
    # TODO: This is probably not needed anymore.
    """
    Controller that returns a dynamically generated JavaScript that builds the
    client-side TagGroup model, which is related (belongsTo / hasMany) to the
    static Activity model. The model is set up based on the defined mandatory
    and optional field in the configuration yaml file.
    """
    def _merge_config(parent_key, global_config, locale_config):
        """
        Merges two configuration dictionaries together
        """

        try:
            for key, value in locale_config.items():
                try:
                    # If the value has items it's a dict, if not raise an error
                    value.items()
                    # Do not overwrite mandatory or optional keys in the global
                    # config. If the key is not in the global config, append it
                    # to the configuration
                    if parent_key == 'mandatory' or parent_key == 'optional':
                        if key not in global_config:
                            _merge_config(key, global_config[key], locale_config[key])
                        # else if the key is in global_config do nothing
                    else:
                        _merge_config(key, global_config[key], locale_config[key])
                except:
                    global_config[key] = locale_config[key]
        # Handle the AttributeError if the locale config file is empty
        except AttributeError:
            pass

    object = {}

    object['extend'] = 'Ext.data.Model'
    object['belongsTo'] = 'Lmkp.model.Activity'

    # Get a stream of the config yaml file to extract the fields
    stream = open(config_file_path(), 'r')

    # Read the global configuration file
    global_stream = open(config_file_path(request), 'r')
    global_config = yaml.load(global_stream)

    # Read the localized configuration file
    try:
        locale_stream = open(locale_config_file_path(request), 'r')
        locale_config = yaml.load(locale_stream)

        # If there is a localized config file then merge it with the global one
        _merge_config(None, global_config, locale_config)

    except IOError:
        # No localized configuration file found!
        pass

    fields = []
    fieldsConfig = global_config['application']['fields']

    # language is needed because fields are to be displayed translated
    localizer = get_localizer(request)
    lang = Session.query(Language).filter(Language.locale == localizer.locale_name).first()
    if lang is None:
        lang = Language(1, 'English', 'English', 'en')

    # First process the mandatory fields
    for (name, config) in fieldsConfig['mandatory'].iteritems():
        o = _get_extjs_config(name, config, lang)
        if o is not None:
            o['mandatory'] = 1
            fields.append(o)
    # Then process also the optional fields
    for (name, config) in fieldsConfig['optional'].iteritems():
        o = _get_extjs_config(name, config, lang)
        if o is not None:
            fields.append(o)

    fields.append({'name': 'id', 'type': 'string'})

    object['fields'] = fields

    return "Ext.define('Lmkp.model.TagGroup', %s);" % object

def _check_difference(new, old, localizer=None):

    changes = {} # to collect the changes

    # not all attributes are of interest when looking at the difference between two versions
    # @todo: geometry needs to be processed differently, not yet implemented
    ignored = ['geometry', 'timestamp', 'id', 'version', 'username', 'userid', 'source',
        'activity_identifier', 'modified', 'new', 'deleted']



    # do comparison based on new version, loop through attributes
    if new is not None:
        for obj in new.__dict__:
            # not all attributes are of interest
            if obj not in ignored:
                # there is no older version (all attributes are new)
                if old is None:
                    # for some reason (?), attribute (although it will be set in later versions)
                    # can already be there (set to None) - we don't want it yet
                    if new.__dict__[obj] is not None:
                        changes[str(translate_key(None, localizer, obj))] = 'new' # attribute is new
                # there exists an older version
                else:
                    # attribute is not in older version
                    if obj not in old.__dict__:
                        changes[str(translate_key(None, localizer, obj))] = 'new' # attribute is new
                    # attribute is already in older version
                    else:
                        # for some reason (?), attribute can already be there in older versions
                        # (set to None). this should be treated as if attribute was not there yet
                        if old.__dict__[obj] is None and new.__dict__[obj] is not None:
                            changes[str(translate_key(None, localizer, obj))] = 'new' # attribute is 'new'
                        # check if attribute is the same in both versions
                        elif new.__dict__[obj] != old.__dict__[obj]:
                            changes[str(translate_key(None, localizer, obj))] = 'modified' # attribute was modified

    # do comparison based on old version
    if old is not None:
        # loop through attributes
        for obj in old.__dict__:
            if obj not in ignored and new is not None:
                # check if attribute is not there anymore in new version
                if obj not in new.__dict__:
                    changes[str(translate_key(None, localizer, obj))] = 'deleted' # attribute was deleted

    if new is not None: # when deleted
        new.changes = changes
    return new

#def _history_get_changeset_details(object):
#    """
#    Appends details from Changeset of an ActivityProtocol object based on the ID of the activity
#    and returns this object.
#    """
#    if object.id is not None:
#        changeset = Session.query(A_Changeset).filter(A_Changeset.fk_activity == object.id).first()
#        object.userid = changeset.user.id
#        object.username = changeset.user.username
#        object.source = changeset.source
#        return object


def _get_extjs_config(name, config, language):

    fieldConfig = {}

    # check if translated name is available
    originalKey = Session.query(A_Key.id).filter(A_Key.key == name).filter(A_Key.fk_a_key == None).first()

    # if no original value is found in DB, return None (this cannot be selected)
    if not originalKey:
        return None

    translatedName = Session.query(A_Key).filter(A_Key.fk_a_key == originalKey).filter(A_Key.language == language).first()

    if translatedName:
        fieldConfig['name'] = str(translatedName.key)
    else:
        fieldConfig['name'] = name

    type = 'string'
    try:
        config['type']
        if config['type'] == 'Number':
            type = 'number'
        if config['type'] == 'Date':
            type = 'number'
    except KeyError:
        pass

    fieldConfig['type'] = type

    return fieldConfig


def _get_config_fields():
    # TODO: Is this still needed?
    log.debug('DO NOT DELETE ME!!!')
    """
    Return a list of mandatory and optional fields extracted from the application
    configuration file (yaml)
    """
    # Get a stream of the config yaml file to extract the fields
    stream = open(config_file_path(), 'r')

    # Read the config stream
    yamlConfig = yaml.load(stream)

    # Get all (mandatory and optional) fields
    yamlFields = yamlConfig['application']['fields']

    # New list that holds the fields
    fields = []

    # First process the mandatory fields
    for name in yamlFields['mandatory']:
        fields.append(name)
    # Then process also the optional fields
    for name in yamlFields['optional']:
        fields.append(name)

    log.info(fields)

    return fields

def _handle_spatial_parameters(request):
    """
    Get the spatial extent of a request. The different options are checked in
    the following order:
    - request GET parameter {bbox}: use this parameter (handled by protocol) if
      provided. Special parameter: bbox=profile in which case use the profile
      boundary as bbox.
    - cookie _LOCATION_: if no bbox parameter was provided in GET, look for the
      map cookie to use as bbox.
    - profile boundary: if no GET parameter was provided and no cookie was found
      use the profile boundary as bbox.
    """

    spatialfilter = None

    bboxparam = request.params.get('bbox', None)
    if bboxparam is not None:

        if bboxparam == 'profile':
            # Use profile as boundary
            spatialfilter = 'profile'
            if 'epsg' in request.GET:
                del(request.GET['epsg'])

        else:
            # Use map extent from GET parameter
            spatialfilter = 'mapextentparam'
            epsg = request.params.get('epsg', None)
            if epsg is None:
                request.GET.add('epsg', '900913')
    else:
        # Use map extent from cookie
        location = request.cookies.get('_LOCATION_')
        if location is not None:
            location = urllib.unquote(location)
            if len(location.split(',')) == 4:
                spatialfilter = 'mapextentcookie'
                request.GET.add('bbox', location)
                request.GET.add('epsg', '900913')

    if spatialfilter is None:
        spatialfilter = 'profile'

    return spatialfilter
