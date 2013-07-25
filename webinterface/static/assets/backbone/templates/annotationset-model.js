var AnnotationSet = Backbone.Model.extend({
    urlRoot: "/api/dev/annotation_set/"
});

var AnnotationSets = Backbone.Tastypie.Collection.extend({
    model: AnnotationSet,
    url: "/api/dev/annotation_set/"
});

