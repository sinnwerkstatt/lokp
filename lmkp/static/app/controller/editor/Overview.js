//Ext.define('Lmkp.controller.editor.Overview', {
//    extend: 'Ext.app.Controller',
//
//    refs: [{
//        ref: 'mapPanel',
//        selector: 'lo_editormappanel'
//    }, {
//        ref: 'detailPanel',
//        selector: 'lo_editordetailpanel'
//    },{
//        ref: 'newActivityPanel',
//        selector: 'lo_newactivitypanel'
//    },{
//        ref: 'selectStakeholderFieldSet',
//        selector: 'lo_newactivitypanel fieldset[itemId="selectStakeholderFieldSet"]'
//    }],
//
//    requires: [
//    'Lmkp.model.Activity',
//    'Lmkp.model.TagGroup',
//    'Lmkp.model.Tag',
//    'Lmkp.model.MainTag',
//    'Lmkp.model.Point'
//    ],
//
//    stores: [
//    'ActivityGrid',
//    'ActivityConfig',
//    'StakeholderGrid',
//    'StakeholderConfig',
//    'Profiles'
//    ],
//
//    views: [
//    'editor.Detail',
//    'editor.Map',
//    'activities.Details',
//    'activities.History',
//    'activities.Filter',
//    'stakeholders.StakeholderSelection',
//    'items.FilterPanel'
//    ],
//
//    init: function() {
//        // Get the config stores and load them
//        this.getActivityConfigStore().load();
//        this.getStakeholderConfigStore().load();
//
//        console.log("blablablabal");
//
//        this.control({
//            'lo_editortablepanel': {
//            //render: this.onTablePanelRender
//            },
//            // Events concerning the NewActivity panel
//            'lo_newactivitypanel': {
//                render: this.onNewActivityPanelRender
//            },
//            'lo_newactivitypanel button[itemId="submitButton"]': {
//                click: this.onSubmitButtonClick
//            },
//            // Events concerning the ActivityTable panel
//            'lo_editoractivitytablepanel': {
//                render: this.onActivityTablePanelRender
//            },
//            'lo_editorstakeholdertablepanel': {
//                render: this.onStakeholderTablePanelRender
//            },
//            'lo_editoractivitytablepanel checkbox[itemId="spatialFilterCheckbox"]': {
//                change: this.onSpatialFilterCheckboxChange
//            },
//            'button[name=addAttributeFilter]': {
//                click: this.addAttributeFilter
//            },
//            'lo_activityfilterpanel button[name=addTimeFilter]': {
//                click: this.addTimeFilter
//            },
//            'lo_editoractivitytablepanel tabpanel[id=detailPanel]': {
//                tabchange: this.showDetails
//            },
//            'lo_editoractivitytablepanel button[id=deleteAllFilters]': {
//                click: this.deleteAllFilters
//            },
//            'button[name=filterActivateButton]': {
//                click: this.applyFilter
//            },
//            'combobox[name=attributeCombo]': {
//                select: this.showValueFields
//            },
//            '[name=valueField]': {
//                change: this.resetActivateButton
//            },
//            'combobox[name=filterOperator]': {
//                select: this.resetActivateButton
//            },
//            'lo_editoractivitytablepanel datefield[name=dateField]': {
//                change: this.resetActivateButton
//            },
//            'button[name=deleteButton]': {
//                click: this.deleteFilter
//            },
//            'combobox[name=logicalOperator]': {
//                select: this.applyFilter
//            },
//            'gridpanel[itemId=activityGrid] gridcolumn[name=activityCountryColumn]': {
//                afterrender: this.renderActivityCountryColumn
//            },
//            'gridpanel[itemId=activityGrid] gridcolumn[name=yearofinvestmentcolumn]': {
//                afterrender: this.renderActivityYearColumn
//            },
//            'lo_editoractivitytablepanel gridpanel[itemId=activityGrid]': {
//                selectionchange: this.showDetails
//            },
//            'lo_editorstakeholdertablepanel gridpanel[itemId=stakeholderGrid]': {
//                selectionchange: this.showDetails
//            },
//            'gridpanel[itemId=stakeholderGrid] gridcolumn[name=stakeholdernamecolumn]': {
//                afterrender: this.renderStakeholderNameColumn
//            },
//            'gridpanel[itemId=stakeholderGrid] gridcolumn[name=stakeholdercountrycolumn]': {
//                afterrender: this.renderStakeholderCountryColumn
//            },
//            'checkbox[itemId=filterConnect]': {
//                change: this.onConnectFilterChange
//            },
//            'lo_itemspendinguserchanges panel[name=showDetails]': {
//                afterrender: this.onPendingUserChangesRender
//            },
//            'lo_itemspendinguserchanges panel[name=hideDetails]': {
//                afterrender: this.onPendingUserChangesRender
//            },
//            'lo_activitypanel panel[name=showDetails]': {
//                afterrender: this.onRenderHiddenOriginal
//            },
//            'lo_activitypanel panel[name=hideDetails]': {
//                afterrender: this.onRenderHiddenOriginal
//            },
//            'lo_stakeholderpanel panel[name=showDetails]': {
//                afterrender: this.onRenderHiddenOriginal
//            },
//            'lo_stakeholderpanel panel[name=hideDetails]': {
//                afterrender: this.onRenderHiddenOriginal
//            }
//        });
//    },
//
//    /**
//     * Adds a beforeload action to the ActivityGridStore to filter the activites
//     * according to the current map extent.
//     */
//    onActivityTablePanelRender: function(comp){
//
//        // Adds a beforeload action
//        this.getActivityGridStore().on('beforeload', function(store){
//
//            // Get the spatialFilterCheckbox
//            var checkbox = comp.getSpatialFilterCheckbox();
//            // Get the store proxy
//            var proxy = store.getProxy();
//            // Checkbox is checked:
//            if(checkbox.getValue()){
//                // Get the map view.
//                // Actually this is bad coding style! This should be done in a
//                // superior controller ...
//                var map = this.getMapPanel().getMap();
//                // Get the extent if the map is already initialized, else the
//                // map extent is still null
//                if(map.getExtent()){
//                    // Set the bounding box as extra parameter
//                    proxy.setExtraParam("bbox", map.getExtent().toBBOX());
//                }
//            // Else checkbox is not checked:
//            } else {
//                // If the bounding box parameter is already set, reset it to
//                // null
//                if(proxy.extraParams.bbox){
//                    proxy.setExtraParam("bbox", null);
//                // Else cancel the reloading of the store and save a request
//                } else {
//                    return false;
//                }
//            }
//        }, this)
//    },
//
//    onStakeholderTablePanelRender: function() {
//        this.getStakeholderGridStore().load();
//    },
//
//    /**
//     * Reload the ActivityGrid store when the spatialFilterCheckbox is checked
//     * or unchecked
//     */
//    onSpatialFilterCheckboxChange: function(comp){
//        this.getActivityGridStore().load();
//    },
//
//    addAttributeFilter: function(button) {
//
//        // Activity or Stakeholder?
//        var panel_xtype = null;
//        var store = null;
//        if (button.item_type == 'activity') {
//            panel_xtype = 'lo_activityfilterpanel';
//            store = this.getActivityConfigStore();
//        } else if (button.item_type == 'stakeholder') {
//            panel_xtype = 'lo_stakeholderfilterpanel';
//            store = this.getStakeholderConfigStore();
//        }
//
//        var form = button.up(panel_xtype);
//
//        // always insert above the panel with the buttons
//        var insertIndex = form.items.length - 1;
//        var cbox = Ext.create('Ext.form.field.ComboBox', {
//            name: 'attributeCombo',
//            store: store,
//            valueField: 'name',
//            displayField: 'fieldLabel',
//            queryMode: 'local',
//            typeAhead: true,
//            forceSelection: true,
//            value: store.getAt('0'),
//            flex: 0,
//            margin: '0 5 5 0'
//        });
//        form.insert(insertIndex, {
//            xtype: 'lo_itemsfilterpanel',
//            name: 'attributePanel',
//            filterField: cbox
//        });
//        // show initial filter
//        this.showValueFields(cbox, [store.getAt('0')]);
//        // toggle logical operator
//        form.toggleLogicalOperator();
//    },
//
//    addTimeFilter: function(button) {
//
//        // Activity or Stakeholder?
//        var panel_xtype = null;
//        if (button.item_type == 'activity') {
//            panel_xtype = 'lo_activityfilterpanel';
//        } else if (button.item_type == 'stakeholder') {
//            panel_xtype = 'lo_stakeholderfilterpanel';
//        }
//
//        var form = button.up(panel_xtype);
//
//        // always insert above the panel with the buttons
//        var insertIndex = form.items.length - 1;
//        var picker = Ext.create('Ext.form.field.Date', {
//            name: 'dateField',
//            fieldLabel: Lmkp.ts.msg("gui_date"),
//            flex: 0,
//            margin: '0 5 5 0',
//            value: new Date() // defaults to today
//        });
//        form.insert(insertIndex, {
//            xtype: 'lo_itemsfilterpanel',
//            name: 'timePanel',
//            filterField: picker
//        });
//        // disable 'add' button
//        button.disable();
//    },
//
//    showValueFields: function(combobox, records, eOpts) {
//        // everything specific for current attributePanel
//        var attributePanel = combobox.up('panel');
//        // remove operator field if it is already there
//        var operatorFieldIndex = attributePanel.items.findIndex('name', 'filterOperator');
//        if (operatorFieldIndex != -1) {
//            attributePanel.items.getAt(operatorFieldIndex).destroy();
//        }
//        // remove value field if it is already there
//        var valueFieldIndex = attributePanel.items.findIndex('name', 'valueField');
//        if (valueFieldIndex != -1) {
//            attributePanel.items.getAt(valueFieldIndex).destroy();
//        }
//        var xtype = records[0].get('xtype');
//        // determine operator field values and insert it
//        var operatorCombobox = this.getOperator(xtype);
//        attributePanel.insert(1, operatorCombobox);
//        // determine type and categories of possible values of value field
//        var valueField = this.getValueField(records[0], xtype);
//        attributePanel.insert(2, valueField);
//        // reset ActivateButton
//        this.resetActivateButton(combobox);
//    },
//
//    renderActivityCountryColumn: function(comp) {
//        this._renderColumnMultipleValues(comp, 'activity_db-key-country');
//    },
//
//    renderActivityYearColumn: function(comp) {
//        this._renderColumnMultipleValues(comp, 'activity_db-key-yearofagreement');
//    },
//
//    renderStakeholderNameColumn: function(comp) {
//        this._renderColumnMultipleValues(comp, 'stakeholder_db-key-name');
//    },
//
//    renderStakeholderCountryColumn: function(comp) {
//        this._renderColumnMultipleValues(comp, 'stakeholder_db-key-country');
//    },
//
//    /**
//     * Shows the selected model in the details panel
//     */
//    showDetails: function(model, selected, eOpts) {
//
//        if (selected && selected.length > 0) {
//
//            // Activity or Stakeholder?
//            var url_prefix = '';
//            if (selected[0].modelName == 'Lmkp.model.Stakeholder') {
//                url_prefix = '/stakeholders/';
//            } else if (selected[0].modelName == 'Lmkp.model.Activity') {
//                url_prefix = '/activities/';
//            }
//
//            // Use a data store to get the full details on current item
//            var detailStore = Ext.create('Ext.data.Store', {
//                model: selected[0].modelName,
//                proxy: {
//                    type: 'ajax',
//                    url: url_prefix + selected[0].get('id'),
//                    reader: {
//                        root: 'data',
//                        type: 'json',
//                        totalProperty: 'total'
//                    },
//                    extraParams: {
//                        involvements: 'full',
//                        show_pending: true
//                    }
//                }
//            });
//            var me = this;
//            // Details can only be shown once store is loaded
//            detailStore.on('load', function(detailStore){
//                var detailPanel = this.getDetailPanel();
//                var d = detailPanel.down('lo_activitydetailwindow');
//                detailPanel.setActiveTab(d);
//                detailPanel.populateDetailsTab(d, detailStore.first());
//
//                // Show or hide toolbar buttons specific for Activities
//                var current = detailPanel.getCurrent();
//                var item_type = null;
//                if (current) {
//                    if (current.modelName == 'Lmkp.model.Activity') {
//                        item_type = 'activity';
//                    } else if (current.modelName == 'Lmkp.model.Stakeholder') {
//                        item_type = 'stakeholder';
//                    }
//                }
//                if (item_type && item_type == 'activity') {
//                    me.toggleActivityButtons(d, true);
//                } else if (item_type && item_type == 'stakeholder') {
//                    me.toggleActivityButtons(d, false);
//                }
//            }, this);
//            detailStore.load();
//        }
//    },
//
//    /**
//     * Show or hide toolbar buttons which are specific for Activities (eg. "Add
//     * involvements" or "Edit location")
//     */
//    toggleActivityButtons: function(detailsTab, toggle) {
//
//        var tbar = detailsTab.getDockedItems('toolbar[dock="top"]')[0];
//
//        if (tbar) {
//            if (toggle) {
//                // Show
//                if (tbar.query('button[itemId=add-involvement-button]').length == 0) {
//                    // Button to Add Involvements
//                    var addInvButton = {
//                        iconCls: 'add-involvement-button',
//                        itemId: 'add-involvement-button',
//                        scale: 'medium',
//                        text: 'Add involvement',
//                        tooltip: 'to be translated'
//                    };
//                    tbar.insert(1, addInvButton);
//                }
//                if (tbar.query('button[itemId=edit-location-button]').length == 0) {
//                    // Button to Edit Location
//                    var mappanel = this.getMapPanel();
//                    var selectCtrl = new OpenLayers.Control.SelectFeature(mappanel.getVectorLayer());
//                    var movePointCtrl = new OpenLayers.Control.ModifyFeature(mappanel.getVectorLayer(), {
//                        mode: OpenLayers.Control.ModifyFeature.DRAG,
//                        selectControl: selectCtrl
//                    });
//                    var moveAction = Ext.create('GeoExt.Action', {
//                        control: movePointCtrl,
//                        iconCls: 'move-button',
//                        itemId: 'edit-location-button',
//                        map: mappanel.getMap(),
//                        scale: 'medium',
//                        text: 'Edit location',
//                        toggleGroup: 'map-controls',
//                        toggleHandler: function(button, state){
//                            if(state){
//                                // Activate the DrawFeature control and select the activity
//                                // on the map
//                                var f = mappanel.getVectorLayer().features[0];
//                                selectCtrl.select(f);
//                                movePointCtrl.activate();
//                                movePointCtrl.selectFeature(f);
//                                // Get the parent tabpanel
//                                var tp = mappanel.up('tabpanel');
//                                // Set the mappanel active
//                                tp.setActiveTab(mappanel);
//                            } else {
//                                movePointCtrl.deactivate();
//                            }
//                        }
//                    });
//                    var moveButton = Ext.create('Ext.button.Button', moveAction);
//                    tbar.insert(1, moveButton);
//                }
//            } else {
//                // Hide
//                if (tbar.query('button[itemId=add-involvement-button]').length == 1) {
//                    tbar.remove(tbar.query('button[itemId=add-involvement-button]')[0]);
//                }
//                if (tbar.query('button[itemId=edit-location-button]').length == 1) {
//                    tbar.remove(tbar.query('button[itemId=edit-location-button]')[0]);
//                }
//            }
//        }
//    },
//
//    resetActivateButton: function(element) {
//        var attributePanel = element.up('panel');
//        var applyFilter = false;
//        // try to find attribute button
//        var attrButtonIndex = attributePanel.items.findIndex('name', 'filterActivateButton');
//        if (attrButtonIndex != -1) {
//            var btn = attributePanel.items.getAt(attrButtonIndex);
//            if (btn.pressed) {
//                applyFilter = true;
//            }
//            attributePanel.items.getAt(attrButtonIndex).toggle(false);
//        }
//        if (applyFilter) {
//            this.applyFilter(element);
//        }
//    },
//
//    /**
//     * When using the checkbox to combine filters from Activities and
//     * Stakeholders, look for the filterpanel to provide it to 'applyFilter()'
//     */
//    onConnectFilterChange: function(checkbox) {
//        var gridpanel = checkbox.up('panel');
//        var tablepanel = gridpanel.up('panel');
//        var filterpanel = tablepanel.down('panel');
//        this.applyFilter(filterpanel);
//    },
//
//    /**
//     * If input is not a button, it is assumed that it is a filterpanel.
//     */
//    applyFilter: function(input) {
//
//        if (input.getXType() == 'button' || input.getXType() == 'combobox') {
//            // use button to find if new filter request came from Activities or
//            // Stakeholders
//            var itempanel = input.up('panel');
//            var filterpanel = itempanel.up('panel') ? itempanel.up('panel') : null;
//        } else {
//            var filterpanel = input;
//        }
//
//        var store = null;
//        var url = '';
//        var logical_operator = null;
//
//        if (filterpanel) {
//            // Fill needed values based on Activity or Stakeholder
//            var prefix = null;
//            var other_xtype = null;
//            var other_prefix = null;
//            var url_prefix = null;
//            var paging_id = null
//            if (filterpanel.getXType() == 'lo_activityfilterpanel') {
//                // Activities
//                url_prefix = 'activities?';
//                prefix = 'a';
//                other_xtype = 'lo_stakeholderfilterpanel';
//                other_prefix = 'sh';
//                store = this.getActivityGridStore();
//                paging_id = 'activityGridPagingToolbar';
//            }
//            else if (filterpanel.getXType() == 'lo_stakeholderfilterpanel') {
//                // Stakeholders
//                url_prefix = 'stakeholders?';
//                prefix = 'sh';
//                other_xtype = 'lo_activityfilterpanel';
//                other_prefix = 'a';
//                store = this.getStakeholderGridStore();
//                paging_id = 'stakeholderGridPagingToolbar';
//            }
//
//            // Add filters from current panel to url
//            var filters = filterpanel.getFilterItems();
//            url += this._getFilterUrl(filters, prefix);
//            if (filters.length > 1) {
//                logical_operator = filterpanel.getLogicalOperator();
//            }
//
//            // if checkbox is set, also add filters from other panel to url
//            var tablepanel = filterpanel.up('panel');
//            if (tablepanel) {
//                var combine_checkbox = tablepanel.query('checkbox[itemId=filterConnect]')[0];
//                if (combine_checkbox && combine_checkbox.checked) {
//                    var other_panel = Ext.ComponentQuery.query(other_xtype)[0];
//                    if (other_panel) {
//                        var other_filters = other_panel.getFilterItems();
//                        url += '&' + this._getFilterUrl(other_filters, other_prefix);
//                        if (other_filters.length > 1 && !logical_operator) {
//                            logical_operator = other_panel.getLogicalOperator();
//                        }
//                    }
//                }
//            }
//
//            // logical operator
//            if (logical_operator) {
//                url += '&logical_op=' + logical_operator;
//            }
//        }
//
//        // Set new url and reload store
//        url = url_prefix + url;
//        store.getProxy().url = url;
//        if (url == url_prefix) {
//            store.load();
//        }
//
//        // move paging to back to page 1 when filtering (otherwise may show
//        // empty page instead of results)
//        if (url != url_prefix) {
//            Ext.ComponentQuery.query('pagingtoolbar[id=' + paging_id + ']')[0].moveFirst();
//        }
//    },
//
//    toggleLogicalOperator: function(filterpanel, visible) {
//        var cb = filterpanel.query('combobox[name=logicalOperator]')[0];
//        if (cb) {
//            cb.setVisible(visible);
//        }
//    },
//
//    deleteFilter: function(button) {
//
//        var item_panel = button.up('panel');
//
//        if (item_panel) {
//            var filter_panel = item_panel.up('panel');
//        }
//
//        if (item_panel && filter_panel) {
//            // if time was filtered, re-enable its 'add' button
//            if (item_panel.name == 'timePanel') {
//                var btn = Ext.ComponentQuery.query('button[name=addTimeFilter]')[0];
//                if (btn) {
//                    btn.enable();
//                }
//            }
//            // reload store if removed filter was activated (deactivate it first)
//            if (item_panel.filterIsActivated()) {
//                item_panel.deactivateFilter();
//                this.applyFilter(button);
//            }
//            filter_panel.remove(item_panel);
//        }
//        // toggle logical operator
//        filter_panel.toggleLogicalOperator();
//    },
//
//    deleteAllFilters: function() {
//        console.log("refactor me and add a button somewhere");
//    //        var panels = Ext.ComponentQuery.query('panel[name=attributePanel]');
//    //        panels = panels.concat(Ext.ComponentQuery.query('panel[name=timePanel]'));
//    //        if (panels.length > 0) {
//    //            form = Ext.ComponentQuery.query('panel[id=activityFilterForm]')[0];
//    //            for (i=0; i<panels.length; i++) {
//    //                // if time was filtered, re-enable its 'add' button
//    //                if (panels[i].name == 'timePanel') {
//    //                    var button = Ext.ComponentQuery.query('button[name=addTimeFilter]')[0];
//    //                    if (button) {
//    //                        button.enable();
//    //                    }
//    //                }
//    //                if (form.items.contains(panels[i])) {
//    //                    form.remove(panels[i], true);
//    //                    panels[i].destroy();
//    //                }
//    //            }
//    //            // collapse form if expanded
//    //            if (!form.collapsed) {
//    //                form.toggleCollapse();
//    //            }
//    //        }
//    //        this.applyFilter();
//    },
//
//    getOperator: function(xType) {
//        // prepare values of the store depending on selected xType
//        switch (xType) {
//            case "combobox": // possibilities: like | nlike
//                var data = [
//                {
//                    'queryOperator': '__like=',
//                    'displayOperator': Lmkp.ts.msg('filter_operator-is')
//                }, {
//                    'queryOperator': '__nlike=',
//                    'displayOperator': Lmkp.ts.msg('filter_operator-is-not')
//                }
//                ];
//                break;
//            case "textfield": // possibilities: like | ilike | nlike | nilike
//                var data = [
//                {
//                    'queryOperator': '__like=',
//                    'displayOperator':
//                    Lmkp.ts.msg('filter_operator-contains-case-sensitive')
//                }, {
//                    'queryOperator': '__ilike=',
//                    'displayOperator':
//                    Lmkp.ts.msg('filter_operator-contains-case-insensitive')
//                }, {
//                    'queryOperator': '__nlike=',
//                    'displayOperator':
//                    Lmkp.ts.msg('filter_operator-contains-not-case-sensitive')
//                }, {
//                    'queryOperator': '__nilike=',
//                    'displayOperator':
//                    Lmkp.ts.msg('filter_operator-contains-not-case-insensitive')
//                }
//                ];
//                break;
//            default: // default is also used for numberfield
//                var data = [
//                {
//                    'queryOperator': '__eq=',
//                    'displayOperator': Lmkp.ts.msg('filter_operator-equals')
//                }, {
//                    'queryOperator': '__lt=',
//                    'displayOperator': Lmkp.ts.msg('filter_operator-less-than')
//                }, {
//                    'queryOperator': '__lte=',
//                    'displayOperator': Lmkp.ts.msg('filter_operator-less-than-or-equal')
//                }, {
//                    'queryOperator': '__gte=',
//                    'displayOperator': Lmkp.ts.msg('filter_operator-greater-than-or-equal')
//                }, {
//                    'queryOperator': '__gt=',
//                    'displayOperator': Lmkp.ts.msg('filter_operator-greater-than')
//                }, {
//                    'queryOperator': '__ne=',
//                    'displayOperator': Lmkp.ts.msg('filter_operator-not-equals')
//                }
//                ];
//                break;
//        }
//        // populate the store
//        var store = Ext.create('Ext.data.Store', {
//            fields: ['queryOperator', 'displayOperator'],
//            data: data
//        });
//        // configure the checkbox
//        var cb = Ext.create('Ext.form.field.ComboBox', {
//            name: 'filterOperator',
//            store: store,
//            displayField: 'displayOperator',
//            valueField: 'queryOperator',
//            queryMode: 'local',
//            editable: false,
//            width: 50,
//            margin: '0 5 0 0'
//        });
//        // default value: the first item of the store
//        cb.setValue(store.getAt('0').get('queryOperator'));
//        return cb;
//    },
//
//    getValueField: function(record, xtype) {
//        var fieldName = 'valueField';
//        // try to find categories
//        var selectionValues = record.get('store');
//        if (selectionValues) {      // categories of possible values available, create ComboBox
//            var valueField = Ext.create('Ext.form.field.ComboBox', {
//                name: fieldName,
//                store: selectionValues,
//                queryMode: 'local',
//                editable: true,
//                forceSelection: true,
//                value: selectionValues[0][0],
//                margin: '0 5 0 0'
//            });
//        } else {                    // no categories available, create field based on xtype
//            switch (xtype) {
//                case "numberfield":
//                    var valueField = Ext.create('Ext.form.field.Number', {
//                        name: fieldName,
//                        emptyText: Lmkp.ts.msg('filter_specify-number-value'),
//                        margin: '0 5 0 0'
//                    });
//                    break;
//                default:
//                    var valueField = Ext.create('Ext.form.field.Text', {
//                        name: fieldName,
//                        emptyText: Lmkp.ts.msg('filter_specify-text-value'),
//                        margin: '0 5 0 0'
//                    });
//                    break;
//            }
//        }
//        return valueField;
//    },
//
//    _isInArray: function(arr, obj) { // http://stackoverflow.com/questions/143847/best-way-to-find-an-item-in-a-javascript-array
//        for(var i=0; i<arr.length; i++) {
//            if (arr[i] == obj) return true;
//        }
//    },
//
//    _formatEmptyNumberValue: function(emptyNumber) {
//        /**
//         * The default NULL-value for unspecified number values is 0.
//         * Assumption: 0 as a number value (currently for Area and Year of Investment)
//         * is not useful and should rather not be displayed.
//         */
//        return (emptyNumber == 0) ? '' : emptyNumber;
//    },
//
//    _renderColumnMultipleValues: function(comp, dataIndex) {
//        /**
//         * Helper function to find values inside Tags and TagGroups.
//         */
//        comp.renderer = function(value, p, record) {
//            // loop through all tags is needed
//            var taggroupStore = record.taggroups();
//            var ret = [];
//            for (var i=0; i<taggroupStore.count(); i++) {
//                var tagStore = taggroupStore.getAt(i).tags();
//                for (var j=0; j<tagStore.count(); j++) {
//                    if (tagStore.getAt(j).get('key') == Lmkp.ts.msg(dataIndex)) {
//                        ret.push(Ext.String.format('{0}', tagStore.getAt(j).get('value')));
//                    }
//                }
//            }
//            if (ret.length > 0) {
//                return ret.join(', ');
//            } else {
//                return Lmkp.ts.msg('gui_unknown');
//            }
//        }
//    },
//
//    onGetFeatureInfo: function(event){
//        var gml = new OpenLayers.Format.GML();
//        // Get the first vector
//        var vector = gml.read(event.text)[0];
//        if(!vector){
//            return;
//        }
//        var identifier = vector.data.activity_identifier;
//        Ext.Ajax.request({
//            url: '/activities/' + identifier,
//            scope: this,
//            success: function(response){
//                var responseObj = Ext.decode(response.responseText);
//
//                // Create a temporary memory store to properly
//                // read the server response
//                var store = Ext.create('Ext.data.Store', {
//                    autoLoad: true,
//                    model: 'Lmkp.model.Activity',
//                    data : responseObj,
//                    proxy: {
//                        type: 'memory',
//                        reader: {
//                            root: 'data',
//                            type: 'json',
//                            totalProperty: 'total'
//                        }
//                    }
//                });
//
//                this.showDetails(null, [store.getAt(0)], null);
//            }
//        });
//    },
//
//    _getFilterUrl: function(filters, prefix) {
//        if (filters && prefix) {
//            // Collect values
//            var queryable = [];
//            var queries = [];
//            for (var i in filters) {
//                if (filters[i] && filters[i].attr) {
//                    // attribute
//                    // only add attribute to queryable if not already there
//                    if (!this._isInArray(queryable, filters[i].attr)) {
//                        queryable.push(filters[i].attr);
//                    }
//                    queries.push(prefix + '__' + filters[i].attr + filters[i].op + filters[i].value)
//                } else if (filters[i] && filters[i].date) {
//                    // date
//                    queries.push('timestamp=' + filters[i].date);
//                }
//            }
//
//            // Put together the url
//            var url = '';
//            if (queryable.length > 0 && queries.length > 0) {
//                // queryable
//                url += prefix + '__queryable=' + queryable.join(',') + '&';
//                // queries
//                url += queries.join('&');
//            }
//            return url;
//        }
//    },
//
//    onNewActivityPanelRender: function(comp, eOpts){
//
//        // Get the map from the map panel
//        var mappanel = this.getMapPanel();
//        var map = mappanel.getMap();
//
//        // Get the toolbar
//        var tbar = comp.down('form').getDockedItems('toolbar[dock="top"]')[0];
//
//        var selectCtrl = new OpenLayers.Control.SelectFeature(mappanel.getVectorLayer());
//
//        // Add the control and button to move an activity
//        var movePointCtrl = new OpenLayers.Control.ModifyFeature(
//            mappanel.getVectorLayer(), {
//                mode: OpenLayers.Control.ModifyFeature.DRAG,
//                selectControl: selectCtrl
//            });
//        map.addControl(movePointCtrl);
//        mappanel.getVectorLayer().events.register('featuremodified', comp, function(event){
//            var g = event.feature.geometry;
//            this.setNewGeometryGeometry(g);
//        });
//
//        var moveAction = Ext.create('GeoExt.Action', {
//            control: movePointCtrl,
//            iconCls: 'move-button',
//            map: map,
//            scale: 'medium',
//            text: 'Edit location',
//            toggleGroup: 'map-controls',
//            toggleHandler: function(button, state){
//                if(state){
//                    // Activate the DrawFeature control
//                    movePointCtrl.activate();
//                    // Get the parent tabpanel
//                    var tp = mappanel.up('tabpanel');
//                    // Set the mappanel active
//                    tp.setActiveTab(mappanel);
//                } else {
//                    movePointCtrl.deactivate();
//                }
//            }
//        });
//        var moveButton = Ext.create('Ext.button.Button', moveAction);
//        tbar.insert(0, moveButton);
//
//        // Add the control and button to create a new activity
//        var createPointCtrl = new OpenLayers.Control.DrawFeature(
//            mappanel.getVectorLayer(),
//            OpenLayers.Handler.Point,{
//                eventListeners: {
//                    'featureadded': function(event){
//                        var g = event.feature.geometry;
//                        //selectCtrl.select(event.feature);
//                        createPointCtrl.deactivate();
//                        selectCtrl.select(event.feature);
//                        movePointCtrl.activate();
//                        movePointCtrl.selectFeature(event.feature);
//                        createButton.toggle(false);
//                        moveButton.toggle(true);
//                        this.setNewFeatureGeometry(g);
//                    //
//                    },
//                    scope: comp
//                }
//            });
//        map.addControl(createPointCtrl);
//        mappanel.getVectorLayer().events.register('beforefeatureadded', mappanel.getVectorLayer(), function(event){
//            this.removeAllFeatures();
//        });
//
//        var createAction = Ext.create('GeoExt.Action',{
//            control: createPointCtrl,
//            iconCls: 'create-button',
//            scale: 'medium',
//            text: 'Add Location',
//            toggleGroup: 'map-controls',
//            toggleHandler: function(button, state){
//                // If button is pressed, state is true
//                if(state){
//                    // Activate the DrawFeature control
//                    createPointCtrl.activate();
//                    // Get the parent tabpanel
//                    var tp = mappanel.up('tabpanel');
//                    // Set the mappanel active
//                    tp.setActiveTab(mappanel);
//                } else{
//                    createPointCtrl.deactivate();
//                }
//            }
//        });
//        var createButton = Ext.create('Ext.button.Button', createAction);
//        tbar.insert(0, createButton);
//
//
//    },
//
//    onSubmitButtonClick: function(button, event){
//
//        console.log("onSubmitButtonClick");
//
//        var me = this;
//        var formpanel = button.up('form');
//        var theform = formpanel.getForm();
//        if (theform.isValid()) {
//
//            // The form cannot be submitted 'normally' because ActivityProtocol expects a JSON object.
//            // As a solution, the form values are used to create a JSON object which is sent using an
//            // AJAX request.
//            // http://www.sencha.com/forum/showthread.php?132082-jsonData-in-submit-action-of-form
//
//            // collect values and fill them into TagGroups
//            // TODO: it seems that the main tag (first added to dict) always remains in first position, but
//            // maybe this should be ensured in a better way ...
//            var taggroups = [];
//            var stakeholders = [];
//
//            // Get the geometry
//            var geometry = null;
//            var geojson = new OpenLayers.Format.GeoJSON();
//            if(this.getNewActivityPanel().getNewFeatureGeometry()){
//                geometry = Ext.decode(geojson.write(this.getNewActivityPanel().getNewFeatureGeometry()));
//            }
//
//            var comps = formpanel.query('lo_stakeholderfieldcontainer');
//            for(var j = 0; j < comps.length; j++ ) {
//                var fieldContainer = comps[j];
//                var stakeholder = {}
//                stakeholder['id'] = fieldContainer.getStakeholderId();
//                //stakeholder['role'] = fieldContainer.getStakeholderRole();
//                stakeholder['role'] = 6;
//                stakeholder['version'] = fieldContainer.getStakeholderVersion();
//                stakeholder['op'] = 'add';
//                stakeholders.push(stakeholder);
//            }
//
//            // Loop through each form panel (they form taggroups)
//            var forms = formpanel.query('form[name=taggroupfieldset]');
//            for (var i in forms) {
//                var tags = [];
//                var main_tag = new Object();
//                // Within a taggroup, loop through each tag
//                var tgpanels = forms[i].query('lo_newtaggrouppanel');
//                for (var j in tgpanels) {
//                    var c = tgpanels[j];
//                    tags.push({
//                        'key': c.getKeyValue(),
//                        'value': c.getValueValue(),
//                        'op': 'add'
//                    });
//                    if (c.isMainTag()) {
//                        main_tag.key = c.getKeyValue();
//                        main_tag.value = c.getValueValue()
//                    }
//                }
//                if (tags.length > 0) {
//                    taggroups.push({
//                        'tags': tags,
//                        'main_tag': main_tag
//                    });
//                }
//            }
//
//            var diffObject = {
//                'activities': [{
//                    'taggroups': taggroups,
//                    'geometry': geometry,
//                    'stakeholders': stakeholders
//                }]
//            };
//
//            // send JSON through AJAX request
//            Ext.Ajax.request({
//                url: '/activities',
//                method: 'POST',
//                headers: {
//                    'Content-Type': 'application/json;charset=utf-8'
//                },
//                jsonData: diffObject,
//                callback: function(options, success, response) {
//                    if(success){
//                        Ext.Msg.alert(
//                            Lmkp.ts.msg('feedback_success'),
//                            Lmkp.ts.msg('feedback_new-activity-created')
//                        );
//
//                        var p = this.getNewActivityPanel();
//                        p.setNewFeatureGeometry(null);
//
//                        // Reset form
//                        var controller = me.getController('editor.Detail');
//                        controller.onNewActivityTabActivate(p);
//
//                        var fieldContainers = formpanel.query('lo_stakeholderfieldcontainer');
//                        for(var i = 0; i < fieldContainers.length; i++){
//                            this.getSelectStakeholderFieldSet().remove(fieldContainers[i]);
//                        }
//
//                        // Remove also the feature on the map
//                        this.getMapPanel().getVectorLayer().removeAllFeatures();
//                    } else {
//                        Ext.Msg.alert(
//                            Lmkp.ts.msg('feedback_failure'),
//                            Lmkp.ts.msg('feedback_new-activity-not-created')
//                        );
//                    }
//
//                },
//                scope: this
//            });
//        }
//    },
//
//    /**
//     * Adds functions to the links to show or hide details about pending
//     * changes by current user.
//     * Because HTML links cannot be accessed directly in Ext, it is necessary to
//     * register a listener after rendering the panel.
//     */
//    onPendingUserChangesRender: function(panel) {
//        var upper_panel = panel.up('panel');
//        if (panel.name == 'showDetails') {
//            var link_showDetails = upper_panel.getEl().select('a.itemspendinguserchanges_showdetails');
//            link_showDetails.on('click', function() {
//                upper_panel.showDetails();
//            });
//        } else if (panel.name == 'hideDetails') {
//            var link_showDetails = upper_panel.getEl().select('a.itemspendinguserchanges_hidedetails');
//            link_showDetails.on('click', function() {
//                upper_panel.hideDetails();
//            });
//        }
//    },
//
//    /**
//     * Adds functions to the links to show or hide original
//     * Because HTML links cannot be accessed directly in Ext, it is necessary to
//     * register a listener after rendering the panel.
//     */
//    onRenderHiddenOriginal: function(panel) {
//        var upper_panel = panel.up('panel');
//        if (panel.name == 'showDetails') {
//            var link_showDetails = upper_panel.getEl().select('a.itempanel_showdetails');
//            link_showDetails.on('click', function() {
//                upper_panel.showDetails();
//            });
//        } else if (panel.name == 'hideDetails') {
//            var link_showDetails = upper_panel.getEl().select('a.itempanel_hidedetails');
//            link_showDetails.on('click', function() {
//                upper_panel.hideDetails();
//            });
//        }
//    }
//});