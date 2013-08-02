var WholeImageAnnotation = Backbone.Model.extend({
    urlRoot: "/api/dev/whole_image_annotation/",
    url: function() {
        var origUrl = Backbone.Model.prototype.url.call(this);
        return origUrl + (origUrl.charAt(origUrl.length - 1) == '/' ? '' : '/');
    }
});

var WholeImageAnnotations = Backbone.Tastypie.Collection.extend({
    model: WholeImageAnnotation,
    url: "/api/dev/whole_image_annotation/"
});