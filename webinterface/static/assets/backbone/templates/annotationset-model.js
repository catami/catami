var AnnotationSet = Backbone.Model.extend({
    urlRoot: "/api/dev/generic_annotation_set/"
});

var AnnotationSets = Backbone.Tastypie.Collection.extend({
    model: AnnotationSet,
    url: "/api/dev/generic_annotation_set/"
});

