import logging
import mimetypes
import os
import csv

from lmkp.config import upload_max_file_size
from lmkp.config import valid_mime_extensions
from lmkp.config import translation_directory_path
from lmkp.models.database_objects import A_Key
from lmkp.models.database_objects import A_Value
from lmkp.models.database_objects import Category
from lmkp.models.database_objects import Language
from lmkp.models.database_objects import Profile
from lmkp.models.database_objects import SH_Key
from lmkp.models.database_objects import SH_Value
from lmkp.models.meta import DBSession as Session
from lmkp.views.form_config import getCategoryList
from pyramid.i18n import TranslationStringFactory
from pyramid.i18n import get_localizer
from pyramid.view import view_config
import simplejson as json
from sqlalchemy.orm import aliased

log = logging.getLogger(__name__)

_ = TranslationStringFactory('lmkp')

# Translatable hashmap with all possible statuses
statusMap = {
    'pending': _('pending'),
    'active': _('active'),
    'inactive': _('inactive'),
    'deleted': _('deleted'),
    'rejected': _('rejected'),
    'edited': _('edited')
}

# Translatable hashmap with all possible statuses
reviewdecisionMap = {
    'approved': _('approved'),
    'rejected': _('rejected')
}

# Translatable hashmap with all possible user groups
usergroupMap = {
    'editors': _('Editors'),
    'moderators': _('Moderators'),
    'administrators': _('Administrators'),
    'translators': _('Translators')
}

# Translatable hashmap with all possible user roles
# TODO: Once the involvements attributes are properly solved using YAML or
# something similar, the translation of the roles should not happen here anymore
stakeholderroleMap = {
    'Investor': _('Investor')
}

