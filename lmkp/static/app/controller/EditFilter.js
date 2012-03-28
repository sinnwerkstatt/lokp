Ext.define('Lmkp.controller.EditFilter', {
    extend: 'Ext.app.Controller',

    models: ['Config', 'ActivityGrid'],
    stores: ['Config', 'ActivityGrid'],

    views: ['Filter'],

    init: function() {
        this.control({
            'filterPanel panel[id=detailPanel] button[id=edit-button]':{
                click: this.onEditButtonClick
            },
            'filterPanel panel[id=detailPanel] button[id=add-button]':{
                click: this.onAddButtonClick
            }
        });
    },

    onEditButtonClick: function(button, event, eOpts){
        Ext.Ajax.request({
            url: '/config/form',
            success: function(response){
                var formConfig = Ext.decode(response.responseText);

                // Get the selected item in the grid panel
                var gridPanel = Ext.ComponentQuery.query('filterPanel gridpanel[id=filterResults]')[0];
                var selection = gridPanel.getSelectionModel().getSelection()[0];

                // Set up the window title
                var title = "Edit " + selection.get("name");

                // Create a new form panel that is put in the edit window
                var formPanel = Ext.create('Ext.form.Panel',{
                    border: false,
                    buttons: [{
                        text: "Save"
                    }],
                    items: formConfig
                });

                // Load the selected record
                formPanel.loadRecord(selection);

                // Create the new edit window and show it
                Ext.create('Ext.window.Window', {
                    title: title,
                    height: 200,
                    width: 400,
                    layout: 'fit',
                    items: [
                    formPanel
                    ]
                }).show();

            },
            scope: this
        })
    },

    onAddButtonClick: function(button, event, eOpts){
        console.log("Add new activity");
    }

});
