import logging
from pyramid.i18n import TranslationStringFactory
from pyramid.i18n import get_localizer
from pyramid.view import view_config
import simplejson as json

log = logging.getLogger(__name__)

_ = TranslationStringFactory('lmkp')

@view_config(route_name='edit_toolbar_config', renderer='javascript', permission='edit')
def edit_toolbar_config(request):
    """
    Returns an array of objects that configure an ExtJS toolbar for users with
    editing permission.
    """
    
    # Write the JavaScript and instantiate the global variable Lmkp.ts
    str = "Ext.namespace('Lmkp');\n"
    str += "Lmkp.toolbar = [{"
    str += "xtype: 'toolbar', dock: 'bottom', items: ['->',"
    str += "{id: 'edit-button', text: '%s'}," % _('Edit', default='Edit')
    str += "{id: 'add-button', text: '%s'}" % _('Add', default='Add')
    str += "]}];\n"
    
    str += "Lmkp.login_form = [{xtype: 'panel', html: '%s <b>%s</b>', border: 0, bodyCls: 'toolbar_username'}," % (_('Logged in as:', default='Logged in as:'), request.user.username)
    str += "{id: 'logout_button', text: '%s'}];\n" % _('Logout', default='Logout')

    str += "Lmkp.mainControllers = ['Main', 'Map', 'Filter', 'EditFilter'];\n"

    return str

