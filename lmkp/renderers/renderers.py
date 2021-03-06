import StringIO
import csv

from geojson.codec import GeoJSONEncoder
from geojson.mapping import to_mapping
from lmkp.models.database_objects import *
from lmkp.models.meta import DBSession as Session
from logging import getLogger
from papyrus.renderers import Encoder
from pyramid.i18n import get_localizer
from shapely import wkb
import simplejson as json
from sqlalchemy.sql.expression import and_
from uuid import UUID

log = getLogger(__name__)

def translate_key(request, localizer, key):
    # Get the language independent key id
    try:
        key_id = Session.query(A_Key.id).filter(A_Key.key == key).first()[0]
    except:
        return key

    if localizer is not None:
        # Create the filter
        f = and_(A_Key.fk_a_key == key_id, Language.locale == localizer.locale_name)
        # And query the translated key
        translated_key = Session.query(A_Key.key).join(Language).filter(f).first()

    try:
        return translated_key[0]
    except TypeError:
        return key
    except UnboundLocalError:
        return key

def translate_value(request, localizer, value):
    # Get the language independent value id
    try:
        value_id = Session.query(A_Value.id).filter(A_Value.value == value).first()[0]
    except:
        return value

    if localizer is not None:
        # Create the filter
        f = and_(A_Value.fk_a_value == value_id, Language.locale == localizer.locale_name)
        # And query the translated value
        translated_value = Session.query(A_Value.value).join(Language).filter(f).first()

    try:
        return translated_value[0]
    except TypeError:
        return value
    except UnboundLocalError:
        return key

class JsonRenderer(object):
    """
    UUID compatible JSON renderer
    """

    def __call__(self, info):

        def _render(value, system):

            # Get the request and set the response content type to JSON
            request = system.get('request')
            if request is not None:
                response = request.response
                response.content_type = 'application/json'

            # Get the localizer from the request
            localizer = get_localizer(request)

            class ActivityFeatureEncoder(json.JSONEncoder):
                """
                A JSON encoder to encode Activity Features
                """

                def default(self, obj):

                    feature = {}
                    for d in obj.__dict__:

                        # Translate the key
                        key = translate_key(request, localizer, d)

                        if obj.__dict__[d] is None:
                            continue

                        # Cast the attribute values.
                        # It is important to check first if it's an global unique
                        # id, else the uuid is casted to integer.
                        if isinstance(obj.__dict__[d], UUID):
                            feature[key] = str(obj.__dict__[d])
                        else:
                            # First try if it's possible to cast the value to integer
                            try:
                                feature[key] = int(obj.__dict__[d])
                            except:
                                # As next we try to cast it to float
                                try:
                                    feature[key] = float(obj.__dict__[d])
                                except:
                                    try:
                                        # Finally the value is casted to unicode and translated
                                        # according to the language in the request
                                        feature[key] = translate_value(request, localizer, unicode(obj.__dict__[d]))
                                    except:
                                        pass

                    return feature

            return json.dumps(value, cls=ActivityFeatureEncoder)

        return _render

class GeoJsonRenderer(object):

    def __init__(self, jsonp_param_name='callback',
                 collection_type=geojson.factory.FeatureCollection):
        self.jsonp_param_name = jsonp_param_name
        if isinstance(collection_type, basestring):
            collection_type = getattr(geojson.factory, collection_type)
        self.collection_type = collection_type

    def __call__(self, info):
        def _render(value, system):
            if isinstance(value, (list, tuple)):
                value = self.collection_type(value)
            ret = geojson.dumps(value, cls=Encoder, use_decimal=True)
            request = system.get('request')
            if request is not None:
                response = request.response
                ct = response.content_type
                if ct == response.default_content_type:
                    callback = request.params.get(self.jsonp_param_name)
                    if callback is None:
                        response.content_type = 'application/json'
                    else:
                        response.content_type = 'text/javascript'
                        ret = '%(callback)s(%(json)s);' % {'callback': callback,
                            'json': ret}
            return ret
        return _render


class JavaScriptRenderer(object):
    def __call__(self, info):

        def _render(value, system):

            # Get the request and set the response content type to JSON
            request = system.get('request')
            if request is not None:
                response = request.response
                response.content_type = 'application/javascript'

            return value

        return _render


class CSVRenderer(object):
    def __call__(self, info):

        def _render(value, system):

            fout = StringIO.StringIO()
            writer = csv.writer(fout, delimiter=';', quoting=csv.QUOTE_ALL)
            writer.writerow(value['header'])
            writer.writerows(value['rows'])

            resp = system['request'].response
            resp.content_type = 'text/csv'
            resp.content_disposition = 'attachment;filename="report.csv"'
            return fout.getvalue()

        return _render
