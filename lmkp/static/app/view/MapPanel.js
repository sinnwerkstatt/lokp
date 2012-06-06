Ext.define('Lmkp.view.MapPanel',{
    extend: 'GeoExt.panel.Map',
    alias: ['widget.mappanel'],

    requires: [
    'GeoExt.Action'
    ],

    center: new OpenLayers.LonLat(0,0),

    config: {
        map: {},
        zoomBoxControl: {}
    },

    layout: 'fit',

    geographicProjection: new OpenLayers.Projection("EPSG:4326"),

    zoomBoxControl: new OpenLayers.Control.ZoomBox({
        id: 'zoombox',
        type: OpenLayers.Control.TYPE_TOGGLE
    }),

    map: {
        displayProjection: this.geographicProjection,
        layers: [
        new OpenLayers.Layer.OSM('mapnik'),
        new OpenLayers.Layer.Vector('vector',{
            isBaseLayer: false,
            // Add an event listener to reproject all features from geographic
            // projection to the spherical Mercator projection.
            // Thus: the layer expect that all features are in EPSG:4326!
            eventListeners: {
                "beforefeatureadded": function(feature){
                    var geom = feature.feature.geometry;
                    // Reproject the feature's geometry from geographic coordinates
                    // to spherical Mercator coordinates.
                    geom.transform(new OpenLayers.Projection("EPSG:4326"), new OpenLayers.Projection("EPSG:900913"));
                }
            }
        })
        ],
        projection: this.sphericalMercatorProjection
    },

    sphericalMercatorProjection: new OpenLayers.Projection("EPSG:900913"),
    
    tbar: [Ext.create('Ext.button.Button', Ext.create('GeoExt.Action',{
        control: this.zoomBox,
        iconCls: 'zoom-in-button',
        toggleGroup: 'map-controls'
    })),{
        iconCls: 'pan-button',
        toggleGroup: 'map-controls'
    },'->',{
        fieldLabel: 'Change Map Layer',
        store: [
        'mapnik',
        'osmarenderer'
        ],
        queryMode: 'local',
        xtype: 'combobox'
    }],

    zoom: 2,

    getVectorLayer: function(){
        return this.getMap().getLayersByName('vector')[0];
    },

    getBaseLayer: function(){
        return this.getMap().getLayersByName('mapnik')[0];
    }

})
