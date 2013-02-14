
<table background-color="#111">
<tr height="73" background-color="#111">
<#list features as feature>
    <td width="98"><a href="javascript:window.open('${feature.left_thumbnail_reference.value}')"><img style="position:absolute;z-index:1;width:98px;height:73px;" src="${feature.left_thumbnail_reference.value}"/></a><div style="color:white;z-index:2;position:relative;font-size:10px;">Depth:${feature.depth.value}</div></td>
</#list>
</tr>
</table>
<br/>