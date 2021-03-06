Ext.define('Lmkp.model.Stakeholder', {
    extend: 'Ext.data.Model',

    idProperty: '_id',

    fields: [{
        name: 'id', // activity_identifier (UID)
        type: 'string'
    }, {
        name: 'version',
        type: 'int'
    }, {
        name: 'status',
        type: 'string'
    }, {
        name: 'status_id',
        type: 'int'
    }, {
        name: 'timestamp',
        type: 'string'
    }, {
        name: 'missing_keys',
        type: 'array'
    }, {
    	name: 'user',
        type: 'Lmkp.model.User'
    }, {
    	name: 'previous_version',
    	type: 'int'
    }, {
        name: 'pending_count',
        type: 'int'
    }],

    hasMany: [{
        model: 'Lmkp.model.TagGroup',
        name: 'taggroups'
    }, {
        model: 'Lmkp.model.Involvement',
        name: 'involvements'
    }],

    getTagValues: function(tag) {

        var values = [];

        var taggroupStore = this.taggroups();
        for (var i = 0; i < taggroupStore.count(); i++) {
            var tagStore = taggroupStore.getAt(i).tags();
            for (var j=0; j < tagStore.count(); j++) {
                if (tagStore.getAt(j).get('key') == tag) {
                    values.push(tagStore.getAt(j).get('value'));
                }
            }
        }
        return values;
    },

    isEmpty: function() {
        var empty = true;
        var taggroupStore = this.taggroups();
        taggroupStore.each(function(taggroup) {
            if (empty && taggroup.get('id') != 0) {
                empty = empty && false;
            } else {
                empty = empty && true;
            }
        });
        return empty;
    }
});