@view_config(route_name='ui_translation', renderer='javascript')
def ui_messages(request):

    # A dictionary that contains all messages that need to be translated in the
    # user interface.
    # Add new messages to this dict!
    uiMap = {
        # Status
        'status_name': _('Status'),
        'status_pending': statusMap['pending'],
        'status_active': statusMap['active'],
        'status_inactive': statusMap['inactive'],
        'status_deleted': statusMap['deleted'],
        'status_rejected': statusMap['rejected'],
        'status_edited': statusMap['edited'],

        # Review decision
        'reviewdecision_approved': reviewdecisionMap['approved'],
        'reviewdecision_rejected': reviewdecisionMap['rejected'],

        # User groups
        'usergroup_editors': usergroupMap['editors'],
        'usergroup_moderators': usergroupMap['moderators'],
        'usergroup_administrators': usergroupMap['administrators'],
        'usergroup_translators': usergroupMap['translators'],

        # Buttons
#        'button_add-attribute-filter': _('Add attribute filter'),
#        'button_add-new-tag': _('Add more specific information'),
#        'button_add-new-taggroup': _('Add further information'),
#        'button_add-time-filter': _('Add time filter'),
#        'button_back': _('Back'),
#        'button_browse': _('Browse'),
#        'button_cancel': _('Cancel'),
#        'button_clear': _('Clear'),
#        'button_close': _('Close'),
#        'button_compare': _('Compare'),
#        'button_continue': _('Continue'),
#        'button_delete': _('Delete'),
#        'button_edit': _('Edit'),
#        'button_filter-activate': _('Activate'),
#        'button_filter-delete': _('Delete'),
#        'button_link': _('Link'),
#        'button_map_base-layers': _('Base Layers'),
#        'button_map_context-layers': _('Context Layers'),
#        'button_map_satellite-map': _('Satellite Imagery'),
#        'button_map_show-legend': _('Show Legend'),
#        'button_map_street-map': _('Street Map'),
#        'button_map_terrain-map': _('Terrain Map'),
#        'button_next': _('Next'),
#        'button_no': _('No'),
#        'button_ok': _('OK'),
#        'button_refresh': _('Refresh'),
#        'button_review': _('Review'),
#        'button_save': _('Save'),
#        'button_submit': _('Submit'),
#        'button_upload': _('Upload'),
#        'button_yes': _('Yes'),

        # Tooltips
#        'tooltip_add-attribute-filter': _('Add a filter based on attribute'),
#        'tooltip_add-time-filter': _('Add a filter based on time'),
#        'tooltip_close-window': _('Close Window'),
#        'tooltip_compare': _('Compare'),
#        'tooltip_delete-file': _('Delete file'),
#        'tooltip_download-file': _('Download file'),
#        'tooltip_edit-file': _('Edit file'),
#        'tooltip_filter-activate': _('Click to activate this filter'),
#        'tooltip_filter-delete': _('Click to delete this filter'),
#        'tooltip_link': _('Permament link to current view'),
#        'tooltip_map_identify-feature': _('Identify Feature'),
#        'tooltip_map_pan': _('Pan'),
#        'tooltip_map_zoom-in': _('Zoom In'),
#        'tooltip_map_zoom-out': _('Zoom Out'),
#        'tooltip_map_zoom-to-profile-region': _('Zoom to Profile Region'),
#        'tooltip_missing-mandatory-key': _('Missing mandatory key!'),
#        'tooltip_not-all-attributes-shown': _('It is possible that not all attributes are shown here!'),
#        'tooltip_refresh': _('Refresh'),
#        'tooltip_remove-stakeholder': _('Remove this stakeholder'),
#        'tooltip_review': _('Review'),
#        'tooltip_review-involvement-not-possible': _('Involvement can not be reviewed. Click for more information.'),
#        'tooltip_review-involvement-possible': _('Involvement can be reviewed'),
#        'tooltip_submit-review': _('Submit Review'),
#        'tooltip_upload-new-file': _('Upload a new file'),
#        'tooltip_view-file': _('View file'),

        # General GUI text
#        'gui_anonymous': _('Anonymous'),
#        'gui_clear-selection': _('Clear Selection'),
#        'gui_confirm': _('Please confirm'),
#        'gui_currently-seeing-pending-version': _('You are seeing a {0} version, which needs to be reviewed before it is publicly visible.'),
#        'gui_currently-seeing-inactive-version': _('You are seeing an {0} version, which was previously active and publicly visible.'),
#        'gui_currently-seeing-deleted-version': _('You are seeing a {0} version, which was previously active and publicly visible.'),
#        'gui_currently-seeing-rejected-version': _('You are seeing a {0} version, which was never publicly visible.'),
#        'gui_currently-seeing-edited-version': _('You are seeing an {0} version, which was edited by a moderator and was never publicly visible.'),
#        'gui_date': _('Date'),
#        'gui_delete-all-filters': _('Delete all Filters'),
#        'gui_details': _('Details'),
#        'gui_filter-count': _('Filter ({0} active)'),
#        'gui_history': _('History'),
#        'gui_id': _('ID'),
#        'gui_language': _('Language'),
#        'gui_last-change': _('Last change'),
#        'gui_loading': _('Loading ...'),
#        'gui_no-attributes': _('No attributes to show'),
#        'gui_overview': _('Overview'),
#        'gui_paging-after': _('of {0}'),
#        'gui_paging-before': _('Page'),
#        'gui_please-confirm': _('Please confirm'),
#        'gui_previous-version': _('Previous Version'),
#        'gui_profile': _('Profile'),
#        'gui_search': _('Search'),
#        'gui_show-details': _('Show Details'),
#        'gui_show-pending-versions': _('Show pending versions'),
#        'gui_taggroups': _('Taggroups'),
#        'gui_timestamp': _('Timestamp'),
#        'gui_unknown': _('Unknown'),
#        'gui_user': _('User'),
#        'gui_version': _('Version'),
#        'gui_versions-pending': _('Versions pending'),

        # Feedback
#        'feedback_failure': _('Failure'),
#        'feedback_information': _('Information'),
#        'feedback_new-activity-created': _('The deal was successfully created. It will be reviewed shortly.'),
#        'feedback_new-activity-not-created': _('The deal could not be created.'),
#        'feedback_new-stakeholder-created': _('The Stakeholder was successfully created. It will be reviewed shortly.'),
#        'feedback_new-stakeholder-not-created': _('The Stakeholder could not be created.'),
#        'feedback_no-changes-made': _('No changes made'),
#        'feedback_no-changes-made-explanation': _('You did not make any changes.'),
#        'feedback_pending-edit-submitted': _('Edited changes were successfully submitted'),
#        'feedback_pending-edit-not-submitted': _('Edited changes could not be submitted'),
#        'feedback_some-attributes-not-editable-because-of-profile': _('Some of the attributes cannot be edited because they are not part of the currently selected profile.'),
#        'feedback_success': _('Success'),

        # Activities
#        'activities_add-new-activity': _('Add new Deal'),
#        'activities_attributes': _('Deal Attributes'),
#        'activities_compare-versions': _('Compare versions of Deal {0}'),
#        'activities_details-title': _('Details on Deal'),
#        'activities_edit-activity': _('Edit Deal (version {0})'),
#        'activities_filter-title': _('Filter Deal'),
#        'activities_new-step-1-part-1': _('Step 1: Please specify the location.'),
#        'activities_new-step-1-part-2': _('You may either select a point on the map or enter some coordinates.'),
#        'activities_new-step-1-explanation': _('You can drag and drop the point. Once you are done, click "Continue".'),
#        'activities_new-title': _('New Deal'),
#        'activities_paging-empty': _('No Deals found'),
#        'activities_paging-message': _('Displaying Deals {0} - {1} of {2}'),
#        'activities_pending-paging-empty': _('No pending Deals to display'),
#        'activities_pending-paging-message': _('Displaying pending Deals {0} - {1} of {2}'),
#        'activities_pending-versions': _('Pending versions of Deals'),
#        'activities_review-pending-versions': _('This deal has pending changes. Click to review them in a popup window.'),
#        'activities_review-versions': _('Review versions of Deal {0}'),
#        'activities_title': _('Deals'),

        # Involvements
#        'involvements_edit-involvement': _('Edit this involvement'),
#        'involvements_stakeholder-role': _('Role'),
#        'involvements_title': _('Involvements'),

        # Stakeholders
#        'stakeholders_add-stakeholders': _('Add Stakeholders'),
#        'stakeholders_associated-stakeholders': _('Associated Stakeholders'),
#        'stakeholders_attributes': _('Stakeholder Attributes'),
#        'stakeholders_compare-versions': _('Compare versions of Stakeholder {0}'),
#        'stakeholders_create-new-stakeholder': _('Create new Stakeholder'),
#        'stakeholders_details-title': _('Details on Stakeholder '),
#        'stakeholders_edit-stakeholder': _('Edit Stakeholder (version {0})'),
#        'stakeholders_filter-title': _('Filter Stakeholders'),
#        'stakeholders_no-associated-stakeholders-yet': _('No associated Stakeholders so far. You can search and select a Stakeholder using the Search field below. Or you can create a new Stakeholder by clicking on the button above.'),
#        'stakeholders_paging-empty': _('No Stakeholders found'),
#        'stakeholders_paging-message': _('Displaying Stakeholders {0} - {1} of {2}'),
#        'stakeholders_pending-paging-empty': _('No pending Stakeholders to display'),
#        'stakeholders_pending-paging-message': _('Displaying pending Stakeholders {0} - {1} of {2}'),
#        'stakeholders_pending-versions': _('Pending versions of Stakeholders'),
#        'stakeholders_review-pending-versions': _('This stakeholder has pending changes. Click to review them in a popup window.'),
#        'stakeholders_review-versions': _('Review versions of Stakeholder {0}'),
#        'stakeholders_search': _('Search Stakeholder'),
#        'stakeholders_select-stakeholder': _('Select Stakeholder'),
#        'stakeholders_title': _('Stakeholders'),

        # Comments
        # TODO: Clean up if it is clear that these strings are not needed anymore.
#        'comments_comment-by': _('comments_comment-by', default='Comment by'),
#        'comments_confirm-delete-comment': _('comments_confirm-delete-comment', default='Do you really want to delete this comment?'),
#        'comments_empty': _('comments_empty', default='No comments yet.'),
#        'comments_leave-comment': _('comments_leave-comment', default='Leave a comment'),
#        'comments_singular': _('comments_singular', default='Comment'),
#        'comments_title': _('comments_title', default='Comments'),

        # Files
#        'files_confirm-delete': _('Are your sure you want to delete the file {0}?'),
#        'files_edit-existing-file': _('Edit existing file'),
#        'files_file': _('File'),
#        'files_maximum-file-size': _('Maximum file size'),
#        'files_name': _('Name'),
#        'files_select-file': _('Select a file'),
#        'files_upload-new-file': _('Upload a new file'),
#        'files_uploading': _('Uploading ...'),
#        'files_valid-extensions': _('Valid file extensions'),

        # Moderator
#        'moderator_approving-creates-new-version': _('Approving this version will create a new version. (further additional information to come)'),
#        'moderator_changes-not-based-on-active': _('These changes are based on a version which is not the active version.'),
#        'moderator_missing-mandatory-keys': _('There are some mandatory keys missing. The item cannot be approved without these keys. Please click the "edit" button to add the missing keys.'),
#        'moderator_multiple-changes-pending': _('moderator_multiple-changes-pending', default='There are multiple changes pending! They may be conflicting.'),
#        'moderator_pending-version-title': _('moderator_pending-version-title', default='Pending version'),
#        'moderator_review-activity': _('Review Deal'),
#        'moderator_review-activity-side-of-involvement-first': _('The Activity of this involvement cannot be reviewed from the Stakeholder\'s side. Please review the Activity to approve or reject this involvement.'),
#        'moderator_review-comment': _('Review Comment'),
#        'moderator_review-decision': _('Review Decision'),
#        'moderator_review-not-possible': _('Review not possible'),
#        'moderator_review-pending-changes': _('Review pending changes'),
#        'moderator_review-stakeholder': _('Review Stakeholder'),
#        'moderator_show-pending-changes': _('Show pending changes'),
#        'moderator_stakeholder-has-no-active-version': _('The Stakeholder of this involvement has no active version and cannot be set active. Please review the Stakeholder first.'),

        # Filter
#        'filter_logical-operator': _('Logical Operator'),
#        'filter_logical-operator-and': _('and'),
#        'filter_logical-operator-or': _('or'),
#        'filter_operator-contains-case-insensitive': _('contains (case insensitive)'),
#        'filter_operator-contains-case-sensitive': _('contains (case sensitive)'),
#        'filter_operator-contains-not-case-insensitive': _('contains not (case insensitive)'),
#        'filter_operator-contains-not-case-sensitive': _('contains not (case sensitive)'),
#        'filter_operator-equals': _('equals'),
#        'filter_operator-greater-than': _('greater than'),
#        'filter_operator-greater-than-or-equal': _('greater than or equal'),
#        'filter_operator-is': _('is'),
#        'filter_operator-is-not': _('is not'),
#        'filter_operator-less-than': _('less than'),
#        'filter_operator-less-than-or-equal': _('less than or equal'),
#        'filter_operator-not-equals': _('not equals'),
#        'filter_specify-number-value': _('Specify number value'),
#        'filter_specify-text-value': _('Specify value'),

        # Translation
#        'translation_add-translation': _('Add translation'),
#        'translation_edit-translation': _('Edit translation'),
#        'translation_global-attribute': _('Global attribute'),
#        'translation_key-or-value': _('Key or Value'),
#        'translation_mandatory': _('Mandatory'),
#        'translation_original': _('Original'),
#        'translation_original-already-in-english': _('Original is already in English'),
#        'translation_translation': _('Translation'),

        # Administration
#        'administration_add-all-to-database': _('Add all to Database'),
#        'administration_batch-translation': _('Batch translation'),
#        'administration_is-in-database': _('Is in Database'),
#        'administration_languages': _('Languages'),
#        'administration_profiles': _('Profiles'),
#        'administration_user-management': _('User management'),

        # Input validations. These validations are defined in the YAML. In order
        # for them to be translateable, they need to appear here.
#        'input-validation_date-format': _('dd.mm.YYYY'),
#        'input-validation_invalid-date': _('{0} is not a valid date - it must be in the format {1}'),
#        'input-validation_number-greater-than-0': _('This number must be greater than 0'),
#        'input-validation_percentage': _('Percentage must be between 0 and 100'),
#        'input-validation_year': _('The year must be a number value between 1900 and 2100'),

#        'mappoints_coordinates-format': _('Format'),
#        'mappoints_coordinates-parse-error': _('The coordinates could not be parsed!'),
#        'mappoints_coordinates-title': _('GPS Coordinates'),
#        'mappoints_enter-coordinates': _('Enter GPS coordinates'),
#        'mappoints_set-point': _('Put point on the map'),
#        'mappoints_select-on-map': _('Select on map'),
    }

    # Get the localizer
    localizer = get_localizer(request)

    # Translate the user interface messages
    for i in uiMap:
        uiMap[i] = localizer.translate(uiMap[i])

    # Add information about locale to translation file so it is available to Ext
    db_lang = Session.query(Language).filter(Language.locale == localizer.locale_name).first()
    if db_lang is None: # fall back language: english
        db_lang = Language(1, 'English', 'English', 'en')
    uiMap['locale'] = db_lang.locale
    uiMap['locale_english-name'] = db_lang.english_name
    uiMap['locale_local-name'] = db_lang.local_name

    """
    For the table view of Activities and Stakeholders, Ext needs to know the key
    from the database (for example to correctly address table columns). It is
    also necessary to check if there are translations of these keys available.
    However, where columns are to be sorted, the original data index needs to be
    known as well.
    """

    # Activity keys: Must be exactly (!) the same as in global activity.yml
    # If you change anything here, make sure to check the copying to the uiMap
    # further below!
    aKeys = [
        'Spatial Accuracy',         # 0
        'Negotiation Status',       # 1
        'Country',                  # 2
        'Intended area (ha)',       # 3
        'Intention of Investment',  # 4
        'Data source',              # 5
        # Not needed for table but for special rendering of files tags
        # The files also appear in protocol.py around line 1548 ...
        'Files'                     # 6
    ]
    aKeysTranslateQuery = get_translated_db_keys(A_Key, aKeys, db_lang)
    aKeysTranslated = []
    for k in aKeys:
        translation = k
        for tk in aKeysTranslateQuery:
            if tk.original == k:
                translation = tk.translation
        aKeysTranslated.append(translation)

    # Store the keys to the uiMap: Store original (needed for sorting) as well
    # as the translation
    uiMap['activity_db-key-spatialaccuracy-original'] = aKeys[0]
    uiMap['activity_db-key-spatialaccuracy'] = aKeysTranslated[0]
    uiMap['activity_db-key-negotiationstatus-original'] = aKeys[1]
    uiMap['activity_db-key-negotiationstatus'] = aKeysTranslated[1]
    uiMap['activity_db-key-country-original'] = aKeys[2]
    uiMap['activity_db-key-country'] = aKeysTranslated[2]
    uiMap['activity_db-key-intendedarea-original'] = aKeys[3]
    uiMap['activity_db-key-intendedarea'] = aKeysTranslated[3]
    uiMap['activity_db-key-intentionofinvestment-original'] = aKeys[4]
    uiMap['activity_db-key-intentionofinvestment'] = aKeysTranslated[4]
    uiMap['activity_db-key-datasource-original'] = aKeys[5]
    uiMap['activity_db-key-datasource'] = aKeysTranslated[5]
    # For 'files', only the translated db-key is needed
    uiMap['activity_db-key-files'] = aKeys[6]

    # Stakeholder keys: Must be exactly (!) the same as in global
    # stakeholder.yml
    # If you change anything here, make sure to check the copying to the uiMap
    # further below!
    shKeys = [
        'Name',                 # 0
        'Country of origin'     # 1
    ]
    shKeysTranslateQuery = get_translated_db_keys(SH_Key, shKeys, db_lang)
    shKeysTranslated = []
    for k in shKeys:
        translation = k
        for tk in shKeysTranslateQuery:
            if tk.original == k:
                translation = tk.translation
        shKeysTranslated.append(translation)

    # Store the keys to the uiMap: Store original (needed for sorting) as well
    # as the translation
    uiMap['stakeholder_db-key-name-original'] = shKeys[0]
    uiMap['stakeholder_db-key-name'] = shKeysTranslated[0]
    uiMap['stakeholder_db-key-countryoforigin-original'] = shKeys[1]
    uiMap['stakeholder_db-key-countryoforigin'] = shKeysTranslated[1]

    # Define Lmkp.ts as class with static objects
    str = "Ext.define('Lmkp.ts',{\n"
    str += "\tstatics: {\n"
    str += "\t\tstrings: "
    json_ustr = json.dumps(uiMap, ensure_ascii=False, indent=8, sort_keys=True)
    str += json_ustr.encode('utf-8')
    str += ",\n"

    str += "\t\tmsg: function(key) {\n"
    str += "\t\t\treturn this.strings[key] ? this.strings[key] : key;\n"
    str += "\t\t}\n"
    str += "\t}\n"

    str += "});"

    return str

