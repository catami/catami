var PointAnnotation = Backbone.Model.extend({
    urlRoot: "/api/dev/generic_point_annotation/"
});

var PointAnnotations = Backbone.Tastypie.Collection.extend({
    model: PointAnnotation,
    url: "/api/dev/generic_point_annotation/"
});