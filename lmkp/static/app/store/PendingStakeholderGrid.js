Ext.define('Lmkp.store.PendingStakeholderGrid', {
    extend: 'Ext.data.Store',
    
    requires: [
        'Lmkp.model.Stakeholder',
        'Lmkp.model.TagGroup',
        'Lmkp.model.Tag',
        'Lmkp.model.MainTag'
    ],
    
    model: 'Lmkp.model.Stakeholder',
    
    pageSize: 10,
    remoteSort: true,

    // initial sorting
    sortOnLoad: true,
    sorters: {
        property: 'timestamp',
        direction : 'DESC'
    },
    
    proxy: {
        type: 'ajax',
        url: '/stakeholders/pending/json',
        reader: {
            root: 'data',
            type: 'json',
            totalProperty: 'total'
        },
        startParam: 'offset',
        simpleSortMode: true,
        sortParam: 'order_by'
    }
});