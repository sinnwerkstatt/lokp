// TODO: Clean up here ...

Ext.define('Lmkp.store.StakeholderGrid', {
    extend: 'Ext.data.Store',

    requires: [
    'Lmkp.model.Stakeholder',
    'Lmkp.model.TagGroup',
    'Lmkp.model.Tag',
    'Lmkp.model.MainTag',
    'Lmkp.model.Involvement'
    ],

    model: 'Lmkp.model.Stakeholder',

    pageSize: 10,
    remoteSort: true,

    proxy: {
        type: 'ajax',
        url: '/stakeholders/json',
        reader: {
            root: 'data',
            type: 'json',
            totalProperty: 'total'
        },
        startParam: 'offset',
        simpleSortMode: true,
        sortParam: 'order_by',
        extraParams: {
            // Do not load involvements in grid for faster loading
            involvements: 'none'
        }
    },

    doCustomSort: function(dataIndex, direction) {
        // Do the sort
        this.sort({
            property: dataIndex,
            direction: direction
        });
    },

    setInitialProxy: function() {

        // Update url
        this.proxy.url = '/stakeholders';

        // Delete any reference to activities
        delete this.proxy.extraParams['a_id'];
        delete this.proxy.extraParams['return_a'];
        
        // Show or hide pending stakeholders?
        this.getPendingCheckbox();
    },
    
    deleteFilters: function() {
        // Delete any filters
        var prefix_a = 'a__';
        var prefix_sh = 'sh__';
        for (var i in this.proxy.extraParams) {
            if (i.slice(0, prefix_a.length) == prefix_a
                || i.slice(0, prefix_sh.length) == prefix_sh) {
                delete this.proxy.extraParams[i];
            }
        }
    },
    
    syncWithActivities: function(extraParams) {

        // Do not directly use extraParams provided by other store (any changes
        // made on these params would also affect the other store). Instead,
        // create a copy of the parameters.

        // (No longer sure what the bounds parameter was supposed to mean, Adrian)
        var ep = new Object();
        for (var e in extraParams) {
            // Do not copy parameter 'bounds''
            if (e != 'bounds') {
                ep[e] = extraParams[e];
            }
        }

        // Update url
        this.proxy.url = '/stakeholders/json';
    	
        // Update extraParams
        this.proxy.extraParams = ep;

        // (Re)load store (load at page 1, otherwise entries may be hidden)
        this.loadPage(1);
    },

    syncWithOther: function(extraParams) {
        this.syncWithActivities(extraParams);
    },
    
    syncByOtherId: function(identifier) {

        // Update url
        this.proxy.url = '/stakeholders/byactivity/json/' + identifier;

        // Update extraParams
        this.proxy.extraParams = {};
    	
        // Reload store (load at page 1, otherwise entries may be hidden)
        this.loadPage(1);
    },

    /**
     * Try to find checkbox to show only pending stakeholders. 
     * If it exists and is checked, add parameter to proxy. If it does not exist
     * or it is unchecked, remove the parameter. 
     */
    getPendingCheckbox: function() {
        var checkbox;
        
        // Try to find checkbox
        var checkbox_q = Ext.ComponentQuery.query('lo_publicstakeholdertablepanel checkbox[itemId="pendingStakeholdersCheckbox"]');
        if (checkbox_q && checkbox_q.length > 0) {
            checkbox = checkbox_q[0];
        }
        
        if (checkbox && checkbox.isChecked()) {
            this.proxy.url = 'stakeholders';
            this.proxy.setExtraParam('moderator', true);
        } else {
            delete this.proxy.extraParams['moderator'];
            // Let function to sync with Activities handle all other
            // parameters
            this.syncWithActivities(this.proxy.extraParams);
        }
    }
});