@view_config(route_name='language_store', renderer='json')
def language_store(request):
    data = []
    langs = Session.query(Language).all()
    for l in langs:
        data.append({
                    'locale': l.locale,
                    'english_name': l.english_name,
                    'local_name': l.local_name
                    })
    ret = {}
    ret['data'] = data
    ret['success'] = True
    ret['total'] = len(langs)
    return ret

@view_config(route_name='edit_translation', renderer='json', permission='translate')
def edit_translation(request):

    _ = request.translate

    success = False
    msg = _('Translation not successful')
    if 'original' and 'translation' and 'language' and 'keyvalue' and 'item_type' in request.params:
        # find language
        language = Session.query(Language).filter(Language.locale == request.params['language']).all()
        if language and len(language) == 1:
            if request.params['keyvalue'] == 'key':
                # Activity or Stakeholder?
                Key = None
                if request.params['item_type'] == 'activity':
                    Key = A_Key
                elif request.params['item_type'] == 'stakeholder':
                    Key = SH_Key
                # find original (fk_a_key empty)
                original = Session.query(Key).filter(Key.key == request.params['original']).filter(Key.original == None).all()
                if original and len(original) == 1:
                    # check if a translation of this key is already there
                    oldTranslation = Session.query(Key).filter(Key.original == original[0]).filter(Key.language == language[0]).all()
                    if oldTranslation and len(oldTranslation) == 1:
                        # translation found, just update it.
                        oldTranslation[0].key = request.params['translation']
                        success = True
                        msg = _('Updated translation')
                    else:
                        # no translation available yet, add it to DB
                        translation = Key(request.params['translation'])
                        translation.original = original[0]
                        translation.language = language[0]
                        Session.add(translation)
                        success = True
                        msg = _('Added translation')
                else:
                    msg = 'Original key not found' # should never happen
            if request.params['keyvalue'] == 'value':
                # Activity or Stakeholder?
                Value = None
                if request.params['item_type'] == 'activity':
                    Value = A_Value
                elif request.params['item_type'] == 'stakeholder':
                    Value = SH_Value
                # find original (fk_a_value empty)
                original = Session.query(Value).filter(Value.value == request.params['original']).filter(Value.original == None).all()
                if original and len(original) == 1:
                    # check if a translation of this value is already there
                    oldTranslation = Session.query(Value).filter(Value.original == original[0]).filter(Value.language == language[0]).all()
                    if oldTranslation and len(oldTranslation) == 1:
                        # translation found, just update it.
                        oldTranslation[0].value = request.params['translation']
                        success = True
                        msg = _('Updated translation')
                    else:
                        # no translation available yet, add it to DB
                        translation = Value(request.params['translation'])
                        translation.original = original[0]
                        translation.language = language[0]
                        Session.add(translation)
                        success = True
                        msg = _('Added translation')
                else:
                    msg = 'Original value not found' # should never happen
        else:
            msg = 'Language not unique or not found in DB' # should never happen
    
    return {
        'success': success,
        'msg': msg
    }

