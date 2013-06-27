var Deployment = window.TastypieModel.extend({
    url: function () {
        // Important! It's got to know where to send its REST calls.
        return this.id ? '/api/dev/generic_deployment/' + this.id : '/api/dev/generic_deployment/';
    }    
});

var Deployments = Backbone.Collection.extend({
    model: Deployment,
    url: "/api/dev/generic_deployment"
});


DeploymentCollectionView = Backbone.View.extend({   
    el: $('div'),
    initialize: function () {
        this.render();
    },
    render: function () {
        var deploymentTemplate = "";
        // Compile the template using underscore       
        var deploymentType = catami_getURLParameter("type");

        deployments.each(function (deployment) {
            var type = deployment.get("type").toUpperCase();
            //if type is not specified, list everything, else filter by type
            if (deploymentType == "null" || deploymentType.toUpperCase() == type) {
                var deploymentVariables = {
                    "type": type,
                    "type_url": "?type=" + type,
                    "short_name": deployment.get("short_name"),
                    "deployment_url": deployment.get("id") + "?type=" + type,
                    "start_time": deployment.get("start_time_stamp"),
                    "end_time": deployment.get("end_time_stamp"),
                    "min_depth": deployment.get("min_depth"),
                    "max_depth": deployment.get("max_depth"),               
                    "campaign_url": deployment.get("campaign"),
                    "campaign_name": deployment.get("campaign_name")
                };
                deploymentTemplate += _.template($("#DeploymentTemplate").html(), deploymentVariables);
            }
        });
       
        var deploymentListVariables = { "deployments": deploymentTemplate };
        // Compile the template using underscore
        var deploymentListTemplate = _.template($("#DeploymentListTemplate").html(), deploymentListVariables);
        // Load the compiled HTML into the Backbone "el"

        this.$el.html(deploymentListTemplate);
        return this;
    }
});


var deployments = new Deployments;

// Make a call to the server to populate the collection 
deployments.fetch({
    success: function (model, response, options) {
        var deployment_view = new DeploymentCollectionView({
            el: $("#DeploymentListContainer"),
            collection: deployments
        });
    },
    error: function (model, response, options) {
        alert('fetch failed: ' + response.status);
    }

});




