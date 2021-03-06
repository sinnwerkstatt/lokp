Ext.define('Lmkp.model.ActivityTree', {
    extend: 'Ext.data.Model',

    fields:[{
        name: 'id',
        type: 'string'
    },{
        name: 'Name',
        type: 'string'
    }],

    proxy: {
        type: 'ajax',
        url: '/activities/tree',
        reader: {
            root: 'children',
            type: 'json'
        }
    }

});