def get_translated_status(request, status):
    """
    Get the translated name of a status. A request is needed to know in which
    language to translate
    """
    localizer = get_localizer(request)
    if status in statusMap:
        return localizer.translate(statusMap[status])

def get_translated_db_keys(mappedClass, db_keys, db_lang):
    """
    Returns a query array with original and translated keys from the database.
    """
    
    if len(db_keys) == 0:
        return []
    
    translation = aliased(mappedClass)

    q = Session.query(
            mappedClass.key.label('original'),
            translation.key.label('translation')
        ).\
        join(translation, mappedClass.translations).\
        filter(mappedClass.key.in_(db_keys)).\
        filter(mappedClass.original == None).\
        filter(translation.language == db_lang).\
        all()

    if q is not None:
        return q

    # If nothing found, return None
    return []

# TODO: This does not necessarily belong here. Also, all the stuff needed for
# each view (languages, profiles, keys, ...) should be loaded in a single
# request for performance reasons.
def get_languages():
    return Session.query(Language.locale, Language.local_name).all()

def get_profiles():
    """
    Never return the global profile!
    """
    profiles = Session.query(Profile.code, Profile.code).all()
    ret = [p for p in profiles if p[0] != 'global']
    return ret

@view_config(route_name='extractDatabaseTranslation', renderer='string')
def extractDatabaseTranslation(request):
    """
    View to extract a csv-like representation of the attributes and categories
    in the database.
    Matchdict {type}: activities, stakeholders, categories
    Getparam {lang}: locale
    """

    type = request.matchdict.get('type')
    lang = request.params.get('lang', 'en')

    separator1 = ';'
    separator2 = '\n'

    if type in ['activities', 'stakeholders']:
        strings = _extractKeyValues(request, type, lang, separator1)

    elif type == 'categories':
        strings = _extractCategories(request, lang, separator1)

    else:
        strings = []

    return separator2.join(strings)

