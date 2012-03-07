Ext.define('Lmkp.view.Filter', {
   	extend: 'Ext.panel.Panel',
   	alias: ['widget.filterPanel'],
   
   	title: 'Filters',
   	layout: {
       	type: 'vbox',
       	align: 'stretch',
       	pack: 'start'
   	},
   	bodyPadding: 5,
   	
   	
   	initComponent: function() {
   		this.items = [{
			// attribute selection
	       	xtype: 'form',
	       	id: 'attrForm',
	       	layout: {
	           	type: 'anchor'
	       	},
	       	border: false,
	       	items: [{
	           	xtype: 'fieldset',
	           	title: 'Set attribute filter',
	           	checkboxToggle: true,
	           	checkboxName: 'filterAttributeCheckbox',
	           	collapsed: true,
	           	items: [{
	               	xtype: 'combobox',
	               	id: 'filterAttribute',
	               	name: 'filterAttribute',
	               	store: 'Config',
	               	valueField: 'fieldLabel',
	               	displayField: 'name',
	               	queryMode: 'local',
	               	typeAhead: true,
	               	forceSelection: true,
	               	emptyText: 'Select attribute',
	               	width: 166
	          	}, {
	              	xtype: 'button',
	              	id: 'filterAdd',
	              	text: '+'
	          	}]
	       	}, {
	           xtype: 'fieldset',
	           title: 'Set time filter',
	           checkboxToggle: true,
	           checkboxName: 'filterTimeCheckbox',
	           collapsed: true,
	           items: [{
	               xtype: 'slider',
	               name: 'theslider',
	               width: 166,
	               minValue: 1990,
	               maxValue: 2020,
	               values: [1995, 2015],
	               constrainThumbs: true,
	               clickToChange: false
	           }]
	       }],
	       buttons: [{
	           text: 'Filter',
	           id: 'filterSubmit',
	           disabled: true
	       }]
		}, {
			// filter results
			xtype: 'panel',
			border: false,
			bodyStyle: {
				margin: '0 5px 0 0'
			},
			// layout: 'border',
			items: [{
				xtype: 'gridpanel',
		       	id: 'filterResults',
		       	store: 'ActivityGrid',
		       	viewConfig: {
		       		stripeRows: false
		       	},
		       	columns: [{
		       		header: 'Name',
		       		name: 'namecolumn',
		       		dataIndex: 'name',
		       		flex: 1,
		       		sortable: true
		       	}],
		       	dockedItems: [{
		       		xtype: 'pagingtoolbar',
		       		store: 'ActivityGrid',
		       		dock: 'bottom',
		       		enableOverflow: true,
		       		displayInfo: true,
		       		displayMsg: 'Displaying activities {0} - {1} of {2}',
		       		emptyMsg: '<b>No activities found.</b>'
		       	}],
			}, {
				xtype: 'panel',
				id: 'detailPanel',
				tpl: Ext.create('Ext.Template', [
					'Name: {name}<br/>',
					'Area: {area}<br/>',
					'Project Use: {project_use}<br/>',
					'Status: {project_status}<br/>',
					'Year of Investment: {year_of_investment}<br/>'
				]),
				html: 'Select an activity above to show its details.',
				height: 100
			}]
	   	}];
	   	this.callParent(arguments);
   	}
});
