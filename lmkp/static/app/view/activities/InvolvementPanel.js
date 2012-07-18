Ext.define('Lmkp.view.activities.InvolvementPanel', {
    extend: 'Ext.form.Panel',
    alias: ['widget.lo_involvementpanel'],

    bodyPadding: 5,
    layout: 'anchor',
    defaults: {
        anchor: '100%',
        margin: 0
    },
    defaultType: 'displayfield',
    title: 'Involvement',

    initComponent: function() {

        if (this.involvement_type && this.involvement) {

            this.items = []

            // For full involvements, ID is empty
            if (this.involvement.get('id')) {
                this.items.push({
                    fieldLabel: 'ID',
                    value: this.involvement.get('id')
                });
            }

            this.items.push({
                fieldLabel: 'Role',
                value: this.involvement.get('role')
            });

            // If 'data' in raw, show full involvement
            if (this.involvement.raw.data) {

                // Activity or Stakeholder?
                var model = null;
                var xtype = null;
                if (this.involvement_type == 'activity') {
                    model = 'Lmkp.model.Activity';
                    xtype = 'lo_activitypanel';
                } else if (this.involvement_type == 'stakeholder') {
                    model = 'Lmkp.model.Stakeholder';
                    xtype = 'lo_stakeholderpanel';
                }

                // Simulate a Store to create a Model instance which allows to
                // access its TagGroups and Tags
                var store = Ext.create('Ext.data.Store', {
                    model: model,
                    data: this.involvement.raw.data,
                    proxy: {
                        type: 'memory',
                        reader: {
                            type: 'json'
                        }
                    }
                });
                store.load();
                var invItem = store.getAt(0);

                if (invItem) {
                    this.items.push({
                        xtype: xtype,
                        contentItem: invItem,
                        border: 0
                    });
                }
            }

        } else {
            this.items = {
                xtype: 'panel',
                html: Lmkp.ts.msg('unknown')
            }
        }

        // Call parent first
        this.callParent(arguments);
    }
});