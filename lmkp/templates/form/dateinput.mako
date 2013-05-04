<input type="date"
       name="${field.name}"
       value="${cstruct}"

        % if field.widget.size:
            size = ${field.widget.size}
        % endif

        % if field.widget.css_class:
            class = ${field.widget.css_class}
        % endif

        % if field.widget.style:
            style = ${field.widget.style}
        % endif

        id="${field.oid}"
/>

<script type="text/javascript">
    deform.addCallback(
        '${field.oid}',
        function(oid) {
            $('#' + oid).datepicker(${options});
        }
    );
</script>