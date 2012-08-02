Ext.define('Lmkp.view.activities.NewActivity', {
    extend: 'Lmkp.view.NewItem',

    alias: ['widget.lo_newactivitypanel'],

    requires: [
    'Lmkp.view.stakeholders.StakeholderFieldContainer',
    'Lmkp.view.activities.NewTaggroupPanel'
    ],
	
    title: 'Add new Activity',

    config: {
        activityGeometry: null
    },
	
    layout: 'fit',
    defaults: {
        border: 0
    },
    width: 400,

    initComponent: function() {
		
        // prepare the form
        var form = Ext.create('Ext.form.Panel', {
            autoScroll: true,
            border: 0,
            bodyPadding: 5,
            layout: 'anchor',
            defaults: {
                anchor: '100%'
            },
            tbar: ['->',{
                disabled: true,
                formBind: true,
                iconCls: 'save-button',
                itemId: 'submitButton',
                scale: 'medium',
                scope: this,
                text: 'Submit'
            }]
        });

        this.items = form;

        this.callParent(arguments);
    },

    showForm: function(mandatoryStore, completeStore) {

        var form = this.down('form');

        // Delete all existing items
        form.removeAll();

        // Collect all records of completeStore
        var all_records = [];
        completeStore.each(function(r){
            all_records.push(r.copy());
        });

        // Add a fieldset for each mandatory Key
        mandatoryStore.each(function(record) {
            // All keys should be available for each fieldset -> 'copy' store
            var main_store = Ext.create('Lmkp.store.ActivityConfig');
            main_store.add(all_records);

            form.add({
                xtype: 'fieldset',
                border: 0,
                bodyPadding: 0,
                padding: 0,
                margin: 0,
                items: [
                    {
                        xtype: 'lo_newtaggrouppanel',
                        is_maintag: true,
                        removable: true,
                        main_store: main_store,
                        complete_store: completeStore,
                        initial_key: record.get('name')
                    }
                ]
            });
        });

        // After adding all mandatory fields, add the associated stakeholder
        // fieldset
        form.add({
            border: 1,
            itemId: 'selectStakeholderFieldSet',
            items: [
            {
                itemId: 'selectStakeholderButton',
                text: 'Add Stakeholder',
                xtype: 'button'
            }],
            title: 'Associated Stakeholders',
            xtype: 'fieldset'
        });
    }
});
