var Deployment = Backbone.Model.extend({
    urlRoot: "/api/dev/deployment/",
});

var Deployments = Backbone.Tastypie.Collection.extend({
    urlRoot: "/api/dev/deployment/",
    model: Deployment
});

DeploymentCollectionView = Backbone.View.extend({   
    el: $('div'),
    meta: {},
    initialize: function (options) {
        this.meta = options['meta']; //assign specified metadata to local var
        this.render();
    },
    render: function () {
        var deploymentTemplate = "";
        // Compile the template using underscore                   
        
        deployments.each(function (deployment) {
            var type = deployment.get("type").toUpperCase()
            var deploymentVariables = {
                "type": type,
                "type_url": "?type=" + type,
                "short_name": deployment.get("short_name"),
                "deployment_url": deployment.get("id"),
                "start_time": deployment.get("start_time_stamp"),
                "end_time": deployment.get("end_time_stamp"),
                "min_depth": deployment.get("min_depth"),
                "max_depth": deployment.get("max_depth"),               
                "campaign_url": CampaignListUrl + catami_getIdFromUrl(deployment.get("campaign")) + "/",
                "campaign_name": deployment.get("campaign_name")
            };
            deploymentTemplate += _.template($("#DeploymentTemplate").html(), deploymentVariables);            
        });
       
        var deploymentListVariables = { "deployments": deploymentTemplate };
        // Compile the template using underscore
        var deploymentListTemplate = _.template($("#DeploymentListTemplate").html(), deploymentListVariables);
        // Load the compiled HTML into the Backbone "el"

        this.$el.html(deploymentListTemplate);

        //Create pagination
        var options = catami_generatePaginationOptions(this.meta);
        $('#pagination').bootstrapPaginator(options);

        return this;
    }
});

var deployments = new Deployments();
loadPage();


function loadPage(offset) {
    var off = {}
    if (offset) off = offset;
    var type = {}
    var deploymentType = catami_getURLParameter("type");
    
    if (deploymentType && deploymentType != 'null') type = deploymentType.toUpperCase();
    // Make a call to the server to populate the collection 
    deployments.fetch({
        data: { offset: off,
                type: type},
        success: function (model, response, options) {
            var deployment_view = new DeploymentCollectionView({
                el: $("#DeploymentListContainer"),
                collection: deployments,
                meta: deployments.meta //read from initiaisation method's "option" variable
            });
        },
        error: function (model, response, options) {
            alert('fetch failed: ' + response.status);
        }
    });
}

