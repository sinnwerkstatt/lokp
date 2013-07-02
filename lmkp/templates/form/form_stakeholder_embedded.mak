<form
    id="${field.formid}"
    action="${field.action}"
    method="${field.method}"
    enctype="multipart/form-data"
    accept-charset="utf-8">

    <input type="hidden"
           name="_charset_"
    />
    <input type="hidden"
           name="__formid__"
           value="${field.formid}"
    />

    % if field.error:
        <div class="alert alert-error">
            <h5>${_("There was a problem with your submission")}</h5>
            <p>${_("Errors have been highlighted below")}</p>
        </div>
    % endif

    % for child in field.children:
        ${child.render_template(field.widget.item_template)}
    % endfor

    % for button in field.buttons:
        <div class="row-fluid">
            <div class="span3 offset9 text-center">
                <ul>
                    % if button.css_class == 'formstepactive':
                        <div class="active-wrapper">
                    % endif

                    <li
                        % if button.name == 'submit':
                            style="background-color:gray;"
                        % endif
                        >
                        <button
                            id="${field.formid + button.name}"
                            name="${button.name}"
                            value="${button.value}"
                            class="btnText ${button.css_class}"
                            onclick="showLoadingIndicator(this);">
                            ${button.title}
                        </button>
                    </li>

                    % if button.css_class == 'formstepactive':
                        </div>
                    % endif
                </ul>
            </div>
        </div>
    % endfor

    % if field.use_ajax:
        <script type="text/javascript">
            deform.addCallback(
                '${field.formid}',
                function(oid) {
                    var target = '#' + oid;
                    var options = {
                        target: target,
                        replaceTarget: true,
                        url: '/stakeholders/form?embedded=True',
                        success: function() {
                            deform.processCallbacks();
                            deform.focusFirstInput(target);
                            return false;
                        }
                    };
                    var extra_options = ${field.ajax_options} || {};
                    $('#' + oid).ajaxForm($.extend(options, extra_options));
                }
            );
        </script>
    % endif

</form>