import os.path
import re

from lmkp.models.database_objects import *
from lmkp.models.meta import DBSession as Session
from lmkp.views import shapefile
from pyramid.view import view_config
from sqlalchemy.sql.expression import and_

@view_config(route_name='lao_read_stakeholders', renderer='json')
def lao_read_stakeholders2(request):

    filepath = "%s/documents/laos/data/lc_champasak_attapeu_grouped_4326" % os.path.dirname(os.path.dirname(__file__))

    # This dictionary maps the attribute in the Shapefile to the mandatory and
    # optional fields
    attributeMap = {
        2: 'Name',
        3: 'Country of origin'
    }

    # Map the country names from the input file to the defined countries in the
    # database
    countriesMap = {
    "Hongkong": "China",
    "Korea": "South Korea"
    }


    shp = shapefile.Reader(filepath)
    records = shp.shapeRecords()


    # Main dict to output
    stakeholderDiffObject = {}
    stakeholderDiffObject['stakeholders'] = []

    # List of already considered stakeholders (name)
    knownStakeholders = []

    # Retreive every feature with its geometry and attributes
    for record in records:

        # A dict for the current stakeholder
        stakeholderObject = {}
        stakeholderObject['taggroups'] = []

        # Handle the name
        nameIndex = 2
        name = record.record[nameIndex]

        # If this stakeholder is already in the list of known stakeholders,
        # go to the next record
        if name in knownStakeholders:
            continue

        # Check if the name is not empty
        if name.strip() != '' and name is not None:
            stakeholderObject['taggroups'].append(create_taggroup_dict(attributeMap[nameIndex], name))
            knownStakeholders.append(name)

        # Handle the country of origin
        countryIndex = 3
        country = record.record[countryIndex]

        # Check if the country is not empty and add a new taggroup
        if country.strip() != '':

            # Handle joint venture stakeholders from different countries
            # In the source Shapefile different countries are connected using
            # hyphens.
            if len(country.split('-')) > 1:
                countries = country.split('-')
                for c in countries:
                    value = c.strip()

                    if value in countriesMap:
                        value = countriesMap[value]

                    stakeholderObject['taggroups'].append(create_taggroup_dict(attributeMap[countryIndex], value))
            else:

                value = country.strip()
                if value in countriesMap:
                    value = countriesMap[value]

                stakeholderObject['taggroups'].append(create_taggroup_dict(attributeMap[countryIndex], value))

        # Finally add the current stakeholder to the list of stakeholders
        stakeholderDiffObject['stakeholders'].append(stakeholderObject)

    return stakeholderDiffObject

@view_config(route_name='lao_read_activities', renderer='json')
def lao_read_activities2(request):
    filepath = "%s/documents/laos/data/lc_champasak_attapeu_grouped_4326" % os.path.dirname(os.path.dirname(__file__))

    # This dictionary maps the attribute in the Shapefile to the mandatory and
    # optional fields
    attributeMap = {
        2: 'Name', # name_of_co
#        59: 'Year of agreement', # Date_Sign
        117: 'Negotiation Status', # txt_status
        127: 'Intended area (ha)', # Area_F
        135: 'Intention of Investment' # Subsector1
    }

    statusMap = {
    'Approved for surveying': 'Contract signed',
    'Not operational': 'Contract cancelled',
    'Operational': 'Contract signed'
    }

    shp = shapefile.Reader(filepath)
    records = shp.shapeRecords()

    # Main dict to output
    activityDiffObject = {}
    activityDiffObject['activities'] = []

    # List of already used stakeholders. This is necessary to increase the
    # reference version in involvements.
    usedStakeholders = []

    # Retreive every feature with its geometry and attributes
    for record in records:

        # A dict for the current stakeholder
        activityObject = {}
        activityObject['taggroups'] = []
        stakeholdersObject = []

        for k, value in attributeMap.items():

            if k == 2:

                investor_name = record.record[k]

                sh = Session.query(Stakeholder).join(SH_Tag_Group).\
                    join(SH_Tag, SH_Tag_Group.id == SH_Tag.fk_sh_tag_group).\
                    join(SH_Key).\
                    join(SH_Value).filter(and_(SH_Key.key == 'Name', SH_Value.value == investor_name)).first()

                if sh is not None:

                    # Version:
                    version = usedStakeholders.count(str(sh.stakeholder_identifier))

                    # TODO: For the moment, add the same stakeholder only once
                    # because it crashes otherwise (Changeset issue).
                    if version == 0:
                        usedStakeholders.append(str(sh.stakeholder_identifier))

                        stakeholdersObject.append({"id": str(sh.stakeholder_identifier), "op": "add", "role": 6, "version": (version + 1)})
                        activityObject['stakeholders'] = stakeholdersObject

                

