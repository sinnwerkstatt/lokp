Ext.define('Lmkp.view.login.Toolbar' ,{
    extend: 'Ext.toolbar.Toolbar',
    alias : ['widget.lo_logintoolbar'],

    defaults: {
        labelWidth: 60,
        xtype: 'combobox'
    },

    requires: [
        'Ext.util.*'
    ],

    items: [{
        fieldLabel: Lmkp.ts.msg("gui_profile"),
        id: 'profile_combobox',
        itemId: 'profile_combobox',
        queryMode: 'local',
        store: 'Profiles',
        displayField: 'name',
        value: Ext.util.Cookies.get('_PROFILE_') ? Ext.util.Cookies.get('_PROFILE_') : 'global',
        valueField: 'profile',
        forceSelection: true,
        editable: false,
        // Hide this combobox if the application is embedded
        hidden: Lmkp.is_embedded
    },{
        fieldLabel: Lmkp.ts.msg("gui_language"),
        id: 'language_combobox',
        queryMode: 'local',
        store: 'Languages',
        displayField: 'local_name',
        value: Lmkp.ts.msg("locale"),
        valueField: 'locale',
        forceSelection: true,
        editable: false
    }, '->', Lmkp.login_form]
});