Ext.onReady(function(){
    var loadingMask = Ext.get('loading-mask');
    loadingMask.fadeOut({
        duration: 1000,
        remove: true
    });

    Ext.application({
        name: 'Lmkp',
        appFolder: 'static/app',

        requires: [
        'Lmkp.view.administrator.Outer',
        'Lmkp.view.login.Toolbar'
        ],

        controllers: [
        'activities.NewActivity',
        'activities.TagGroup',
        'administrator.Main',
        'editor.BaseLayers',
        'editor.ContextLayers',
        'editor.Detail',
        'editor.Map',
        'editor.Overview',
        'login.Toolbar',
        'moderator.Pending',
        'stakeholders.NewStakeholder',
        'stakeholders.StakeholderFieldContainer',
        'stakeholders.StakeholderSelection'
        ],

        launch: function() {
            Ext.create('Ext.container.Viewport', {
                layout: {
                    type: 'border',
                    padding: 0
                },
                items: [{
                    region: 'center',
                    xtype: 'lo_administratorouterpanel'
                }]
            });
        }
    });
});