Ext.define('Lmkp.store.Languages', {
	extend: 'Ext.data.Store',
	requires: 'Lmkp.model.Language',
	model: 'Lmkp.model.Language'
	
	/**
	 * autoLoad disabled because it loads too late.
	 * The combobox (eg. in controller/Main.js) needs to know these values to set
	 * the current value as selected.
	 * 
	 * Use this.getLanguagesStore().load() in controller to load store manually.
	 */
	// autoLoad: true
})
