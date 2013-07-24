console.log("init d3 icicle");

var classification_api = '/api/dev/annotation_code/?format=json&limit=999';

var current_depth = 0;

var w = 1000,
    h = 500,
    //x = d3.scale.linear().range([0, w]),
    x = d3.scale.linear().range([0, w]),
    y = d3.scale.linear().range([0, h]),
    color = d3.scale.category20c();

var svgContainer = d3.select("#annotation-chooser").append("svg:svg")
    .attr("color", "#0f0")
    .attr("width", w)
    .attr("height", h);

var partition = d3.layout.partition()
    .sort(null)
    .value(function(d) { return 1; });

d3.json(classification_api, function(json) {
  var root = classificationTreeBuilder(json);

  var theData = partition.nodes(root);

  var kx = w / root.dx,
      ky = h / 1;


  var group = svgContainer.selectAll("g")
      .data(theData)
    .enter().append("svg:g")
      .attr("transform", function(d) { return "translate(" + x(depth_scaled_position(d)) + "," + y(d.x) + ")"; })
      .attr("caabcode_id", function(d) { return "code_"+d.caabcode_id; })
      .on("click", click);

  group.append("svg:rect")
      .attr("stroke", "#eee")
      .attr("width", function(d) {return depth_scaled_width(d.dy * kx, d.depth);})
      .attr("height", function(d) { return d.dx * ky; })
      .attr("fill", function(d) {  return color((d.children ? d : d.parent).name); });

  group.append("svg:text")
      .attr("transform", transform)
      .attr("class", "label")
      .attr("dy", ".35em")
      .style("opacity", function(d) { return d.dx * ky > 12 ? 1 : 0; })
      .text(function(d) { return d.name; });

  d3.select(window)
      .on("click", function() { click(root); });

  function click(d) {
        current_depth = d.depth;

        GlobalEvent.trigger("annotation_chosen", d.caabcode_id);

        kx = (d.y ? w - 0 : w) / (1 - d.y);
        console.log(d.depth,d.dy, kx);

        ky = h / d.dx;
        y.domain([d.x, d.x + d.dx]);

        var transition = group.transition()
            .duration(d3.event.altKey ? 7500 : 750)
            .attr("transform", function(d) { return "translate(" + x(depth_scaled_position(d)) + "," + y(d.x) + ")"; });

        transition.select("rect")
            .attr("width", function(d) {return depth_scaled_width(d.dy * w, d.depth);})
            .attr("height", function(d) { return d.dx * ky; });

        transition.select("text")
            .attr("transform", transform)
            .style("opacity", function(d) { return d.dx * ky > 12 ? 1 : 0; });

        // move parent text strings if needed
        if (d.parent) adjustParentText(d.parent);

        d3.event.stopPropagation();
    }

    function transform(d) {
        //transform text rect to rotate if the bounding rect container gets tall
        if(d.dx*ky > d.dy*kx) {return "translate("+10 + "," + d.dx * ky/2  + ") rotate(-90)";}
        return "translate(8," + d.dx * ky / 2 + ")";
    }
});

function depth_scaled_position(point){
    // computes offset for node taking into account 1/4 width nodes for parent hierachry 
    // in the view
    var offset;
    if (point.depth < current_depth){
        offset = point.depth * point.dy/4;
    } else {
        if (point.depth - current_depth === 0) offset = point.dy * point.depth/4;
        if (point.depth - current_depth === 1) offset = point.dy + current_depth*point.dy/4;
        if (point.depth - current_depth === 2) offset = point.dy * 1.5+ current_depth*point.dy/4;
        if (point.depth - current_depth === 3) offset = point.dy * 2 + current_depth*point.dy/4;
        if (point.depth - current_depth > 3) offset =  (point.dy * 2 + (point.depth-current_depth-3)*point.dy/4)+ current_depth*point.dy/4;
    }

    return offset;
}

function depth_scaled_width (width, depth){
    // node width.  Left in this ugly form for dev purposes.
    if (depth < current_depth) return width/4;
    if (depth - current_depth === -3) return width/4;
    if (depth - current_depth === -2) return width/2;
    if (depth - current_depth === -1) return width/2;
    if (depth - current_depth === 0) return width;
    if (depth - current_depth === 1) return width/2;
    if (depth - current_depth === 2) return width/2;
    if (depth - current_depth === 3) return width/4;
    if (depth - current_depth > 3) return width/4;
    return width;
}

// caab code to tree code
function caab_as_icicle_node(object){
  var icicle_node = {};

/*   icicle_node.id = object.caab_code; */
  icicle_node.name = object.code_name;

/*
  icicle_node['area'] = 5;
  icicle_node['dim'] = 5;
*/
  icicle_node['color'] = '#'+object.point_colour;
  icicle_node['caabcode_object'] = object.caab_code;
  icicle_node['caabcode_id'] = object.id;
  //icicle_node.children = [];
  return icicle_node;
}


function classificationTreeBuilder(jsonData){
  // takes the json of caab code objects from the catami API 
  // and converts it from a list of objects with parent information
  // to a JSON Tree with child arrays
  var new_array = [];

  var lookup = [];
  for (var i = 0, len = jsonData.objects.length; i < len; i++) {
      var temp =  jsonData.objects[i];
      lookup[jsonData.objects[i].id] = temp;
  }
  for (var index = 1; index < lookup.length; index++){
      new_array.push(caab_as_icicle_node(lookup[index]));
  }

  //list is now ordererd so we build the tree starting at the bottom and working up

  for (index = lookup.length - 1; index > 0; index--){
    // get the ID of the parent from the parent url
    if (lookup[index].parent !== null) {
      parent_text = lookup[index].parent.split('/');
      parent_id = parent_text[parent_text.length-2];
      if (parent_id > -1){
        if (new_array[parent_id-1].children === undefined){
            new_array[parent_id-1].children = [];
        }
        new_array[parent_id-1].children.push(new_array[index-1]);
      }
    }
  }

  // we accululated the children to parent nodes from the bottom up. So
  // everything ends up the top node
  return new_array[0];
}

function adjustParentText(node){
    //recurses up the parent stack to adjust text to keep parent node texts visible and ordered.
    var _group = d3.select("[caabcode_id=code_"+node.caabcode_id+"]");
    console.log(_group);
    _group.transition().select("text")
        .attr("transform", function(node){return "translate("+10 + "," + 0.3 * h  + ") rotate(-90)";});
    if (node.parent) adjustParentText(node.parent);
}