def _extractCategories(request, lang, separator):
    """
    Helper function to extract the categories of the database and their
    translations.
    """

    def _processCategories(originalCategoryList, translatedCategoryList, type, separator):

        categories = []
        strings = []

        originalCategories = sorted(originalCategoryList.getCategories(), key=lambda c:c.getId())
        translatedCategories = sorted(translatedCategoryList.getCategories(), key=lambda c:c.getId())

        for i, originalCategory in enumerate(originalCategories):
            translatedCategory = translatedCategories[i]

            # Add each category only once
            if originalCategory.getName() not in categories:
                categories.append(originalCategory.getName())
                strings.append(separator.join([
                    originalCategory.getName(),
                    translatedCategory.getTranslation(True),
                    type
                ]))

            # Subcategories
            originalSubcategories = sorted(originalCategory.getThematicgroups(), key=lambda c:c.getId())
            translatedSubcategories = sorted(translatedCategory.getThematicgroups(), key=lambda c:c.getId())

            for j, originalSubcategory in enumerate(originalSubcategories):
                translatedSubcategory = translatedSubcategories[j]

                # Add each subcategory only once
                if originalSubcategory.getName() not in categories:
                    categories.append(originalSubcategory.getName())
                    strings.append(separator.join([
                        originalSubcategory.getName(),
                        translatedSubcategory.getTranslation(True),
                        type
                    ]))

        return strings

    strings = []
    strings.append(separator.join([
        'Name (original)',
        'Name (translation)',
        'Type',
        'Additional comments'
    ]))

    for t in ['activities', 'stakeholders']:
        strings += _processCategories(
            getCategoryList(request, t, lang='en'),
            getCategoryList(request, t, lang=lang),
            t,
            separator)

    return strings


