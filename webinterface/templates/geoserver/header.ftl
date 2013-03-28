<#--
Header section of the GetFeatureInfo HTML output. Should have the <head> section, and
a starter of the <body>. It is advised that eventual css uses a special class for featureInfo,
since the generated HTML may blend with another page changing its aspect when usign generic classes
like td, tr, and so on.
-->
<html>
  <head>
    <title>Geoserver GetFeatureInfo output</title>
  </head>
  <style type="text/css">

  </style>
  <script type="text/javascript">
    <#list features as feature>
        $("#image-${feature.id.value}").load(nil,function(){
            getThumbnailURL(${feature.id.value});
        });
    </#list>

    function getThumbnailURL(requested_id) {            
        var requested_api_url = 'http://localhost:8000/api/dev/image/'+requested_id+'/?&format=json';
        
        $.ajax({
             async: true,
             url: requested_api_url,
             dataType: "json",
             success: function(json_data) {
                $("#image-"+requested_id).html("<img src='http://localhost:8888/json_data[\"thumbnail_location\"]'/>")
             }
        })                       
    }
    

</script>

  <body>
