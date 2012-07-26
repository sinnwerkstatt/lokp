Ext.define('Lmkp.view.editor.Detail', {
    extend: 'Ext.tab.Panel',
    alias: ['widget.lo_editordetailpanel'],

    requires: [
        'Lmkp.view.comments.CommentPanel',
        'Lmkp.view.activities.ActivityPanel',
        'Lmkp.view.items.PendingUserChanges'
    ],

    config: {
        // The currently shown activity in this panel or null if no activity
        // is shown
        current: {},
        // The OpenLayers GeoJSON format
        geojson: {}
    },

    geojson: new OpenLayers.Format.GeoJSON(),
	
    plain: true,
    activeTab: 0,
    defaults: {
        autoScroll: true
    },

    items: [{
        title: 'Details',
        xtype: 'lo_activitydetailtab'
    }, {
        title: 'History',
        xtype: 'lo_activityhistorypanel'
    }, {
        title: 'Add new Activity',
        xtype: 'lo_newactivitypanel'
    }],

    initComponent: function() {
        this.callParent(arguments);
    },

    populateDetailsTab: function(panel, data) {

        if (data) {

            // Set the current selection to current
            this.current = data;

            // Remove all existing panels
            panel.removeAll();

            // Add the panel for the current activity
            panel.add({
                xtype: 'lo_activitypanel',
                contentItem: data,
                border: 0,
                bodyPadding: 0
            });

            // Add a panel for pending versions of current user
            if (data.raw.pending) {
                panel.add({
                    xtype: 'lo_itemspendinguserchanges',
                    detailData: data.raw.pending,
                    itemModel: data.modelName,
                    detailsOnStart: false,
                    bodyCls: 'notice'
                });
            }

            // Add commenting panel
            panel.add({
                xtype: 'lo_commentpanel',
                identifier: data.get('id'),
                comment_object: 'activity'
            });

            // Show the feature on the map
            // Actually this does not belong here ...
            var mappanel = Ext.ComponentQuery.query('lo_editormappanel')[0];
            var vectorLayer = mappanel.getVectorLayer();
            vectorLayer.removeAllFeatures();
            var features = this.getFeatures(data);
            if (features) {
                vectorLayer.addFeatures(features);
            }
            vectorLayer.events.remove('featureunselected');
            vectorLayer.events.register('featureunselected',
                this,
                function(event){
                    Ext.MessageBox.confirm("Save changes?",
                        "Do you want to save the changes?",
                        function(buttonid){
                            // In case of yes, save the feature
                            if(buttonid == 'yes'){
                                // do something
                                this.saveGeometry(data, event.feature.geometry);
                            }
                            // If no is selected, reset the features
                            else if(buttonid == 'no'){
                                vectorLayer.removeAllFeatures();
                                vectorLayer.addFeatures(this.getFeatures(data));
                            }
                        }, this);
                });
        }
    },

    getFeatures: function(data){
        var geom = data.get('geometry');
        var vectors = this.geojson.read(Ext.encode(geom));
        if (vectors) {
            for(var j = 0; j < vectors.length; j++){
                vectors[j].geometry.transform(new OpenLayers.Projection("EPSG:4326"), new OpenLayers.Projection("EPSG:900913"));
            }
            return vectors

        }
    },

    /**
     * Add a new geometry to an existing activity.
     */
    saveGeometry: function(data, newGeometry){
        // Create the geojson object
        var geom = Ext.decode(
            this.geojson.write(
                // Project the point back to geographic coordinates
                newGeometry.transform(new OpenLayers.Projection("EPSG:900913"),
                    new OpenLayers.Projection("EPSG:4326"))
                )
            );

        // Create the diff object
        var activities = [];
        var activity = new Object();
        activity.id = data.get('id');
        activity.geometry = geom;
        activity.taggroups = [];
        activity.version = data.get('version');

        activities.push(activity);

        // Send JSON through AJAX request
        Ext.Ajax.request({
            url: '/activities',
            method: 'POST',
            headers: {
                'Content-Type': 'application/json;charset=utf-8'
            },
            jsonData: {
                'activities': activities
            },
            success: function() {
                Ext.Msg.alert('Success', 'The activity was successfully updated. It will be reviewed shortly.');
            },
            failure: function() {
                Ext.Msg.alert('Failure', 'The activity could not be created.');
            }
        });

    },

    populateHistoryTab: function(panel, uid) {
        if (uid) {
            Ext.Ajax.request({
                url: '/activities/history/' + uid,
                success: function(response, opts) {

                    // remove initial text if still there
                    if (panel.down('panel[name=history_initial]')) {
                        panel.remove(panel.down('panel[name=history_initial]'));
                    }

                    // remove old panels
                    if (panel.down('panel[name=history_active]')) {
                        panel.remove(panel.down('panel[name=history_active]'));
                    }
                    if (panel.down('panel[name=history_deleted]')) {
                        panel.remove(panel.down('panel[name=history_deleted]'));
                    }
                    while (panel.down('panel[name=history_overwritten]')) {
                        panel.remove(panel.down('panel[name=history_overwritten]'));
                    }

                    // get data
                    var json = Ext.JSON.decode(response.responseText);
                    // prepare template
                    var tpl = new Ext.XTemplate(
                        '<tpl for="attrs">',
                        '<span class="{cls}"><b>{k}</b>: {v}<br/></span>',
                        '</tpl>',
                        '<p>&nbsp;</p>',
                        '<tpl if="deleted != null">',
                        'Deleted: <span class="deleted"><b>{deleted}</b></span>',
                        '<p>&nbsp;</p>',
                        '</tpl>',
                        '<p class="version_info">Version {version} created on {timestamp}.<br/>',
                        'Data provided by <a href="#" onclick="Ext.create(\'Lmkp.view.users.UserWindow\', { username: \'{username}\' }).show();">{username}</a> [userid: {userid}].<br/>',
                        'Additional source of information: {source}</p>'
                        );

                    // add panel for current version if there is one
                    if (json.data.active) {
                        // prepare data
                        var o = json.data.active;
                        var ts = Ext.Date.format(Ext.Date.parse(o.timestamp, "Y-m-d H:i:s.u"), "Y/m/d H:i");
                        var changes = Ext.JSON.decode(o.changes);

                        // first, add general data about activity and changeset
                        var data = {
                            username: o.username,
                            userid: o.userid,
                            source: o.source,
                            timestamp: ts,
                            version: o.version,
                            id: o.id,
                            activity_identifier: o.activity_identifier
                        }
                        // add all remaining data: the key/value pairs
                        attrs = []
                        for (attr in o) {
                            // do not add general data (again) and do not add 'changes'
                            if (!data[attr] && attr != 'changes') {
                                // default class
                                var cls = 'unchanged';
                                // check for changes and update class accordingly
                                if (changes[attr]) {
                                    cls = changes[attr];
                                }
                                attrs.push({
                                    k: attr,
                                    v: o[attr],
                                    cls: cls
                                });
                            }
                        }
                        data["attrs"] = attrs;
                        // check for deleted attributes
                        var deleted = []
                        for (var i in changes) {
                            if (changes[i] == 'deleted') {
                                deleted.push(i);
                            }
                        }
                        data["deleted"] = (deleted.length > 0) ? deleted.join(", ") : null;

                        // create panel
                        var activePanel = Ext.create('Ext.panel.Panel', {
                            name: 'history_active',
                            title: '[Current] Version ' + o.version + ' (' + ts + ')',
                            collapsible: true,
                            collapsed: true
                        });
                        // add panel and apply template
                        panel.add(activePanel);
                        tpl.overwrite(activePanel.body, data);
                    }

                    // add panel for deleted version if there is one
                    if (json.data.deleted) {
                        // prepare data
                        var o = json.data.deleted;
                        var ts = Ext.Date.format(Ext.Date.parse(o.timestamp, "Y-m-d H:i:s.u"), "Y/m/d H:i");

                        // first, add general data about activity and changeset
                        var data = {
                            username: o.username,
                            userid: o.userid,
                            source: o.source,
                            timestamp: ts,
                            version: o.version,
                            id: o.id,
                            activity_identifier: o.activity_identifier
                        }

                        // special template
                        var deletedTpl = new Ext.XTemplate(
                            '<span class="deleted"><b>Deleted</b></span>',
                            '<p>&nbsp;</p>',
                            '<p class="version_info">This activity was deleted on {timestamp} by <a href="#" onclick="Ext.create(\'Lmkp.view.users.UserWindow\', { username: \'{username}\' }).show();">{username}</a> [userid: {userid}].<br/>',
                            'Additional source of information: {source}</p>'
                            );

                        // create panel
                        var deletedPanel = Ext.create('Ext.panel.Panel', {
                            name: 'history_deleted',
                            title: '[Deleted] (' + ts + ')',
                            collapsible: true,
                            collapsed: true
                        });

                        // add panel and apply template
                        panel.add(deletedPanel);
                        deletedTpl.overwrite(deletedPanel.body, data);
                    }

                    // add panels for old versions if there are any
                    if (json.data.overwritten.length > 0) {
                        for (var i in json.data.overwritten) {
                            // prepare data
                            var o = json.data.overwritten[i];
                            var ts = Ext.Date.format(Ext.Date.parse(o.timestamp, "Y-m-d H:i:s.u"), "Y/m/d H:i");
                            var changes = Ext.JSON.decode(o.changes);
                            // first, add general data about activity and changeset
                            var data = {
                                username: o.username,
                                userid: o.userid,
                                source: o.source,
                                timestamp: ts,
                                version: o.version,
                                id: o.id,
                                activity_identifier: o.activity_identifier
                            };
                            // add all remaining data: the key/value pairs
                            attrs = [];
                            for (attr in o) {
                                // do not add general data (again) and do not add 'changes'
                                if (!data[attr] && attr != 'changes') {
                                    // default class
                                    var cls = 'unchanged';
                                    // check for changes and update class accordingly
                                    if (changes[attr]) {
                                        cls = changes[attr];
                                    }
                                    attrs.push({
                                        k: attr,
                                        v: o[attr],
                                        cls: cls
                                    });
                                }
                            }
                            data["attrs"] = attrs;
                            // check for deleted attributes
                            var deleted = []
                            for (var i in changes) {
                                if (changes[i] == 'deleted') {
                                    deleted.push(i);
                                }
                            }
                            data["deleted"] = (deleted.length > 0) ? deleted.join(", ") : null;
                            // create panel
                            var p = Ext.create('Ext.panel.Panel', {
                                name: 'history_overwritten',
                                title: 'Version ' + o.version + ' (' + ts + ')',
                                collapsible: true,
                                collapsed: true
                            });
                            panel.add(p);
                            tpl.overwrite(p.body, data);
                        }
                    }

                    // in case no active and no overwritten activities were found (this should never happen),
                    // show at least something.
                    // using the initial panel because this will be removed when selected the next activity
                    if (!json.data.active && !json.data.deleted && json.data.overwritten.length == 0) {
                        panel.add({
                            xtype: 'panel',
                            border: 0,
                            name: 'history_initial',
                            html: 'No history found for this activity',
                            collapsible: false,
                            collapsed: false
                        });
                    }

                    // layout does not seem to work if panel is expanded on start, therefore this is done
                    // after everything was added.
                    // TODO: find out why ...
                    if (activePanel) {
                        activePanel.toggleCollapse();
                    }
                    if (deletedPanel) {
                        deletedPanel.toggleCollapse();
                    }
                }
            });
        }
    }

});
