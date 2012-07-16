Ext.onReady(function(){
    Ext.application({
        name: 'Lmkp',
        appFolder: 'static/app',

        requires: [
        'Lmkp.view.editor.Outer',
        ],

        controllers: [
        'login.Toolbar',
        'editor.GxMap',
        'editor.Detail',
        'Map',
        'editor.Table',
        'Stakeholder'
        ],

        launch: function() {
            Ext.create('Ext.container.Viewport', {
                layout: {
                    type: 'border',
                    padding: 0
                },
                items: [{
                    region: 'center',
                    xtype: 'lo_editorouterpanel'
                }]
            });
        }
    });
});