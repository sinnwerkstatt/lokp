/**
 * Subclass of Lmkp.view.items.Details window.
 */
Ext.define('Lmkp.view.activities.Details', {
    extend: 'Lmkp.view.items.Details',
    alias: ['widget.lo_activitydetailwindow'],

    centerPanelType: 'lo_activitypanel',
    
    config: {
        centerPanel: null,
        historyPanel: null,
        historyStore: null
    },
    
    itemId: 'activityDetailWindow',

    layout: 'border',

    requires: [
    'Lmkp.view.activities.ActivityPanel',
    'Lmkp.view.comments.CommentPanel'
    ],

    initComponent: function(){

        var activity_identifier;

        this.activity ? activity_identifier = this.activity.get('id') : activity_identifier = this.activity_identifier

        this.centerPanel = Ext.create('Ext.panel.Panel',{
            autoScroll: true,
            layout: 'anchor',
            itemId: 'activityDetailCenterPanel'
        });

        this.historyStore = Ext.create('Ext.data.Store', {
            autoLoad: true,
            autoScroll: true,
            listeners: {
                load: function(store, records, successful){
                    var firstRecord = store.first();
                    this._populateDetails(firstRecord);
                },
                scope: this
            },
            storeId: 'historyStore',
            // all are needed to build relation
            requires: [
            'Lmkp.model.Activity',
            'Lmkp.model.TagGroup',
            'Lmkp.model.Tag',
            'Lmkp.model.MainTag',
            'Lmkp.model.Involvement',
            'Lmkp.model.Point'
            ],

            model: 'Lmkp.model.Activity',

            pageSize: 10,
            proxy: {
                extraParams: {
                    involvements: 'full'
                },
                reader: {
                    root: 'data',
                    type: 'json',
                    totalProperty: 'total'
                },
                simpleSortMode: true,
                sortParam: 'order_by',
                startParam: 'offset',
                type: 'ajax',
                url: '/activities/history/' + activity_identifier
            },
            remoteSort: true
        });


        this.historyPanel = Ext.create('Ext.grid.Panel',{
            collapsible: true,
            collapseMode: 'header',
            columns: [{
                dataIndex: 'version',
                flex: 1,
                text: 'Version'
            }, {
                dataIndex: 'status',
                flex: 1,
                text: 'Status'
            }, {
                dataIndex: 'timestamp',
                flex: 1,
                text: 'Timestamp'
            }],
            itemId: 'historyPanel',
            region: 'west',
            store: this.historyStore,
            title: 'History',
            width: 250
        });

        this.items = [{
            bodyPadding: 5,
            layout: 'card',
            margin: 3,
            itemId: 'activityDetailWizardPanel',
            items: [ this.centerPanel ],
            region: 'center',
            title: 'Details'
        },
        this.historyPanel
        ];

        this.title = 'Details on Activity ' + activity_identifier;

        this.callParent(arguments);
    }	
});