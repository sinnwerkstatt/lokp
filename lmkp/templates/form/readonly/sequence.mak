% for i, tup in enumerate(subfields):
    % if i > 0:
            </div>
        </div>
        <div class="row-fluid">
            <div class="span9 grid-area">
    % endif
    ${field.render_template(field.widget.readonly_item_template, field=tup[1], cstruct=tup[0])}
% endfor