AnnotationStatusView = Backbone.View.extend({
    initialize: function () {
        //when annotation is updated, update this
        GlobalEvent.on("annotation_set_has_changed", this.render, this);
    },
    render: function () {

        var parent = this;
        var statusVariables = {};
        var chartVariables = { "image_progress": {}, "project_progress": {}, "image_dist": {}, "project_dist": {}, "topfive": {} };
        var series_project_progress = [];
        var series_image_progress = [];
        var series_image_dist = [];
        var series_project_dist = [];
        var series_topfive = [];
        var labels_X_axis_topfive = [];
        var colours = ["red", "green", "yellow", "blue", "violet", "orange", "indigo"];

        var chartRenderCallback = function () {
            require(["dojox/charting/Chart", "dojox/charting/plot2d/Columns", "dojox/charting/axis2d/Default",
                 "dojox/charting/plot2d/Pie", "dojox/charting/action2d/Highlight",
                 "dojox/charting/action2d/MoveSlice", "dojox/charting/action2d/Tooltip",
                 "dojox/charting/themes/MiamiNice", "dojox/charting/widget/Legend", "dojo/ready"],
                    function (Chart, Columns, Default, Pie, Highlight, MoveSlice, Tooltip, MiamiNice, Legend, ready) {
                        ready(function () {
                            var type = statusVariables['annotation_set_type'];

                            if (type != "Point") {
                                parent.$('#progress_image').hide();
                                parent.$('#distribution_image').hide();
                            }

                            var chart_image_progress;
                            var chart_image_dist;

                            if (type === 'Point') {
                                chart_image_progress = new Chart("chart_image_progress");
                                chart_image_progress.setTheme(MiamiNice).addPlot("default", {
                                    type: Pie,
                                    font: "normal normal 11pt Tahoma",
                                    fontColor: "black",
                                    labelOffset: -40,
                                    radius: 200
                                });

                                chart_image_dist = new Chart("chart_image_distribution");
                                chart_image_dist.setTheme(MiamiNice).addPlot("default", {
                                    type: Pie,
                                    font: "normal normal 11pt Tahoma",
                                    fontColor: "black",
                                    labelOffset: -40,
                                    radius: 200
                                });
                            }

                            var chart_project_progress = new Chart("chart_project_progress");
                            chart_project_progress.setTheme(MiamiNice).addPlot("default", {
                                type: Pie,
                                font: "normal normal 11pt Tahoma",
                                fontColor: "black",
                                labelOffset: -40,
                                radius: 200
                            });

                            var chart_project_dist = new Chart("chart_project_distribution");
                            chart_project_dist.setTheme(MiamiNice).addPlot("default", {
                                type: Pie,
                                font: "normal normal 11pt Tahoma",
                                fontColor: "black",
                                labelOffset: -40,
                                radius: 200
                            });

                            var chart_topfive = new Chart("chart_topfive");
                            chart_topfive.setTheme(MiamiNice).addPlot("default", {
                                type: Columns,
                                gap: 3
                            }).addAxis("y", {
                                vertical: true,
                                min: 0
                            });

                            if (type === 'Point') {
                                var keys_image_progress = Object.keys(chartVariables['image_progress']);
                                for (var i = 0; i < keys_image_progress.length; i++) {
                                    var key = keys_image_progress[i];
                                    series_image_progress.push({
                                        y: chartVariables['image_progress'][key] * 100,
                                        text: key,
                                        stroke: "black",
                                        tooltip: chartVariables['image_progress'][key] + "%",
                                        color: colours[i]
                                    });
                                }
                                var keys_image_dist = Object.keys(chartVariables['image_dist']);
                                for (var i = 0; i < keys_image_dist.length; i++) {
                                    var key = keys_image_dist[i];
                                    series_image_dist.push({
                                        y: chartVariables['image_dist'][key] * 100,
                                        stroke: "black",
                                        tooltip: key,
                                        color: "#" + (Math.random().toString(16) + '000000').slice(2, 8) //randomly generate RGB in hex to fill pie segment
                                    });
                                }
                            }

                            var keys_project_progress = Object.keys(chartVariables['project_progress']);
                            for (var i = 0; i < keys_project_progress.length; i++) {
                                var key = keys_project_progress[i];
                                series_project_progress.push({
                                    y: chartVariables['project_progress'][key] * 100,
                                    text: key,
                                    stroke: "black",
                                    tooltip: chartVariables['project_progress'][key] + "%",
                                    color: colours[i]
                                });
                            }


                            var keys_project_dist = Object.keys(chartVariables['project_dist']);
                            for (var i = 0; i < keys_project_dist.length; i++) {
                                var key = keys_project_dist[i];
                                //series.push({ y: 4, text: "Red", stroke: "black", tooltip: "Red is 50%" });
                                series_project_dist.push({
                                    y: chartVariables['project_dist'][key] * 100,
                                    stroke: "black",
                                    tooltip: key,
                                    color: "#" + (Math.random().toString(16) + '000000').slice(2, 8) //randomly generate RGB in hex to fill pie segment
                                });
                            }

                            var keys_topfive = Object.keys(chartVariables['topfive']);
                            labels_X_Axis_topfive = [];
                            for (var i = 0; i < keys_topfive.length; i++) {
                                var key = keys_topfive[i];
                                //series_topfive.push({ x: key, y: chartVariables['topfive'][key]});
                                series_topfive.push({ y: chartVariables['topfive'][key], fill: colours[i] });
                                labels_X_Axis_topfive.push({ value: i + 1, text: key });
                            }
                            if (type === 'Point') {
                                chart_image_progress.addSeries("Chart Image Progress", series_image_progress);
                                chart_image_dist.addSeries("Chart Image", series_image_dist);
                            }
                            chart_project_progress.addSeries("Chart Project Progress", series_project_progress);
                            chart_project_dist.addSeries("Chart Project Distribution", series_project_dist);
                            chart_topfive.addAxis("x", {
                                labels: labels_X_Axis_topfive,
                                font: "normal normal 11pt Tahoma",
                                rotation: -90,
                            });
                            chart_topfive.addSeries("Chart Top Five", series_topfive);

                            if (type === 'Point') {
                                var anim_image_progress_a = new MoveSlice(chart_image_progress, "default");
                                var anim_image_progress_b = new Highlight(chart_image_progress, "default");
                                var anim_image_progress_c = new Tooltip(chart_image_progress, "default");

                                var anim_image_dist_a = new MoveSlice(chart_image_dist, "default");
                                var anim_image_dist_b = new Highlight(chart_image_dist, "default");
                                var anim_image_dist_c = new Tooltip(chart_image_dist, "default");
                            }

                            var anim_project_progress_a = new MoveSlice(chart_project_progress, "default");
                            var anim_project_progress_b = new Highlight(chart_project_progress, "default");
                            var anim_project_progress_c = new Tooltip(chart_project_progress, "default");

                            var anim_project_dist_a = new MoveSlice(chart_project_dist, "default");
                            var anim_project_dist_b = new Highlight(chart_project_dist, "default");
                            var anim_project_dist_c = new Tooltip(chart_project_dist, "default");

                            //var chart_topfive_anim_a = new MoveSlice(chart_topfive, "default");
                            var anim_topfive_b = new Highlight(chart_topfive, "default");
                            //var chart_topfive_anim_c = new Tooltip(chart_topfive, "default");

                            if (type === 'Point') {
                                chart_image_progress.render();
                                chart_image_dist.render();
                            }
                            chart_project_progress.render();
                            chart_project_dist.render();
                            chart_topfive.render();
                        });
                    }
                );
        };

        $.ajax({
            url: '/api/dev/annotation_set/'
                + annotationSets.at(0).get('id')
                + '/' + selectedImageId
                + '/image_status/',
            dataType: "json",
            //async: false,
            success: function (response, textStatus, jqXHR) {
                var image_total = response.total;
                var image_unannotated = response.unannotated;
                var image_annotated = response.annotated;
                chartVariables['image_progress']['unannotated'] = (image_unannotated / image_total * 100).toFixed(2);;
                chartVariables['image_progress']['annotated'] = ((image_total - image_unannotated) / image_total * 100).toFixed(2);
                var image_names = Object.keys(image_annotated);
                for (var i = 0; i < image_names.length; i++) {
                    var name = image_names[i];
                    chartVariables['image_dist'][name] = (image_annotated[name] / image_total * 100).toFixed(2);
                }

                $.ajax({
                    url: '/api/dev/annotation_set/'
                        + annotationSets.at(0).get('id')
                        + '/annotation_status/',
                    dataType: "json",
                    success: function (response, textStatus, jqXHR) {
                        var type = response.annotation_set_type;
                        var total = response.total;
                        var unannotated = response.unannotated;
                        statusVariables['annotation_set_id'] = response.annotation_set_id;
                        statusVariables['annotation_set_type'] = type;
                        statusVariables['total'] = total;
                        statusVariables['unannotated'] = unannotated + " (" + (unannotated / total * 100).toFixed(2) + "%)";
                        statusVariables['annotated'] = total - unannotated + " (" + ((total - unannotated) / total * 100).toFixed(2) + "%)";

                        chartVariables['project_progress']['unannotated'] = (unannotated / total * 100).toFixed(2);
                        chartVariables['project_progress']['annotated'] = ((total - unannotated) / total * 100).toFixed(2);

                        var statusSubTemplate = "";
                        var statusSubVariables = {};
                        var annotated = response.annotated;
                        var names = Object.keys(annotated);
                        for (var i = 0; i < names.length; i++) {
                            var name = names[i];
                            statusSubVariables['sub_label'] = name;
                            statusSubVariables['sub_value'] = annotated[name] + " (" + (annotated[name] / total * 100).toFixed(2) + "%)";
                            chartVariables['project_dist'][name] = (annotated[name] / total * 100).toFixed(2);
                            statusSubTemplate += _.template($("#AnnotationStatusSubTemplate").html(), statusSubVariables);
                        }
                        statusVariables['annotated_sub'] = statusSubTemplate;

                        var topfive = response.top_five_annotated
                        var keys = Object.keys(topfive);
                        for (var i = 0; i < keys.length; i++) {
                            var key = keys[i];
                            chartVariables['topfive'][key] = topfive[key];
                        }
                        //chartVariables['topfive']['total'] = total;

                        var statusTemplate = _.template($("#AnnotationStatusTemplate").html(), statusVariables);

                        // // Load the compiled HTML into the Backbone "el"
                        parent.$el.html(statusTemplate);

                        //render the charts
                        chartRenderCallback();
                    },
                    error: function (request, status, error) {
                        alert(request.responseText);
                    }
                });
            },
            error: function (request, status, error) {
                alert(request.responseText);
            }
        });

        return this.el;
    },
    events: {
        'click #radio_progress': 'progressClicked',
        'click #radio_distribution': 'distributionClicked',
        'click #radio_topfive': 'topfiveClicked',
        'click #radio_summary': 'summaryClicked'
    },
    progressClicked: function (event) {
        this.$('#distribution_tab').hide();
        this.$('#topfive_tab').hide();
        this.$('#summary_tab').hide();
        this.$('#progress_tab').fadeIn();
    },
    distributionClicked: function (event) {
        this.$('#progress_tab').hide();
        this.$('#topfive_tab').hide();
        this.$('#summary_tab').hide();
        this.$('#distribution_tab').fadeIn();
    },
    topfiveClicked: function (event) {
        this.$('#progress_tab').hide();
        this.$('#distribution_tab').hide();
        this.$('#summary_tab').hide();
        this.$('#topfive_tab').fadeIn();
    },
    summaryClicked: function (event) {
        this.$('#progress_tab').hide();
        this.$('#distribution_tab').hide();
        this.$('#topfive_tab').hide();
        this.$('#summary_tab').fadeIn();
    }
});