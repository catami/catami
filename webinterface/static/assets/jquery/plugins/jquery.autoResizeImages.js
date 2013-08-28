/**
 *
 * PLUGIN: jquery.autoResizeImages
 * BY: Mattias Norell
 * VERSION: 0.5 (based on jQuery 1.4.4)
 * BROWSERS: Safari 4, Chrome 7, Firefox 3.6
 * ABOUT: Auto resize images.
 * HOW-TO: $(img).autoResizeImages({maxSize:500});
 *
 **/
(function($){
    jQuery.fn.autoResizeImages = function(options) {
        var defaults = {
			maxSize:-1
        };

        var options = $.extend(defaults, options);

		return this.each(function(){
			if($(this).width() > $(this).height()){
				if($(this).width() > options.maxSize){
					var ratio = $(this).width() / $(this).height();
					$(this).css("width",options.maxSize);
					$(this).css("height",options.maxSize / ratio);
				}
			}else{
				if($(this).height() > options.maxSize){
					var ratio = $(this).height() / $(this).width();
					$(this).css("height",options.maxSize);
					$(this).css("width",options.maxSize / ratio)
				}
			}
		});
    };
})(jQuery);