def _extractKeyValues(request, itemType, lang, separator):
    """
    Helper function to extract the keys and values of the database and their
    translations.
    """

    keys = []
    values = []
    strings = []
    valueStrings = []

    originalCategoryList = getCategoryList(request, itemType, lang='en')
    translatedCategoryList = getCategoryList(request, itemType, lang=lang)

    originalTags = sorted(originalCategoryList.getAllTags(), key=lambda t:t.getKey().getName())
    translatedTags = sorted(translatedCategoryList.getAllTags(), key=lambda t:t.getKey().getName())

    strings.append(separator.join([
        'Name (original)',              # [0]
        'Name (translation)',           # [1]
        'Helptext (original)',          # [2]
        'Helptext (translation)',       # [3]
        'Type',                         # [4]
        'Belongs to Key',               # [5]
        'Additional comments'           # [6]
    ]))

    # Keys
    for i, originalTag in enumerate(originalTags):

        originalKeyName = originalTag.getKey().getTranslatedName()

        # Add each key only once
        if originalKeyName in keys:
            continue

        keys.append(originalKeyName)
        originalKey = originalTag.getKey()
        translatedTag = translatedTags[i]
        translatedKey = translatedTag.getKey()
        strings.append(separator.join([
            originalKeyName,
            translatedKey.getTranslatedName(True),
            originalKey.getTranslatedHelptext(),
            translatedKey.getTranslatedHelptext(True),
            'key',
            '-'
        ]))

        originalValues = sorted(originalTag.getValues(), key=lambda val: val.getName())
        translatedValues = sorted(translatedTag.getValues(), key=lambda val: val.getName())

        if len(originalValues) > 0 and len(translatedValues) == len(originalValues):
            for j, originalValue in enumerate(originalValues):

                originalValueName = originalValue.getTranslation()

                # Add each value only once
                if originalValueName in values:
                    continue

                values.append(originalValueName)
                translatedValue = translatedValues[j]
                valueStrings.append(separator.join([
                    originalValueName,
                    translatedValue.getTranslation(True),
                    '',
                    '',
                    'value',
                    originalKeyName
                ]))

    return strings + valueStrings

