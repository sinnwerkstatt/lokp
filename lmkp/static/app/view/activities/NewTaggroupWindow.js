Ext.define('Lmkp.view.activities.NewTaggroupWindow', {
	extend: 'Ext.window.Window',
	
	layout: 'fit',
	defaults: {
		border: 0
	},
	width: 400,
	
	initComponent: function() {
		var me = this;
		
		// set window title
		name = (me.activity_name) ? me.activity_name : Lmkp.ts.msg("unnamed-activity");
		this.title = 'Add information to activity \'' + name + '\'';
		
		if (me.activity_identifier) {
			// prepare the form
			var form = Ext.create('Ext.form.Panel', {
				border: 0,
				bodyPadding: 5,
				layout: 'anchor',
				defaults: {
					anchor: '100%'
				},
				items: [{
					// submit activity_identifier as well
					xtype: 'hiddenfield',
					name: 'activity_identifier',
					value: me.activity_identifier
				}, {
					// button to add new attribute selection to form
					xtype: 'panel',
					layout: {
						type: 'hbox',
						flex: 'stretch'
					},
					border: 0,
					items: [{
						// empty panel for spacing
						xtype: 'panel',
						flex: 1,
						border: 0
					}, {
						// the button
						xtype: 'button',
						text: '[+] Add item',
						flex: 0,
						handler: function() {
							// functionality to add new attribute selection to form
							var fieldContainer = form.up('window')._getFieldContainer(store, completeStore, true);
							form.insert(form.items.length-1, fieldContainer);
						}
					}]
				}],
				// submit button
				buttons: [{
					formBind: true,
					disabled: true,
					text: 'Submit',
					handler: function() {
						console.log("submitted");
					}
				}]
			});
			
			// load the config store
			var store = Ext.create('Lmkp.store.Config');
			store.load();
			// another instance of the config store is needed to keep track of all attributes available
			var completeStore = Ext.create('Lmkp.store.Config');
			completeStore.load();
			
			// add initial attribute selection to form
			var fieldContainer = this._getFieldContainer(store, completeStore, false);
			form.insert(1, fieldContainer);
						
			// add form to window
			this.items = form;
		}
		this.callParent(arguments);
	},
	
	/**
	 * Returns a FieldContainer with a ComboBox for attribute selection.
	 * 'store' is needed to display only attributes that are not yet selected
	 * 'completeStore' keeps track of all attributes available
	 * 'removable' indicates whether delete-button is disabled or not
	 */
	_getFieldContainer: function(store, completeStore, removable) {
		var fieldContainer = Ext.create('Ext.form.FieldContainer', {
			layout: 'hbox',
			items: [{
				// ComboBox to select attribute
				xtype: 'combobox',
				name: 'tg_combobox',
				store: store,
				valueField: 'name',
				displayField: 'fieldLabel',
				queryMode: 'local',
				typeAhead: true,
				forceSelection: true,
				flex: 1,
				allowBlank: false,
				margin: '0 5 5 0',
				listeners: {
					// functionality to replace value field based on selected attribute
					change: function(combo, newValue, oldValue, eOpts) {
						// remove newly selected value from store
						var currentRecord = store.findRecord('name', newValue);
						store.remove(currentRecord);
						// add previously selected (now deselected) value to store again
						var previousRecord = completeStore.findRecord('name', oldValue);
						if (previousRecord) {
							store.add(previousRecord);
						}
						// replace the value field
						fieldContainer.items.getAt(fieldContainer.items.findIndex('name', 'tg_valuefield')).destroy();
						newField = this.up('window')._getValueField(currentRecord);
						fieldContainer.insert(1, newField);
					}
				}
			}, {
				// initial dummy TextField (disabled)
				xtype: 'textfield',
				name: 'tg_valuefield',
				flex: 1,
				disabled: true,
				margin: '0 5 0 0'
			}, {
				// button to delete attribute (disabled or not)
				xtype: 'button',
				text: '[-] Delete',
				disabled: !removable,
				handler: function() {
					// functionality to remove attribute
					var fieldContainer = this.up('fieldcontainer');
					// add value (if selected) to store again
					var selectedValue = fieldContainer.items.getAt(fieldContainer.items.findIndex('name', 'tg_combobox')).getValue();
					if (selectedValue) {
						store.add(completeStore.findRecord('name', selectedValue));
					}
					// remove fields
					fieldContainer.removeAll(); // remove items first to allow form to check its validity
					fieldContainer.destroy();
				}
			}]
		});
		return fieldContainer;
	},
	
	/**
	 * Returns a form field (ComboBox, NumberField or TextField)
	 * Basically the same as in controller.Filter)
	 */
	_getValueField: function(record) {
        var fieldName = 'tg_valuefield';
        // try to find categories
        var selectionValues = record.get('store');
        if (selectionValues) {      // categories of possible values available, create ComboBox
            var valueField = Ext.create('Ext.form.field.ComboBox', {
                name: fieldName,
                store: selectionValues,
                queryMode: 'local',
                editable: false,
                value: selectionValues[0],
                margin: '0 5 0 0',
                allowBlank: false
            });
        } else {                    // no categories available, create field based on xtype
            switch (record.get('xtype')) {
                case "numberfield":
                    var valueField = Ext.create('Ext.form.field.Number', {
                        name: fieldName,
                        margin: '0 5 0 0',
                        allowBlank: false
                    });
                    // add validation if available
                    if (record.get('validator')) {
                    	valueField.validator = new Function('value', record.get('validator'));
                    }
                    break;
                default:
                    var valueField = Ext.create('Ext.form.field.Text', {
                        name: fieldName,
                        margin: '0 5 0 0',
                        allowBlank: false
                    });
                    // add validation if available
                    if (record.get('validator')) {
                    	valueField.validator = new Function('value', record.get('validator'));
                    }
                    break;
            }
        }
        return valueField;
    },
});
