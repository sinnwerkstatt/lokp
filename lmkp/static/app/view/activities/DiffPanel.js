/*
 * As far as I know, this panel is not used anymore. However, it (or parts of
 * it) could be used again so I am not going to delete it yet.
 * However, its translations are deleted. So if reactivating this panel, make
 * sure to add the translations again (Lmkp.ts.msg('xxx')).
 */

Ext.define('Lmkp.view.activities.DiffPanel', {
    extend: 'Ext.form.Panel',
    alias: ['widget.lo_diffpanel'],

    // General settings
    layout: 'anchor',
    defaults: {
        anchor: '100%',
        margin: 0,
        border: 0
    },
    border: 1,
    bodyPadding: 5,

    title: Lmkp.ts.msg('review-diff_title'),

    initComponent: function() {

        this.items = []


        if (this.diff && this.contentItem) {

            // Involvement is Activity or Stakeholder?
            var involvement_type = null;
            if (this.contentItem == 'activities') {
                involvement_type = 'stakeholder';
            } else if (this.contentItem == 'stakeholders') {
                involvement_type = 'activity';
            }

            // New attributes
            if (this.diff.new_attr) {
                var me = this;
                var tgStore = Ext.create('Ext.data.Store', {
                    model: 'Lmkp.model.TagGroup',
                    data: this.diff.new_attr,
                    proxy: {
                        type: 'memory',
                        reader: {
                            type: 'json'
                        }
                    }
                });
                tgStore.load();
                tgStore.each(function(record) {
                    me.items.push({
                        xtype: 'fieldset',
                        collapsible: true,
                        collapsed: true,
                        border: 1,
                        title: '<span class="new">' +
                            Lmkp.ts.msg('review-diff_attr_added') + '</span>',
                        items: [
                            {
                                xtype: 'lo_taggrouppanel',
                                taggroup: record,
                                border: 0
                            }
                        ]
                    });
                });
            }
            // New involvements
            if (this.diff.new_inv) {
                for (var j in this.diff.new_inv) {
                    this.items.push({
                        xtype: 'fieldset',
                        collapsible: true,
                        collapsed: true,
                        border: 1,
                        title: '<span class="new">' +
                            Lmkp.ts.msg('review-diff_inv_added') + '</span>',
                        items: [
                            {
                                xtype: 'lo_involvementpanel',
                                involvement: this.diff.new_inv[j],
                                involvement_type: involvement_type,
                                title: null,
                                border: 0,
                                bodyPadding: 0
                            }
                        ]
                    });
                }
            }
            // Deleted attributes
            if (this.diff.old_attr) {
                var me = this;
                var tgStore = Ext.create('Ext.data.Store', {
                    model: 'Lmkp.model.TagGroup',
                    data: this.diff.old_attr,
                    proxy: {
                        type: 'memory',
                        reader: {
                            type: 'json'
                        }
                    }
                });
                tgStore.load();
                tgStore.each(function(record) {
                    me.items.push({
                        xtype: 'fieldset',
                        collapsible: true,
                        collapsed: true,
                        border: 1,
                        title: '<span class="deleted">' +
                            Lmkp.ts.msg('review-diff_attr_deleted') + '</span>',
                        items: [
                            {
                                xtype: 'lo_taggrouppanel',
                                taggroup: record,
                                border: 0
                            }
                        ]
                    });
                });
            }
            // Deleted involvements
            if (this.diff.old_inv) {
                for (var l in this.diff.old_inv) {
                    this.items.push({
                        xtype: 'fieldset',
                        collapsible: true,
                        collapsed: true,
                        border: 1,
                        title: '<span class="deleted">' +
                            Lmkp.ts.msg('review-diff_inv_deleted') + '</span>',
                        items: [
                            {
                                xtype: 'lo_involvementpanel',
                                involvement: this.diff.old_inv[l],
                                involvement_type: involvement_type,
                                title: null,
                                border: 0,
                                bodyPadding: 0
                            }
                        ]
                    });
                }
            }
        }
        this.callParent(arguments);
    }

});