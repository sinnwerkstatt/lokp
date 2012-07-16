import fnmatch
from lmkp.config import profile_directory_path
import os
from pyramid.view import view_config
import re
import yaml

def get_current_profile(request):

    if '_PROFILE_' in request.params:
        return request.params['_PROFILE_']
    if '_PROFILE_' in request.cookies:
        return request.cookies['_PROFILE_']

    return 'global'

@view_config(route_name='profile_store', renderer='json')
def profile_store(request):
    """
    Return a JSON representation (can be used to build an Ext Store) of all
    available profiles.
    In order to appear in this list, a profile needs to be a valid YAML (.yml)
    file located in /profiles and it must contain an attribute "name".
    """

    data = []

    profile_dir = profile_directory_path(request)

    for root, dirs, files in os.walk(profile_dir):
        for filename in fnmatch.filter(files, 'application.yml'):
            file = "%s/%s" % (root, filename)
           
            try:
                curr_file = open(file, 'r')
                curr_yaml = yaml.load(curr_file)

                try:
                    name = curr_yaml["application"]["name"]
                    profile = re.split('\/', root)[-1]
                    geometry = curr_yaml['application']['geometry']

                    if profile == '' or profile is None:
                        profile = 'global'

                    data.append({
                                'name': name,
                                'profile': profile,
                                'geometry': geometry,
                                'active': get_current_profile(request) == profile
                                })

                except TypeError:
                    # Profile is empty.
                    pass

                except KeyError:
                    # No attribute "name".
                    pass

            except IOError:
                # No profile found.
                pass

    ret = {}
    ret['data'] = data
    ret['success'] = True
    ret['total'] = len(data)

    return ret