var labelType, useGradients, nativeTextSupport, animate;
var parent_based_list, child_based_tree;

(function() {
  var ua = navigator.userAgent,
      iStuff = ua.match(/iPhone/i) || ua.match(/iPad/i),
      typeOfCanvas = typeof HTMLCanvasElement,
      nativeCanvasSupport = (typeOfCanvas == 'object' || typeOfCanvas == 'function'),
      textSupport = nativeCanvasSupport && (typeof document.createElement('canvas').getContext('2d').fillText == 'function');
  //I'm setting this based on the fact that ExCanvas provides text support for IE
  //and that as of today iPhone/iPad current text support is lame
  labelType = (!nativeCanvasSupport || (textSupport && !iStuff))? 'Native' : 'HTML';
  nativeTextSupport = labelType == 'Native';
  useGradients = nativeCanvasSupport;
  animate = !(iStuff || !nativeCanvasSupport);
})();

var Log = {
  elem: false,
  write: function(text){
    if (!this.elem)
      this.elem = document.getElementById('log');
    this.elem.innerHTML = text;
    this.elem.style.left = (500 - this.elem.offsetWidth / 2) + 'px';
  }
};


var icicle;
var currentSelection = [];

function classificationTreeBuilder(jsonData){
  // takes the json of caab code objects from the catami API 
  // and converts it from a list of objects with parent information
  // to a JSON Tree with child arrays

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
        new_array[parent_id-1].children.push(new_array[index-1]);
      }
    }
  }

  // we accululated the children to parent nodes from the bottom up. So
  // everything ends up the top node

  generate_fullnames_for_tree(new_array[0]);
  return new_array[0];
}

function caab_as_icicle_node(object){
  var icicle_node = {};
  var icicle_data = {};

  icicle_node.id = object.caab_code;
  icicle_node.name = object.code_name;
  icicle_data['$area'] = 5;
  icicle_data['$dim'] = 5;
  icicle_data['$color'] = '#'+object.point_colour;
  icicle_data['caabcode_object'] = object.caab_code;
  icicle_data['caabcode_id'] = object.id;
  icicle_node.data = icicle_data;
  icicle_node.children = [];
  return icicle_node;
}

function fullname_for_caabcode(caabname, caabcode){
  return caabname+':'+caabcode;
}


function generate_fullnames_for_tree(code_tree){
  //recurse through the tree to make fullnames
  //code_tree.data.fullname = code_tree.name;

  for (var i = 0; i < code_tree.children.length; i++){
    if(code_tree.data.fullname){
      code_tree.children[i].data.fullname = code_tree.data.fullname+': '+code_tree.children[i].name;
    } else {
      code_tree.children[i].data.fullname = code_tree.children[i].name;
    }
    generate_fullnames_for_tree(code_tree.children[i]);
  }
}

function start_icicle_view(){
  var json;

  new_array = [];

  //left panel controls
  controls();

  // get the classification data and get it organised
  var classification_api = 'http://localhost:8000/api/dev/annotation_code/?format=json&limit=999';
  var class_code;
  ajaxobj = $.ajax({
      dataType: "json",
      async: false,
      url: classification_api,
      success: function (jsonData) {
         json = classificationTreeBuilder(jsonData);
         parent_based_list = jsonData;
         child_based_tree = json;
      }
  });
  // init Icicle
  icicle = new $jit.Icicle({
    // id of the visualization container
    injectInto: 'annotation-chooser',
    // whether to add transition animations
    animate: true,
    duration: 100,
    fps: 40,
    transition: $jit.Trans.Quad.easeInOut,
    // nodes offset
    offset: 1,
    // whether to add cushion type nodes
    cushion: false,
    //show only three levels at a time
    constrained: true,
    levelsToShow: 2,
    // enable tips
    Tips: {
      enable: true,
      type: 'Native',
      // add positioning offsets
      offsetX: 20,
      offsetY: 20,
      // implement the onShow method to
      // add content to the tooltip when a node
      // is hovered
      onShow: function(tip, node){
        // count children
        var count = 0;
        node.eachSubnode(function(){
          count++;
        });
        // add tooltip info
        tip.innerHTML = "<div class=\"tip-title\"><b>Name:</b> " + node.name + "</div><div class=\"tip-text\">" + count + " children</div>";
      }
    },
    // callbacks for node actions
    onAfterCompute: function(){
      alert('yep');
    },
    // Add events to nodes
    Events: {
      enable: true,
      onMouseEnter: function(node) {
        //add border and replot node
        node.setData('border', '#33dddd');
        icicle.fx.plotNode(node, icicle.canvas);
        icicle.labels.plotLabel(icicle.canvas, node, icicle.controller);
      },
      onMouseLeave: function(node) {
        node.removeData('border');
        icicle.fx.plot();
      },
      onClick: function(node){
        if (node) {
          //hide tips and selections
          icicle.tips.hide();
          if(icicle.events.hovered)
            this.onMouseLeave(icicle.events.hovered);
          //perform the enter animation
          icicle.enter(node);
          currentSelection.name= fullname_for_caabcode(node.data.fullname,node.id);
          currentSelection.caabcode_id = node.data.caabcode_id;
          currentSelection.caabcode = node.id;
          GlobalEvent.trigger("annotation_chosen", currentSelection.caabcode_id);
        }
      },
      onRightClick: function(){
        //hide tips and selections
        icicle.tips.hide();
        if(icicle.events.hovered)
          this.onMouseLeave(icicle.events.hovered);
        //perform the out animation
        icicle.out();
      }
    },
    // Add canvas label styling
    Label: {
      overridable: true,
      type: labelType,
      size: 15,
      family: 'Helvetica',
      textAlign: 'center',
      textBaseline: 'alphabetic'
    },
    // Add the name of the node in the corresponding label
    // This method is called once, on label creation and only for DOM and not
    // Native labels.
    onCreateLabel: function(domElement, node){
      domElement.innerHTML = node.name;
      var style = domElement.style;
      style.fontSize = '0.9em';
      style.display = '';
      style.cursor = 'pointer';
      style.color = '#333';
      style.overflow = 'hidden';
    },
    // Change some label dom properties.
    // This method is called each time a label is plotted.
    onPlaceLabel: function(domElement, node){
      var style = domElement.style,
          width = node.getData('width'),
          height = node.getData('height');
      if(width < 7 || height < 7) {
        style.display = 'none';
      } else {
        style.display = '';
        style.width = width + 'px';
        style.height = height + 'px';
      }
    }
  });
  // load data
  icicle.loadJSON(json);
  // compute positions and plot
  icicle.refresh();
  //end
}

//init controls
function controls() {
  var jit = $jit;
  //define goto parent button action
  var gotoparent = jit.id('goto_parent_button');
  jit.util.addEvent(gotoparent, 'click', function() {
    //GlobalEvent.trigger("new_parent_icicle_node", currentSelection.caabcode_id);
    icicle.out();
  });
}
//end
