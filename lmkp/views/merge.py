from lmkp.models.meta import DBSession as Session
from lmkp.views.activity_protocol2 import ActivityProtocol2
from pyramid.view import view_config

activity_protocol2 = ActivityProtocol2(Session)

@view_config(route_name='merge_versions', renderer='lmkp:templates/merge_versions.mak')
#@view_config(route_name='merge_versions', renderer='json')
def merge_versions(request):

    activities, count = activity_protocol2._history(request, 'af5de618-f9d1-4742-960e-a42708fda3ab',
                                                    ['active', 'pending'], versions=activity_protocol2._get_versions(request))

    # Get the latest active version:
    latest_active_version = None
    for a in activities:
        if a.get_status() == 'active' and latest_active_version is None:
            latest_active_version = a
        elif a.get_status() == 'active' and a.get_version() > latest_active_version.get_version():
            latest_active_version = a

    pending_versions = []
    for a in activities:
        if a.get_status() == 'pending':
            pending_versions.append(a)

    table = []

    nbrColumns = len(pending_versions) + 1;

    # First write the headers
    header_row = []
    header_row.append({'class': 'title', 'tags': [
                      {'key': 'version', 'value': latest_active_version.get_status()},
                      {'key': 'version', 'value': latest_active_version.get_version()}
                      ]})

    for pending in pending_versions:
        header_row.append({'class': 'title', 'tags': [
                          {'key': 'version', 'value': pending.get_status()},
                          {'key': 'version', 'value': pending.get_version()}
                          ]})

    table.append(header_row)

    for tg in latest_active_version.get_taggroups():
        additional_rows = []
        row = []

        col = {}
        for t in tg.get_tags():
            col['tags'] = [{'key': t.get_key(), 'value': t.get_value()}]
            col['class'] = ''
        row.append(col)

        index = 0
        for pending in pending_versions:

            col = {}
            old_taggroup, new_taggroup = _find_old_diff(pending, tg.get_id())
            if old_taggroup is not None:
                #print "*****************************************************"
                #print old_taggroup['tags']
                col['tags'] = old_taggroup['tags']
                col['class'] = 'remove'
                row.append(col)
            else:
                row.append({'class': '', 'tags': []})
                
            if new_taggroup is not None:

                additional_row = []

                for i in range(0, index + 1):
                    additional_row.append({'class': '', 'tags': []})

                additional_cell = {}
                additional_cell['tags'] = new_taggroup['tags']
                additional_cell['class'] = 'add'
                additional_row.append(additional_cell)

                for j in range(index + 1, nbrColumns-1):
                    additional_row.append({'class': '', 'tags': []})

                additional_rows.append(additional_row)


            index += 1

        table.append(row)
        for r in additional_rows:
            table.append(r)

    # Append all new taggroups at the end
    index = 0
    additional_rows = []
    for pending in pending_versions:
        new_taggroups = _find_new_taggroups(pending)

        for new_taggroup in new_taggroups:

            additional_row = []

            for i in range(0, index + 1):
                additional_row.append({'class': '', 'tags': []})

            additional_cell = {}
            additional_cell['tags'] = new_taggroup['tags']
            additional_cell['class'] = 'add'
            additional_row.append(additional_cell)

            for j in range(index + 1, nbrColumns-1):
                additional_row.append({'class': '', 'tags': []})

            additional_rows.append(additional_row)

        index += 1

    for r in additional_rows:
        table.append(r)


    return {'data': table}

def _find_old_diff(activity_feature, taggroup_id):
    """
    
    """

    diff = activity_feature._diff_info['diff']
    try:
        for old_taggroup in diff['old_attr']:
            if old_taggroup['id'] == taggroup_id:

                # Search the new tag / taggroup
                for old_tag in old_taggroup['tags']:

                    for new_taggroup in diff['new_attr']:
                        for new_tag in new_taggroup['tags']:
                            if new_tag['key'] == old_tag['key']:
                                return old_taggroup, new_taggroup

                return old_taggroup, None
    except KeyError:
        pass

    return None, None

def _find_new_taggroups(activity_feature):
    """

    """

    diff = activity_feature._diff_info['diff']

    new_taggroups = []

    for new_taggroup in diff['new_attr']:

        # Loop all tags and try to decide if there is no corresponding old one
        # Start with testing the main tag:
        main_tag = new_taggroup['main_tag']
        if main_tag is not None:
            try:
                is_new_taggroup = True
                for old_taggroup in diff['old_attr']:
                    for old_tag in old_taggroup['tags']:
                        if main_tag['key'] == old_tag['key']:
                            is_new_taggroup = False

                if is_new_taggroup:
                    new_taggroups.append(new_taggroup)
            except KeyError:
                new_taggroups.append(new_taggroup)
                break

        # If the main tag is empty, we have to check each tag
        else:

            for new_tag in new_taggroup['tags']:

                try:
                    is_new_taggroup = True
                    for old_taggroup in diff['old_attr']:
                        for old_tag in old_taggroup['tags']:
                            if new_tag['key'] == old_tag['key']:
                                is_new_taggroup = False

                    if is_new_taggroup:
                        #new_taggroups.append(new_taggroup)
                        pass
                except KeyError:
                    new_taggroups.append(new_taggroup)
                    break

    return new_taggroups