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
        'Lmkp.view.moderator.Outer',
        'Lmkp.view.login.Toolbar'
        ],

        controllers: [
        'activities.NewActivityWindow',
        'login.Toolbar',
        'editor.Detail',
        'editor.Overview',
        'moderator.Pending',
        'Stakeholder',
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
                    xtype: 'lo_moderatorouterpanel'
                }]
            });
        }
    });
});