@view_config(route_name='translation_files', renderer='json', permission='administer')
def translation_files(request):
    """
    List all the batch translation files available in the directory
    """

    ret = {'success': False}

    files = []

    # Empty file to allow deselecting a file
    files.append({
        'description': '',
        'delimiter': '',
        'item': '',
        'success': True,
        'filename': '-',
        'language': ''
    })

    dirList = os.listdir(translation_directory_path())
    for filename in dirList:
        try:
            stream = open("%s/%s" % (translation_directory_path(), filename), 'rb')
        except IOError:
            ret['msg'] = 'Unable to open file %s' % filename
            return ret

        csvReader = csv.reader(stream, delimiter=";")

        line = None

        try:
            line = csvReader.next()
        except StopIteration:
            # This happens if file is empty
            pass

        if line is None:
            item = {
                'description': 'Empty file',
                'success': False,
                'filename': filename + ' (seems to be empty)'
            }

        elif len(line) > 3:
            item = {
                'description': line[0],
                'delimiter': line[1],
                'item': line[2],
                'success': True,
                'filename': filename,
                'language': line[3]
            }
        else:
            item = {
                'description': 'Unable to parse file information.',
                'success': False,
                'filename': filename
            }
        files.append(item)

    ret['success'] = True
    ret['files'] = files

    return ret

