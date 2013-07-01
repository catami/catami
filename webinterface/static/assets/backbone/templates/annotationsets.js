var AnnotationSet = window.TastypieModel.extend({
    url: function () {
        // Important! It's got to know where to send its REST calls.
        return this.id ? '/api/dev/annotation_set/' + this.id + "/" : '/api/dev/annotation_set/';
    }
});

var AnnotationSet = Backbone.Collection.extend({
    model: Project,
    url: "/api/dev/annotation_set/"
});