#            if k == 59:
#                year = 0
#                dates = record.record[k].split('/')
#                if len(dates) == 3:
#                    lastdigits = int(dates[-1])
#                    if lastdigits > 20:
#                        year = 1900 + lastdigits
#                    else:
#                        year = 2000 + lastdigits
#
#                activityObject['taggroups'].append(create_taggroup_dict(attributeMap[k], year))

            if k == 117:
                if record.record[k].strip() != '' and statusMap[record.record[k]] is not None:
                    activityObject['taggroups'].append(create_taggroup_dict(value, statusMap[record.record[k]]))
                else:
                    activityObject['taggroups'].append(create_taggroup_dict(value, 'Contract signed'))

            if k == 127:
                activityObject['taggroups'].append(create_taggroup_dict(value, float(record.record[k])))

            if k == 135:
                #value = guess_intention(record.record[k])
                activityObject['taggroups'].append(create_taggroup_dict(value, record.record[k]))

        # The country is obviously Laos
        activityObject['taggroups'].append(create_taggroup_dict('Country', 'Laos'))
        # Not sure about these sources
        activityObject['taggroups'].append(create_taggroup_dict('Data source', 'Government sources'))
        activityObject['taggroups'].append(create_taggroup_dict('Spatial Accuracy', 'better than 100m'))

        # Add geometry to activity
        activityObject['geometry'] = {'coordinates': [record.shape.points[0][0], record.shape.points[0][1]], 'type': 'Point'}

        activityDiffObject['activities'].append(activityObject)

    return activityDiffObject


def create_tag_dict(key, value):
    return {'key': key, 'op': 'add', 'value': value}


def create_taggroup_dict(key, value):
    taggroup = {}
    taggroup['op'] = 'add'
    taggroup['tags'] = []
    taggroup['tags'].append({"key": key, "value": value, "op": "add"})
    taggroup['main_tag'] = {"key": key, "value": value}
    return taggroup

def guess_intention(value):
    """
      - Agriculture
      - Forestry
      - Mining
      - Tourism
      - Industry
      - Conservation
      - Renewable energy
      - Other
    """

    if re.match(r'.*oil.*|.*rubber.*|.*cassava.*|.*shrimp.*|.*tapioca.*|.*sugar.*|.*tree.*|.*plantation.*', value, re.I):
        return "Agriculture"
    if re.match(r'.*agro.*|.*coffee.*', value, re.I):
        return "Agriculture"
    if re.match(r'.*acacia.*|.*onion.*', value, re.I):
        return "Agriculture"
    if re.match(r'.*corn.*|.*vegetables.*|.*tree.*', value, re.I):
        return "Agriculture"
    if re.match(r'.*eucalyptus.*|.*goats.*|.*seed.*', value, re.I):
        return "Agriculture"

    if re.match(r'.*tourism.*|.*turi.*|.*hotel.*', value, re.I):
        return "Tourism"

    if re.match(r'.*dam.*|.*ember.*', value, re.I):
        return "Renewable energy"

    if re.match(r'.*port.*|.*funitur.*|.*furnitur.*', value, re.I):
        return "Other"

    if re.match(r'.*clay.*|.*gold.*|.*sand.*', value, re.I):
        return "Mining"

    if re.match(r'.*gas.*|.*sawmill.*|.*additives.*', value, re.I):
        return "Industry"


    return 'Other'