Ext.define('Lmkp.view.moderation.CompareReview', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.lo_moderatorcomparereview',

    requires: [
        'Lmkp.store.CompareInvolvements',
        'Lmkp.store.CompareTagGroups',
        'Lmkp.store.CompareVersions',
        'Lmkp.store.CompareMetadata',
        'Lmkp.store.ReviewDecisions'
    ],

    layout: 'border',
    border: false,
    items: [
        {
            xtype: 'container',
            region: 'north',
            flex: 0,
            layout: {
                align: 'stretch',
                type: 'vbox'
            },
            items: [
                {
                    xtype: 'panel',
                    html: Lmkp.ts.msg('moderator_approving-creates-new-version'),
                    bodyCls: 'notice',
                    bodyPadding: 5,
                    hidden: true,
                    itemId: 'recalculationNotice'
                }, {
                    xtype: 'container',
                    layout: {
                        align: 'stretchmax',
                        type: 'hbox'
                    },
                    defaults: {
                        bodyPadding: 5
                    },
                    items: [
                        {
                            xtype: 'panel',
                            border: false,
                            flex: 1,
                            itemId: 'refMetadataPanel'
                        }, {
                            xtype: 'panel',
                            border: false,
                            flex: 1,
                            itemId: 'newMetadataPanel'
                        }
                    ]
                }
            ]
        }, {
            xtype: 'container',
            flex: 1,
            border: false,
            region: 'center',
            layout: 'border',
            items: [
                {
                    xtype: 'grid',
                    flex: 1,
                    region: 'center',
                    title: Lmkp.ts.msg('gui_taggroups'),
                    hideHeaders: true,
                    disableSelection: true,
                    store: 'CompareTagGroups',
                    columns: [
                        {
                            dataIndex: 'ref',
                            flex: 1,
                            name: 'compareGridColumn'
                        }, {
                            dataIndex: 'new',
                            flex: 1,
                            name: 'compareGridColumn'
                        }
                    ],
                    bbar: [
                        '->', {
                            xtype: 'button',
                            text: Lmkp.ts.msg('button_edit'),
                            itemId: 'editButton'
                        }
                    ]
                }, {
                    xtype: 'grid',
                    flex: 1,
                    region: 'south',
                    split: true,
                    title: Lmkp.ts.msg('involvements_title'),
                    hideHeaders: true,
                    disableSelection: true,
                    store: 'CompareInvolvements',
                    columns: [
                        {
                            dataIndex: 'ref',
                            flex: 1,
                            name: 'compareGridColumn'
                        }, {
                            width: 24,
                            xtype: 'templatecolumn',
                            tpl: '',
                            name: 'compareGridColumn'
                        }, {
                            dataIndex: 'new',
                            flex: 1,
                            name: 'compareGridColumn'
                        }, {
                            xtype: 'templatecolumn',
                            tpl: '',
                            width: 24,
                            align: 'center',
                            itemId: 'compareGridReviewableColumn'
                        }
                    ]
                }
            ]
        }, {
            xtype: 'form',
            itemId: 'reviewFormPanel',
            region: 'south',
            border: false,
            hidden: true,
            defaults: {
                margin: 3
            },
            layout: {
                type: 'vbox',
                align: 'stretch'
            },
            items: [
                {
                    xtype: 'combobox',
                    store: 'ReviewDecisions',
                    name: 'review_decision',
                    queryMode: 'local',
                    displayField: 'name',
                    valueField: 'id',
                    editable: false,
                    fieldLabel: Lmkp.ts.msg('moderator_review-decision'),
                    allowBlank: false,
                    value: 1
                }, {
                    xtype: 'textarea',
                    fieldLabel: Lmkp.ts.msg('moderator_review-comment'),
                    name: 'comment_textarea',
                    itemId: 'reviewCommentTextarea'
                }
            ],
            dockedItems: [
                {
                    xtype: 'toolbar',
                    dock: 'right',
                    defaults: {
                        iconAlign: 'top',
                        scale: 'medium'
                    },
                    items: ['->',
                        {
//                            text: 'Skip',
//                            tooltip: 'Skip',
//                            iconCls: 'skip-button',
//                            itemId: 'skipReviewButton'
//                        }, {
                            text: Lmkp.ts.msg('button_submit'),
                            tooltip: Lmkp.ts.msg('tooltip_submit-review'),
                            iconCls: 'button-save',
                            itemId: 'reviewSubmitButton'
                        }
                    ]
                }
            ]
        }
    ],
    dockedItems: [
        {
            xtype: 'toolbar',
            dock: 'top',
            layout: {
                type: 'hbox',
                align: 'stretchmax'
            },
            items: [
                {
                    xtype: 'combobox',
                    flex: 1,
                    editable: false,
                    fieldLabel: Lmkp.ts.msg('gui_version'),
                    queryMode: 'local',
                    store: 'CompareVersions',
                    displayField: 'display',
                    valueField: 'version',
                    itemId: 'cbRefVersion'
                }, {
                    xtype: 'combobox',
                    flex: 1,
                    editable: false,
                    fieldLabel: Lmkp.ts.msg('gui_version'),
                    queryMode: 'local',
                    store: 'CompareVersions',
                    displayField: 'display',
                    valueField: 'version',
                    itemId: 'cbNewVersion'
                }
            ]
        }, {
            xtype: 'toolbar',
            dock: 'bottom',
            defaults: {
                iconAlign: 'top',
                scale: 'medium'
            },
            items: [
                {
                    text: Lmkp.ts.msg('button_close'),
                    tooltip: Lmkp.ts.msg('tooltip_close-window'),
                    iconCls: 'button-close',
                    itemId: 'windowCloseButton'
                }, {
                    text: Lmkp.ts.msg('button_refresh'),
                    tooltip: Lmkp.ts.msg('tooltip_refresh'),
                    iconCls: 'button-refresh',
                    itemId: 'compareRefreshButton'
                }, {
                    text: Lmkp.ts.msg('button_link'),
                    tooltip: Lmkp.ts.msg('tooltip_link'),
                    iconCls: 'button-link',
                    itemId: 'compareLinkButton'
                }, '->', {
                    text: Lmkp.ts.msg('button_review'),
                    tooltip: Lmkp.ts.msg('tooltip_review'),
                    iconCls: 'button-review',
                    itemId: 'reviewButton'
                }, {
                    text: Lmkp.ts.msg('button_compare'),
                    tooltip: Lmkp.ts.msg('tooltip_compare'),
                    hidden: true,
                    iconCls: 'button-compare',
                    itemId: 'compareButton'
                }
            ]
        }
    ],

    initComponent: function() {
        this.callParent(arguments);
    }
});