@view_config(route_name='translation_batch', renderer='json', permission='administer')
def translation_batch(request):
    """
    Do a batch translation based on csv-like file in the following format:
    {translation} {delimiter} {value} [{delimiter} {helptext_original} {delimiter} {helptext_translation}]
    """

    def _translate_keyvalue(original, translation, TableItem, isKey,
        locale, helptext_translation):
        """
        Helper function to insert or update a single translation for a key or a
        value
        """

        # Query the database to find english entry of key or value
        if isKey:
            english_query = Session.query(TableItem).\
                filter(TableItem.key == original).\
                filter(TableItem.fk_language == 1)
        else:
            english_query = Session.query(TableItem).\
                filter(TableItem.value == original).\
                filter(TableItem.fk_language == 1)
        eng = english_query.all()

        if eng is None or len(eng) == 0:
            return {'success': False, 'msg': 'No english value found for "%s", translation "%s" not inserted.' % (original, translation)}

        for e in eng:
            # Check if translation already exists for value
            if isKey:
                originalEntry = e.original
                translation_query = Session.query(TableItem).\
                    filter(TableItem.original == originalEntry).\
                    filter(TableItem.language == locale)
            else:
                originalEntry = e
                translation_query = Session.query(TableItem).\
                    filter(TableItem.original == originalEntry).\
                    filter(TableItem.language == locale)
            translation_entry = translation_query.first()

            if translation_entry is None:
                # No translation found, insert a new translation
                if isKey:
                    new_translation = TableItem(translation, e.type)
                else:
                    new_translation = TableItem(translation)
                new_translation.language = locale
                new_translation.original = originalEntry
                if helptext_translation != '':
                    new_translation.helptext = helptext_translation
                Session.add(new_translation)
            else:
                # There is already a translation, update it
                if isKey:
                    translation_entry.key = translation
                else:
                    translation_entry.value = translation
                if helptext_translation != '':
                    translation_entry.helptext = helptext_translation

        return {'success': True, 'msg': 'Translation "%s" inserted for value "%s".' % (translation, original)}

    def _translate_category(original, translation, TableItem, locale):
        """
        Helper function to insert or update a single translation for a category.
        """

        # Query the database to find the english entry of the category
        english_query = Session.query(TableItem).\
            filter(TableItem.name == original).\
            filter(TableItem.fk_language == 1)
        eng = english_query.all()

        if len(eng) == 0:
            return {
                'success': False,
                'msg': 'No english value found for "%s", translation "%s" not inserted.' % (original, translation)
            }

        for e in eng:
            # Check if translation already exists
            translation_query = Session.query(TableItem).\
                filter(TableItem.original == e).\
                filter(TableItem.language == locale)
            translation_entry = translation_query.first()

            if translation_entry is None:
                # Insert a new translation
                new_translation = TableItem(translation)
                new_translation.language = locale
                new_translation.original = e
                Session.add(new_translation)
            else:
                # Update an existing translation
                translation_entry.name = translation

        return {
            'success': True,
            'msg': 'Translation "%s" inserted for value "%s".' % (translation, original)
        }

    ret = {'success': False}

    filename = request.params.get('filename', None)
    delimiter = request.params.get('delimiter', None)
    locale = request.params.get('locale', None)

    if filename is None or delimiter is None or locale is None:
        ret['msg'] = 'Not all needed values provided.'
        return ret

    if len(delimiter) != 1:
        ret['msg'] = 'Delimiter must be a 1-character string'
        return ret

    item_type = request.params.get('item_type', None)
    if item_type == 'A_Value':
        TableItem = A_Value
        translationType = 'value'
    elif item_type == 'A_Key':
        TableItem = A_Key
        translationType = 'key'
    elif item_type == 'SH_Value':
        TableItem = SH_Value
        translationType = 'value'
    elif item_type == 'SH_Key':
        TableItem = SH_Key
        translationType = 'key'
    elif item_type == 'Category':
        TableItem = Category
        translationType = 'category'
    else:
        ret['msg'] = 'Database item not found.'
        return ret

    if locale == 'en':
        ret['msg'] = 'The language "English" cannot be selected!'
        return ret

    language = Session.query(Language).\
        filter(Language.locale == locale).\
        first()

    try:
        stream = open("%s/%s" % (translation_directory_path(), filename), 'rb')
    except IOError:
        ret['msg'] = 'File (%s) not found' % filename
        return ret

    errorCount = 0
    insertCount = 0
    msgStack = []

    csvReader = csv.reader(stream, delimiter=str(delimiter))
    for row in csvReader:
        # Skip the first item
        if csvReader.line_num > 1:
            try:
                if row[0] != '' and row[1] != '':
                    if translationType in ['key', 'value']:
                        # Key or value
                        helptext_translation = ''
                        if len(row) >= 4:
                            helptext_translation = row[3]
                        inserted = _translate_keyvalue(row[0], row[1], TableItem,
                            translationType == 'key', language, helptext_translation)
                    else:
                        # Category
                        inserted = _translate_category(row[0], row[1], TableItem,
                            language)
                else:
                    inserted = None
            except:
                ret['msg'] = 'Wrong delimiter or wrong value type?'
                return ret
            if inserted is not None:
                msgStack.append(inserted)
                if inserted['success'] is True:
                    insertCount += 1
                elif inserted['success'] is None:
                    pass
                else:
                    errorCount += 1

    if errorCount == 0:
        ret['success'] = True

    ret['insertCount'] = insertCount
    ret['errorCount'] = errorCount
    ret['messages'] = msgStack

    return ret

