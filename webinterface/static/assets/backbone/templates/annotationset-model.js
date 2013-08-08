var AnnotationSet = Backbone.Model.extend({
    urlRoot: "/api/dev/annotation_set/",
    url: function() {
        var origUrl = Backbone.Model.prototype.url.call(this);
        return origUrl + (origUrl.charAt(origUrl.length - 1) == '/' ? '' : '/');
    }
});

var AnnotationSets = Backbone.Tastypie.Collection.extend({
    model: AnnotationSet,
    url: "/api/dev/annotation_set/"
});

