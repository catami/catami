<table background-color="#111" class="table table-striped table-condensed">
<tr height="73" background-color="#111">
<#list features as feature>
    <td width="98"><a href="javascript:window.open('MEDIA_HOST${feature.web_location.value}')"><img src="MEDIA_HOST${feature.web_location.value}" width="73" height="98"/></td>
</#list>
</tr>
<tr>
<#list features as feature>
<td><div style="font-size:10px;"><strong>Depth:</strong>${feature.depth.value}</div></td>
</#list>
</tr>
<tr>
<#list features as feature>
<td><div style="font-size:10px;"><strong>Lat:</strong>${feature.position.rawValue[7..13]}</div></td>
</#list>
</tr>
<tr>
<#list features as feature>
<td><div style="font-size:10px;"><strong>Long:</strong>${feature.position.rawValue[19..25]}</div></td>
</#list>
</tr>
</table>
