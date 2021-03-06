Ext.define('Lmkp.controller.public.Map', {
    extend: 'Ext.app.Controller',
    
    refs: [{
        ref: 'mapPanel',
        selector: 'lo_publicmappanel'
    },{
        ref: 'activityGridPanel',
        selector: 'lo_publicactivitytablepanel gridpanel[itemId="activityGrid"]'
    }],

    requires: [
    'Lmkp.view.editor.EditLocation'
    ],

    stores: [
    'ActivityGrid',
    'ActivityVector',
    'Profiles',
    'StakeholderGrid'
    ],

    config: {
        geojson: {}
    },
    geojson: new OpenLayers.Format.GeoJSON(),

    init: function() {
        this.control({
            'lo_publicmappanel': {
                render: this.onMapPanelRender
            },
            'lo_publicmappanel button[itemId="zoomRegionButton"]': {
                click: this.onZoomRegionButtonClick
            }
        });
    },

    onZoomRegionButtonClick: function(button, event, eOpts){
        this.zoomToProfile(this.getMapPanel().getMap());
    },

    zoomToProfile: function(map) {

        var store = this.getProfilesStore();
        var activeProfile = store.getAt(store.findExact('active', true));
        if (activeProfile && activeProfile.get('geometry')) {
            var geoJson = new OpenLayers.Format.GeoJSON();
            var feature = geoJson.read(Ext.encode(activeProfile.get('geometry')))[0];
            var geom = feature.geometry.clone().transform(
                new OpenLayers.Projection("EPSG:4326"),
                new OpenLayers.Projection("EPSG:900913"));
            map.zoomToExtent(geom.getBounds());
        }
    },

    onMapPanelRender: function(comp){

        // Do some OpenLayers magic to prevent pink tiles
        // Copied from http://drupal.org/node/787838
        OpenLayers.Util.onImageLoadError = function(){
            this.src='/static/img/blank.gif';
        }
        OpenLayers.Tile.Image.useBlankTile=false;

        // Get the map
        var map = comp.getMap();

        // Register the moveend event with the map
        // after setting map center and zoom level
        map.events.register('moveend', this, this.onMoveEnd);

        // If logged in, show controls for editors (add or edit location etc.)
        if (Lmkp.editor) {
            var editorMapController = this.getController('editor.Map');
            editorMapController.initEditorControls();
        }

        var ctrl = comp.getSelectCtrl();
        ctrl.events.register('featurehighlighted', this, this.openDetailWindow);

        // Adds a beforeload action
        var mappanel = this.getMapPanel();
        var vectorStore = mappanel.activityFeatureStore;
        vectorStore.on('beforeload', function(store){

            // Loading mask
            mappanel.setLoading({msg: Lmkp.ts.msg('gui_loading')});

            // Get the store proxy
            var proxy = store.getProxy();
            // Get the map view.
            var map = this.getMapPanel().getMap();
            // Get the extent if the map is already initialized, else the
            // map extent is still null
            if(map.getExtent()){
                // Set the bounding box as extra parameter
                proxy.setExtraParam("bbox", map.getExtent().toBBOX());
                proxy.setExtraParam("epsg", 900913);
            }
        }, this);
        vectorStore.on('load', function() {
            // Loading mask
            mappanel.setLoading(false);
        });
    },
    
    openDetailWindow: function(event){
        var f = event.feature
        if (f) {
            // Get the selection model of the activity grid
            var selectionModel = this.getActivityGridPanel().getSelectionModel();
            // Deselect all activities in the store
            selectionModel.deselectAll(true);
            // and its store
            var store = selectionModel.getStore();

            // Try to find the record in the store (only the showed activities!)
            var activity = store.findRecord('id', f.attributes.activity_identifier);

            // If we find an activity in the current page of the store, select
            // it!
            // Else it is not possible to know on which page the record is.
            if(activity){
                selectionModel.select([activity], false, true);
            }

            // Show in any case the related stakeholder
            if (this.getStakeholderGridStore()) {
                // Update other grid panel
                this.getStakeholderGridStore().syncByOtherId(f.attributes.activity_identifier);
            }

            // Window parameters
            // Also in controller.public.Main : onShowDetailsColumnClick
            var buffer = 50; // Minimal blank space at the sides of the window
            var defaultHeight = 700; // Default height of the window
            var defaultWidth = 700; // Default width of the window

            // Prepare some values before showing the window
            var viewSize = Ext.getBody().getViewSize();
            var height = (viewSize.height > defaultHeight + buffer)
                ? defaultHeight : viewSize.height - buffer;
            var width = (viewSize.width > defaultWidth + buffer)
                ? defaultWidth : viewSize.width - buffer;

            // Finally show the window with details
            var w = Ext.create('Lmkp.view.activities.Details',{
                activity_identifier: f.attributes.activity_identifier,
                modelName: 'Lmkp.model.Activity',
                width: width,
                height: height
            }).show()._collapseHistoryPanel();
        }
    },

    onMoveEnd: function(event){
        // Store the current map center and zoom level as cookie in the format:
        // longitude|latitude|zoom
        // and set the expiration date in three month
        var map = event.object;
        var center = map.getCenter();
        var zoom = map.getZoom();
        var value = center.lon + "|" + center.lat + "|" + zoom;

        var me = this;

        var expirationDate = new Date();
        expirationDate.setMonth(new Date().getMonth() + 3);
        Ext.util.Cookies.set('_LOCATION_', value, expirationDate);

        // Reload the ActivityGrid store. Also refresh StakeholderGrid.
        var aStore = this.getActivityGridStore();
        var shStore = this.getStakeholderGridStore();

        // Reload the activities on the map
        var vectorStore = this.getMapPanel().activityFeatureStore;
        vectorStore.load();

        aStore.setInitialProxy();

        aStore.loadPage(1);
        shStore.loadPage(1);
        me.unselectAll();
    },

    /**
     * Select an activity on the map.
     */
    selectActivity: function(activity, suppressWindow){
        
        this.unselectAll();

        var ctrl = this.getMapPanel().getSelectCtrl();
        
        ctrl.events.unregister('featurehighlighted', this, this.openDetailWindow);
        
        if (activity.modelName == 'Lmkp.model.Activity') {
            var layer = this.getMapPanel().getActivitiesLayer();
            // Try to find the corresponding feature
            var feature = layer.getFeaturesByAttribute('activity_identifier', activity.get('id'))[0];
            if(feature){
                ctrl.select(feature);
            }
        }

        ctrl.events.register('featurehighlighted', this, this.openDetailWindow);
        
    },

    selectFeature: function(feature){

        this.unselectAll();

        var ctrl = this.getMapPanel().getSelectCtrl();

        ctrl.events.unregister('featurehighlighted', this, this.openDetailWindow);

        if(feature){
            ctrl.select(feature);
        }

        ctrl.events.register('featurehighlighted', this, this.openDetailWindow);
    },

    /**
     * Unselect all activities.
     */
    unselectAll: function(){
        this.getMapPanel().getSelectCtrl().unselectAll();
    },

    _getVectorsFromActivity: function(activity) {

        // Make sure item is an 'Activity'
        if (activity.modelName != 'Lmkp.model.Activity') {
            return null;
        }

        // Collect vectors, transform and return them
        var geom = activity.get('geometry');
        var map = this.getMapPanel();
        var vectors = this.geojson.read(Ext.encode(geom));
        if (vectors) {
            for(var j = 0; j < vectors.length; j++){
                vectors[j].geometry.transform(
                    map.geographicProjection,
                    map.sphericalMercatorProjection
                    );
            }
            return vectors;
        }
    }

});