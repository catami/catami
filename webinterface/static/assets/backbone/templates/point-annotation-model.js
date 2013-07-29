var PointAnnotation = Backbone.Model.extend({
    urlRoot: "/api/dev/point_annotation/",
    url: function() {
        var origUrl = Backbone.Model.prototype.url.call(this);
        return origUrl + (origUrl.charAt(origUrl.length - 1) == '/' ? '' : '/');
    }
});

var PointAnnotations = Backbone.Tastypie.Collection.extend({
    model: PointAnnotation,
    url: "/api/dev/point_annotation/"
});