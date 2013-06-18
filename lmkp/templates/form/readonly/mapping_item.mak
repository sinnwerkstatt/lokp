<%
    # Leave out all fields which contain no values! Also find out the depth of
    # the current current mapping item:
    # 0: A single tag
    # 1: A Taggroup
    # 2: A Thematic Group
    # 3: A Category
    from lmkp.views.form import structHasOnlyNullValues
    hasOnlyNullValues, depth = structHasOnlyNullValues(cstruct)
%>

% if not hasOnlyNullValues:

    % if field.name == 'map':
        <div class="row-fluid">
            <div class="span9 map-not-whole-page">
                <div id="googleMapNotFull"></div>
            </div>
        </div>

    % elif depth >= 2:
        ## Category or Thematic Group
        ${field.serialize(cstruct, readonly=True)}

    % elif depth == 1:
        ## Taggroup
        <div class="row-fluid">
            <div class="span9 grid-area">${field.serialize(cstruct, readonly=True)}</div>
        </div>

    % elif field.name not in ['tg_id', 'id', 'category', 'version']:
        ## Single tag
        <div class="span5">
            <h5 class="green">${field.title}</h5>
        </div>
        <div class="span2 inactive"></div>
        <div class="span4">
            <p class="deal-detail">${field.serialize(cstruct, readonly=True)}</p>
        </div>
    % endif

% endif