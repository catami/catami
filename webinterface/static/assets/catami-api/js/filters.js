function ApiFilters(updatefnc) {

    this.update = updatefnc;

    // Searches for all radio buttons contained within the "api-filter" class and
    // sets change functions for filter radio buttons
    this.init = function() {
        $('.api-filter input:radio').on('change',function() {
            updatefnc();
        });
    }


    this.get = function() {
        var filter = 'format=json';

        $('.api-filter input:radio:checked').each(function(i, obj) {
            if (obj.value != '') {
                filter += '&'+$(obj).attr('name')+'='+$(obj).val();
                //alert($(obj).parent().text());
                $(obj).closest(".api-filter").find('.api-filt-text').html($(obj).parent().text());
            }
        });
        return filter;
    }
}
