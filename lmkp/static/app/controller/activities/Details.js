Ext.define('Lmkp.controller.activities.Details', {
    extend: 'Ext.app.Controller',

    refs: [{
        ref: 'activityDetailWindow',
        selector: 'lo_activitydetailwindow'
    },{
        ref: 'mapPanel',
        selector: 'lo_publicmappanel'
    }],

    init: function() {
        this.control({
            'lo_activitydetailwindow gridpanel[itemId="historyPanel"]': {
                select: this.onHistoryPanelSelect
            },
            'lo_activitydetailwindow button[itemId="closeWindowButton"]': {
                click: this.onCloseWindowButtonClick
            },
            'lo_activitydetailwindow lo_activitypanel lo_taggrouppanel button[name=editTaggroup]': {
                click: this.onEditTaggroupButtonClick
            },
            'lo_activitydetailwindow lo_stakeholderpanel lo_taggrouppanel button[name=editTaggroup]': {
                click: this.onEditSHTaggroupButtonClick
            },
            'lo_involvementpanel button[name=editInvolvementButton]': {
                click: this.onEditInvolvementButtonClick
            }
        });
    },
    
    onHistoryPanelSelect: function(rowModel, record, index, eOpts){
        this.getActivityDetailWindow()._populateDetails(record);
    },

    onCloseWindowButtonClick: function(){
        this.getActivityDetailWindow().close();
    },

    /**
     * If any Activitiy Tag Group is to be edited, show same window as when 
     * adding a new Activity but fill out the form with the current values.
     */
    onEditTaggroupButtonClick: function(button) {
        // If the button is inside an Involvement panel, the button belongs to a
        // Stakeholder. In this case do not show the window for Activities. 
        // Instead, wait for another function ('onEditSHTaggroupButtonClick' 
        // further down) to show correct window.
        if (!button.up('lo_involvementpanel')) {
            var activityPanel = button.up('lo_activitypanel');
            if (activityPanel && activityPanel.contentItem) {
                var newActivityController = this.getController('activities.NewActivity');
                newActivityController.showNewActivityWindow(
                    // Provide current item
                    activityPanel.contentItem
                    );
            }
        }
    },
    
    /**
     * If any Stakeholder Tag Group (inside an Involvement panel) is to be 
     * edited, show same window as when adding a Stakeholder but fill out the 
     * form with the current values.
     */
    onEditSHTaggroupButtonClick: function(button) {
        // Make sure the button is inside an Involvement panel
        if (button.up('lo_involvementpanel')) {
            var stakeholderPanel = button.up('lo_stakeholderpanel');
            if (stakeholderPanel && stakeholderPanel.contentItem) {
                var newActivityController = this.getController('activities.NewActivity');
                newActivityController.showNewStakeholderWindow(
                    // Provide current item
                    stakeholderPanel.contentItem
                    );
            }
        }
    },
    
    onEditInvolvementButtonClick: function(button) {
        var activityPanel = button.up('lo_activitypanel');
        if (activityPanel && activityPanel.contentItem) {
            var newActivityController = this.getController('activities.NewActivity');
            newActivityController.showNewActivityWindow(
                // Provide current item
                activityPanel.contentItem,
                1 // 1: Involvements
                );
        }
    }

});