//(function(){
//var this_js_script = $('script[src*=somefile]');
var width = window.innerWidth,
    height = 1000;

        function resize() {
    svg.attr("width", width).attr("height", height);
    force.size([width, height]).resume();
  }

var centerx = width/2,
centery = 500;

var color = d3.scale.category20();

var force = d3.layout.force()
    .charge(-80)//function(d){return (d.suggest <= 15) && (d.suggest != 0) ? -150 : -60;})
    .linkDistance(linkdist)
    .size([width, height]);

var svg = d3.select("body").append("svg");//.attr("preserveAspectRatio","xMidYMid slice").attr("viewBox", "0 0 1024 768")

var select = d3.select("body").append("div").text("Sort by: ").attr("id","orderdiv").append("select").attr("id","order");//.on("change", change);
    select.append("option").text("Centrality").attr("value","deg");
    select.append("option").text("Time").attr("value","time");    
    select.append("option").text("Source (to come)"); // Data join
    select.append("option").text("Sentimental analysis (to come)"); 


var timestamp_arc = d3.svg.arc()
    .startAngle(355)
    .endAngle(5)
    .innerRadius(radius + 50)
    .outerRadius(radius + 48)
        .padAngle(.01)
    .padRadius(radius / 3 );



var radius = 230//Math.min(width/4,200), //Math.min(margin.top, margin.right, margin.bottom, margin.left);
    margin = {top: 500, right: 500, bottom: 500, left: 500};//{top: 200, right: (width-3*radius)/2, bottom: 300, left: (width-3*radius)/2};
    

var hue = d3.scale.category20();
var luminance = d3.scale.sqrt()
    .domain([0, 1e6])
    .clamp(true)
    .range([90, 20]);
var chart = d3.select("svg").append("svg:svg")
    .attr("width", margin.left + margin.right)
    .attr("height",margin.top + margin.bottom)
  .append("svg:g")
    .attr("transform", "translate(" + centerx + "," + centery + ")")
    .style('opacity',0);
var partition = d3.layout.partition()
    .sort(function(a, b) { return d3.ascending(a.id, b.id); })
    .size([2*Math.PI, radius]); // 7/4* 
var arc = d3.svg.arc()
    .startAngle(function(d) { return d.x; }) // + 1/8*Math.PI
    .endAngle(function(d) { return d.x + d.dx ; }) // + 1/8*Math.PI
    .padAngle(.01)
    .padRadius(radius /3 )
    .innerRadius(function(d) { return radius ; })
    .outerRadius(function(d) { return radius - 40; });

var json //= //"/static/last24h/ug_nl_cluster.json"
,tgt;// = "/static/last24h/tgt_cluster.json";

d3.json(tgt, function(error, root) {
  if (error) throw error;
  // Compute the initial layout on the entire tree to sum sizes.
  // Also compute the full name and fill color for each node,
  // and stash the children so they can be restored as we descend.
  partition
      .value(function(d) { return d.size; })
      .nodes(root)
      .forEach(function(d) {
        d._children = d.children;
        d.sum = d.value;
        d.key = key(d);
        d.fill = fill(d);
      });
  // Now redefine the value function to use the previously-computed sum.
  partition
      .children(function(d, depth) { return depth < 2 ? d._children : null; })
      .value(function(d) { return d.sum; });
  var center = chart.append("ellipse")
      .attr("rx", radius)
      .attr("ry",radius)

      .style("fill","#ffffff")
      .on("click", zoomOut);

  center.append("title")
      .text("zoom out");
  var path = chart.selectAll("path")
      .data(partition.nodes(root).slice(1))
    .enter().append("path")
      .attr("d", arc)
      .style("fill", function(d) { return d.fill; })
     .style("pointer-events","none")
      .each(function(d) { this._current = updateArc(d); })
      .on("click", function(p){if (detail == 0) {return zoomIn(p);} else {return zoomOut(p);}})
      .on("mouseover",function(o){
        if (detail == 0) {
        var h = d3.selectAll(".node").filter(function(e) {return e.comp == o.parent.id && e.suggest != 0 ? this : null;}).node();
        var f = h.__data__;
        if (f.time != null) {
        div.html('<b>Most central article for this cluster:</b><br/><a href=' + f.url + '><b>' + f.title + '</b></a><br/><br/><b>' + f.source  + '   ' + f.time.substr(5,2) + '/' + f.time.substr(8,2) + ' ' + f.time.substr(11,5) + '</b><br/><br/>' + f.summary);}
        else {        div.html('<b>Most central article for this cluster:</b><br/><a href=' + f.url + '><b>' + f.title + '</b></a><br/><br/><b>' + f.source  + '</b><br/><br/>' + f.summary);}
        
      }});

    //var path2 = svg.append("path2").attr("d",timestamp_arc)
           //.style("fill", "#bbb")


var suggestbutton = d3.select("body")
    .append("button")
    .attr("class", "btn btn-primary visbutt")
    .attr("id","suggestbutton")
    .attr("type","button")
    .style("opacity", 1e-6)
    .style("position","absolute")
    .style("right","105px")
    .style("pointer-events","none")
    .style("top","60px" )
    .html('<span class="glyphicon glyphicon-star" aria-hidden="true">')
    .on("click",zoomSuggest);

var helper = d3.select("body")
    .append("button")
    .attr("class", "btn btn-primary visbutt")
    .attr("id","helper")
    .attr("type","button")
    .attr("data-toggle","modal")
    .attr("data-target","#myModal")
    .style("opacity", 1e-6)
    .style("position","absolute")
    .style("right","15px")
    .style("top","60px" )
    .html('<span class="glyphicon glyphicon-question-sign" aria-hidden="true"></span>');

var sharer = d3.select("body")
    .append("button")
    .attr("class", "btn btn-primary visbutt")
    .attr("id","sharer")
    .attr("type","button")
    .attr("data-toggle","modal")
    .attr("data-target","#share_modal")
    .style("opacity", 1e-6)
    .style("position","absolute")
    .style("pointer-events","none")
    .style("right","60px")
    .style("top","60px" )
    .html('<span class="glyphicon glyphicon-share-alt" aria-hidden="true"></span>');


        var timeline2 = svg.append("line").attr("class","tim").attr("x1",centerx + Math.cos(1.3*Math.PI)*radius*1.05).attr("x2",centerx + Math.cos(1.3*Math.PI)*radius*0.75).attr("y1",centery + Math.sin(1.3*Math.PI)*radius*1.05).attr("y2",centery + Math.sin(1.3*Math.PI)*radius*0.75).style("stroke-width","2px").style("stroke","#2b2b2b").style("opacity",0)
        var timeline3 = svg.append("line").attr("class","tim").attr("x1",centerx + Math.cos(0.9*Math.PI)*radius*1.05).attr("x2",centerx + Math.cos(0.9*Math.PI)*radius*0.75).attr("y1",centery + Math.sin(0.9*Math.PI)*radius*1.05).attr("y2",centery + Math.sin(0.9*Math.PI)*radius*0.75).style("stroke-width","2px").style("stroke","#2b2b2b").style("opacity",0)
        var timeline4 = svg.append("line").attr("class","tim").attr("x1",centerx + Math.cos(0.5*Math.PI)*radius*1.05).attr("x2",centerx + Math.cos(0.5*Math.PI)*radius*0.75).attr("y1",centery + Math.sin(0.5*Math.PI)*radius*1.05).attr("y2",centery + Math.sin(0.5*Math.PI)*radius*0.75).style("stroke-width","2px").style("stroke","#2b2b2b").style("opacity",0)
        var timeline5 = svg.append("line").attr("class","tim").attr("x1",centerx + Math.cos(2.1*Math.PI)*radius*1.05).attr("x2",centerx + Math.cos(2.1*Math.PI)*radius*0.75).attr("y1",centery + Math.sin(2.1*Math.PI)*radius*1.05).attr("y2",centery + Math.sin(2.1*Math.PI)*radius*0.75).style("stroke-width","2px").style("stroke","#2b2b2b").style("opacity",0)
        var timeline6 = svg.append("line").attr("class","tim").attr("x1",centerx + Math.cos(1.7*Math.PI)*radius*1.05).attr("x2",centerx + Math.cos(1.7*Math.PI)*radius*0.75).attr("y1",centery + Math.sin(1.7*Math.PI)*radius*1.05).attr("y2",centery + Math.sin(1.7*Math.PI)*radius*0.75).style("stroke-width","2px").style("stroke","#2b2b2b").style("opacity",0)
       //var timepath =  svg.append("path").path("M 100 100 a 50 50 0 1 0 35 85").attr({stroke: "#2b2b2b", opacity: 1, "stroke-width" : 2})  // this is about 62.5% of a circle, and it shows on most any browsers
  

    var recto = chart.selectAll("text")
      .data(partition.nodes(root).slice(1))
    .enter().append("text")
    //.attr("transform", function(d) { return "rotate(" + computeTextRotation(d) + ")"; })
    //.attr("x", function(d) {return radius ; })
    .attr("dx", function (d) { return computeTextRotation(d) > 180 ? "-23" : "23"; }) // margin
    .attr("dy", ".35em")
   // .style("opacity",1) // vertical-align
    //.html(function(d) { return d.name; });
    .attr("transform", function(d) { return "translate(" + arc.centroid(d) + ")rotate(" + computeTextRotation(d) + ")"; })
        .attr('text-anchor', function (d) { return computeTextRotation(d) > 180 ? "end" : "start"; })
    /*.attr("text-anchor", function(d) {
        return d.x + d.dx / 2 > Math.PI ? "end" : "start";
      })
      .attr("transform", function(d) {
        var angle = (d.x + d.dx / 2) * 180 / Math.PI - 90;
           //if (angle > 90) { angle = angle - 180; }
           
        return "rotate(" + angle + ")translate(" + (d.y  + 10)  + ")rotate(" + (angle > 90 ? -180 : 0) + ")"
       })*/

      //.attr("display", function(d) { return d.depth ? null : "none"; }) // hide inner
      .html(function(d) { return d.children ? d.name:null; });



    function computeTextRotation(d) {
  var ang = (d.x + d.dx/2-Math.PI/2)/ Math.PI*180; // add +1/8*Math.PI in case you open up the initial circle
        return (ang > 90) ? 180 + ang : ang;

}
var newradius = 5*radius;
var radiansss = 1.5*height/newradius+ 0.75*height/newradius;
  //var time1 = svg.append("text").attr("class","tim").attr("x", -3*radius + Math.cos(0.1*radiansss)*newradius*0.99).attr("y",centery + Math.sin(0.1*radiansss)*newradius*0.99).html('no timestamp').style("opacity",0).style({"text-baseline":"right","text-anchor":"right","width":"40px"}).attr("transform", function(d) { return "rotate(" + 0.1*radiansss/Math.PI*180 + ")"; })
  var time6 = svg.append("text")
      .attr("class","tim")
      .attr("x", -3*radius + Math.cos(0.12*radiansss)*newradius*1.06)
      .attr("y",centery + Math.sin(0.12*radiansss)*newradius*1.06)
      .html('no timestamp')
      .style("opacity",0)
      .style({"text-baseline":"right","text-anchor":"right"})
      .attr("transform", function(d) { return "rotate(" + 0.12*radiansss/Math.PI*180 + ")"; });

  var time5 = svg.append("text").attr("class","tim").attr("x", -3*radius + Math.cos(0.06*radiansss)*newradius*0.98).attr("y",centery + Math.sin(0.06*radiansss)*newradius*0.98).html('no timestamp').style("opacity",0).style({"text-baseline":"right","text-anchor":"right","width":"40px"}).attr("transform", function(d) { return "rotate(" + 0.06*radiansss/Math.PI*180 + ")"; })
  var time4 = svg.append("text").attr("class","tim").attr("x", -3*radius + Math.cos(0*radiansss)*newradius*0.92).attr("y",centery).html('no timestamp').style("opacity",0).style({"text-baseline":"right","text-anchor":"right","width":"40px"}).attr("transform", function(d) { return "rotate(" + 0*radiansss/Math.PI*180 + ")"; })
  var time3 = svg.append("text").attr("class","tim").attr("x", -3*radius + Math.cos(-0.075*radiansss)*newradius*0.87).attr("y",centery + Math.sin(-0.075*radiansss)*newradius*0.87).html('no timestamp').style("opacity",0).style({"text-baseline":"right","text-anchor":"right","width":"40px"}).attr("transform", function(d) { return "rotate(" + -0.075*radiansss/Math.PI*180 + ")"; })
  var time2 = svg.append("text").attr("class","tim").attr("x", -3*radius + Math.cos(-0.15*radiansss)*newradius*0.86).attr("y",centery + Math.sin(-0.15*radiansss)*newradius*0.86).html('no timestamp').style("opacity",0).style({"text-baseline":"right","text-anchor":"right","width":"40px"}).attr("transform", function(d) { return "rotate(" + -0.15*radiansss/Math.PI*180 + ")"; })
  //d3.selectAll("text").attr("transform","rotate(45)");
  var zoomfac = 2,
    clock = 2,
    suggestt = 0;



  function zoomIn(p) {
    if (p.depth > 1) p = p.parent;
    if (!p.children) return;
var newradius = 5*radius;
//partition.size([1/6* Math.PI, radius]);
    zoom(p, p,newradius,1250,750);
    d3.select("#suggestbutton").style("pointer-events","none");
    d3.selectAll("path").style("pointer-events","none");
   chart.transition().duration(750).transition().duration(1250).attr("transform", "translate(" + (-radius*3) + "," + centery + ")")
   center.transition().duration(750).transition().duration(1250).attr("rx", newradius).attr("ry",newradius)
   div.transition().duration(750).transition().duration(1250).style("left","40px").style("top", (centery + 100) + "px");//style("pointer-events","none") // add suggestion here
   d3.select("#orderdiv").transition().duration(2000).transition().duration(500).style("opacity",1);

    var g = d3.selectAll("circle").filter(function(e) {return e.comp == p.id && e.suggest != 0 ? this : null;}).node().__data__;//viscenter(p.id);//
    recto.transition().duration(2000).style("opacity",0)  // filter(function(e) {return e.id != p.id ? this : null;})
    //div.transition().duration(500).style("opacity",0);
    var h = d3.selectAll("circle").filter(function(e) {return e.comp == p.id && e.suggest != 0 ? this : null;}).node()
    var cir = d3.selectAll(".node").filter(function(d) {return p.id == d.comp ? this : null;});
    var circir = d3.selectAll("circle").filter(function(d) {return p.id == d.comp ? this : null;});
    var texts = d3.selectAll("#nodetext").filter(function(d) {return p.id == d.comp ? this : null;});
    var rects = d3.selectAll("#rect").filter(function(d) {return p.id == d.comp ? this : null;});

    //d3.selectAll("circle").style("stroke","#fff"); 
    if (g.time != null) {
    div.html('<a href=' + g.url + '><b>' + g.title + '</b></a><br/><br/><b>' + g.source  + '   ' + g.time.substr(5,2) + '/' + g.time.substr(8,2) + ' ' + g.time.substr(11,5) + '</b><br/><br/>' + g.summary);}
    else {div.html('<a href=' + g.url + '><b>' + g.title + '</b></a><br/><br/><b>' + g.source  + '</b><br/><br/>' + g.summary)}
    d3.selectAll("#image").attr("xlink:href",g.images);
     //d3.select(h).style("stroke","#2b2b2b"); 

    div.transition().duration(500).transition().duration(1500).style("left","50px").style("top", (centery + 50) + "px");//style("pointer-events","none") // add suggestion here
    rects.attr("xlink:href",function(d){return d.url;}).style("pointer-events","auto");
    //cir.style("pointer-events","auto");
    d3.selectAll("circle").filter(function(d) {return p.id != d.comp ? this : null;}).style("pointer-events","none").transition().duration(2000).style("opacity",0);
    //d3.selectAll(".link").filter(function(d) {return p.id != d.source.comp ? this : null;}).transition().duration(1000).style("opacity",0);
    d3.selectAll(".link").transition().duration(1000).style("opacity",0);
    topichead.style("border-color",color(g.comp))
        .style("font-color",color(g.comp))
        .html('<h3>topic</h3><br/><h1>'+ p.name +'</h1><br/><p># of articles:'+ cir.size()+ '<p>Clustering:' + p.clustering + '%').transition().duration(500).transition().duration(1500).style("opacity",1);
  d3.selectAll("#bubble").transition().duration(500).transition().duration(1500).style("opacity",1);
    detail = p.id;
    texts.transition().duration(500).transition().duration(1500)
            .style("opacity",1)
            .attr("dx", function (d) { return computeTextRotation(d) > 180 ? "-23" : "23"; }) // margin
            .attr("dy", ".35em")
            //.attr("transform", function(d) { return "translate(" + arc.centroid(d) + ")rotate(" + computeTextRotation(d) + ")"; })
            .attr('text-anchor', function (d) { return computeTextRotation(d) > 180 ? "end" : "start"; });

     if (clock == 0) {}
    else if (clock == 1) { 
        time2.html(p.timeinf[0]).transition().duration(2000).style("opacity",1);
        time3.html("-" + p.timeinf[1]).transition().duration(2000).style("opacity",1);
        time4.html("-" + p.timeinf[2]).transition().duration(2000).style("opacity",1);
        time5.html("-" + p.timeinf[3]).transition().duration(2000).style("opacity",1);
        time6.html("-" + p.timeinf[4]).transition().duration(2000).style("opacity",1);
    }
     //end if clock==1 

    else if (clock == 2) {
      //cir.html('blabla');

      time2.html(p.timeinf[0]).transition().duration(2000).style("opacity",0);
        time3.html("-" + p.timeinf[1]).transition().duration(2000).style("opacity",0);
        time4.html("-" + p.timeinf[2]).transition().duration(2000).style("opacity",0);
        time5.html("-" + p.timeinf[3]).transition().duration(2000).style("opacity",0);
        time6.html("-" + p.timeinf[4]).transition().duration(2000).style("opacity",0);
    } 

          cir.transition().duration(500).transition().duration(1500).attr("transform", function(d) {return around(d,centerx,centery,radius,newradius,500,clock);})
     circir.transition().duration(500).transition().duration(1500).attr("r",function(d){return 2*nodefac*(d.deg)+2;});


  } // end of zoomin function

function movetocenter(g,d,zoomfac,centerx,centery){
return "translate(" + (centerx+zoomfac*(d.x-g.x)) + "," + (centery+zoomfac*(d.y-g.y)) + ")";}
function movetocenter_link(g,d,zoomfac,center){
return center+zoomfac*(d-g);}

  function aroundtheclock(d,centerx,centery,radius){
    var radians = d.time_pos*Math.PI/180 + Math.PI/2;
return "translate(" + (centerx + Math.cos(radians)*radius) + "," + (centery + Math.sin(radians)*radius) + ")";}

function around(d,centerx,centery,radius,newradius,height,clock){
  if (clock == 1) {var radians = 1.5*d.time_pos*height/(360*newradius)+ -0.75*height/newradius; }//+ Math.PI/2-height/(4*Math.PI*newradius);
  if (clock == 2) {var radians = 1.5*d.deg_pos*height/(360*newradius)+ -0.75*height/newradius; }
    
return "translate(" + (-3*radius + Math.cos(radians)*newradius) + "," + (centery + Math.sin(radians)*newradius) + ")rotate(" + radians/Math.PI*180 + ")";}

function around_suggest(d,centerx,centery,radius,newradius,height,clock){
  if (clock == 1) {var radians = 1.5*d.time_pos*height/(360*newradius)+ -0.75*height/newradius; }//+ Math.PI/2-height/(4*Math.PI*newradius);
  if (clock == 2) {var radians = 1.5*d.suggest/root.comps*360*height/(360*newradius)+ -0.75*height/newradius; }
    

return "translate(" + (-3*radius + Math.cos(radians)*newradius) + "," + (centery + Math.sin(radians)*newradius) + ")rotate(" + radians/Math.PI*180 + ")";}


  function aroundtheclock_link(d,center,radius,bin){
    var radians = d.time_pos*Math.PI/180 + Math.PI/2;
    return center;} 

function calc_pos(d){
  var x = d3.selectAll("circle").filter(function(e) {return e.comp < d.comp ? this : null;}).size()+d3.selectAll("circle").filter(function(e) {return e.comp == d.comp ? this : null;}).size()/2,
  y = d3.selectAll("circle").size(),
    f = d3.selectAll("circle").filter(function(e) {return e.comp == d.comp? this : null;}).node().__data__;//&&e.suggest != 0
   if (0<= x/y < 0.25) {var T = Math.tan(2*Math.PI*x/y),TT = radius*2/Math.sqrt(1+Math.pow(T,2)); return [-TT*T+d.x-f.x,TT+d.y-f.y];}
   else if (0.25 <= x/y< 0.5) {var T = Math.tan(2*Math.PI*x/y-Math.PI),TT = radius*2/Math.sqrt(1+Math.pow(T,2)); return [TT*T+d.x-f.x,-TT+d.y-f.y];}
   else if (0.5 <= x/y< 0.75) {var T = Math.tan(2*Math.PI*x/y),TT = radius*2/Math.sqrt(1+Math.pow(T,2)); return [-TT*T+d.x-f.x,TT+d.y-f.y];}
   else if (0.75 <= x/y< 0.1){var T = Math.tan(2*Math.PI*x/y-3*Math.PI),TT = radius*2/Math.sqrt(1+Math.pow(T,2)); return [-TT*T+d.x-f.x,TT+d.y-f.y];}
   else {var T = Math.tan(2*Math.PI*x/y-3*Math.PI),TT = radius*2/Math.sqrt(1+Math.pow(T,2)); return [TT*T+d.x-f.x,-TT+d.y-f.y];}
        }
  function zoomOut(p) {
    //partition.size([2* Math.PI, radius]);
    detail = 0;
    if (!p.parent) return;
    zoom(p.parent, p,radius,2000,150);
    d3.select("#suggestbutton").style("pointer-events","auto");
    //d3.selectAll("path").style("pointer-events","auto");
   chart.transition().duration(2000).attr("transform", "translate(" + centerx + "," + centery + ")")
   center.transition().duration(2000).attr("rx", radius).attr("ry",radius)
   div.transition().duration(500).style("opacity",0).transition().duration(1500).style("left",centerx - radius/2 + "px").style("top",centery - radius/3 + "px" ).transition().duration(500).style("opacity",1);//style("pointer-events","none")
   d3.select("#orderdiv").transition().duration(2000).style("opacity",0);
    recto.transition().duration(2000).style("opacity",1);
    //var g = d3.selectAll("circle").filter(function(e) {return e.comp == p.id && e.suggest != 0 ? this : null;}).node().__data__;//viscenter(p.id);//
    
    if (suggestt == 0){

    var cir = d3.selectAll(".node").filter(function(d) {return p.id == d.comp ? this : null;});
    var circir = d3.selectAll("circle").filter(function(d) {return p.id == d.comp ? this : null;});
   d3.selectAll("circle").filter(function(d) {return p.id != d.comp ? this : null;}).style("pointer-events","auto").transition().duration(2000).style("opacity",1);//.style("stroke",function(d) {return (d.suggest <= root.comps) && (d.suggest != 0) ? '#2b2b2b' :'#fff';});       

  }
      else if (suggestt == 50){

    var cir = d3.selectAll(".node").filter(function(d) {return (d.suggest <= root.comps) && (d.suggest != 0) ? this : null;});
    var circir = d3.selectAll("circle").filter(function(d) {return (d.suggest <= root.comps) && (d.suggest != 0)? this : null;});
    d3.selectAll("circle").style("pointer-events","auto").transition().duration(2000).style("opacity",1);      
    suggestt = 0;
     
      }


    d3.selectAll("#rect").style("pointer-events","none");
    d3.selectAll("#nodetext").transition().duration(2000).style("opacity",0);
 
    //d3.selectAll(".link").filter(function(d) {return p.id != d.comp ? this : null;}).transition().duration(1000).style("opacity",0).transition().duration(500).style("opacity",1);
    //d3.selectAll(".link").filter(function(d) {return p.id == d.comp ? this : null;}).transition().duration(2000).style("opacity",1);
    d3.selectAll(".link").transition().duration(2000).style("opacity",1);
    //div.transition().duration(2000).style("opacity",0).transition().duration(500).style("opacity",1);
    cir.transition().duration(2000).attr("transform", function(d){ return "translate(" + (centerx+calc_pos(d)[0]) + "," + (centery+ calc_pos(d)[1]) + ")";}).style("pointer-events","none");
    circir.transition().duration(2000).attr("r",function(d){return nodefac*d.deg+6;});//.attr("stroke",function(d){return (d.suggest <= 15) && (d.suggest != 0) ?  '#2b2b2b' :'#fff';})//.attr("transform", "scale(0.5,0.5)");
//d3.selectAll("circle").filter(function(d) {return p.id == d.comp ? this : null;})
d3.selectAll(".link").filter(function(d) {return p.id == d.source.comp ? this : null;}).transition().duration(2000).transition().duration(500).style("opacity",1).attr("x1", function(d) {return centerx+calc_pos(d.source)[0];}) 
        .attr("y1", function(d) {return centery+calc_pos(d.source)[1];})
        .attr("x2", function(d) {return centerx+calc_pos(d.target)[0];})
        .attr("y2", function(d) {return centery+calc_pos(d.target)[1];})
        .attr("stroke-width", "1.5px" ); 
      

    

  topichead.transition().duration(2000).style("opacity",0);
  d3.select("#bubble").transition().duration(1000).style("opacity",0);
  div.style("pointer-events","auto")

  } //end of zoomout


  // Zoom to the specified new root.
  function zoom(root, p,newradius,sig,sig2) {
    if (document.documentElement.__transition__) return;
    // Rescale outside angles to match the new layout.
    var enterArc,
        exitArc,
        outsideAngle = d3.scale.linear().domain([0, 2*Math.PI]); // [0, 2 * Math.PI]
        var arc2 = d3.svg.arc()
    .startAngle(function(d) { return d.x; })
    .endAngle(function(d) { return d.x + d.dx; })
    .padAngle(.01)
    .padRadius(newradius /3 )
    .innerRadius(newradius)
    .outerRadius(newradius - 40);
    function insideArc(d) {
      return p.key > d.key
          ? {depth: d.depth - 1, x: 0, dx: 0} : p.key < d.key
          ? {depth: d.depth - 1, x: 2 * Math.PI, dx: 0}
          : {depth: 0, x: 0, dx: 2 * Math.PI};
    }
    function outsideArc(d) {
      return {depth: d.depth + 1, x: outsideAngle(d.x), dx: outsideAngle(d.x + d.dx) - outsideAngle(d.x)};
    }
    center.datum(root);
    // When zooming in, arcs enter from the outside and exit to the inside.
    // Entering outside arcs start from the old layout.
    if (root === p) enterArc = outsideArc, exitArc = insideArc, outsideAngle.range([p.x, p.x + p.dx]);
    path = path.data(partition.nodes(root).slice(1), function(d) { return d.key; });
    // When zooming out, arcs enter from the inside and exit to the outside.
    // Exiting outside arcs transition to the new layout.

    //Modifying this so that they get sucked into the clicked arc
    if (root !== p) enterArc = insideArc, exitArc = outsideArc, outsideAngle.range([p.x, p.x + p.dx]);
    
      if (root == p)  {
        d3.transition().duration(d3.event.altKey ? 7500 : sig2).each(function() {
      path.exit().transition()
          .style("fill-opacity", function(d) { return d.depth === 1 + (root === p) ? 1 : 0; })
          .attrTween("d", function(d) { return arcTween.call(this, exitArc(d)); })
          .remove();
      path.enter().append("path")
          .style("fill-opacity", function(d) { return d.depth === 2 - (root === p) ? 1 : 0; })
          .style("fill", function(d) { return d.fill; }) //'url(#grad)')//
          .on("click", zoomIn)
          .each(function(d) { this._current = enterArc(d); });
          path.transition()
          .style("fill-opacity", 1)
          //.attr("d",arc2)
          .attrTween("d", function(d) { return arcTween.call(this, updateArc(d)); })
          .transition().duration(sig).attr("d",arc2);

      });
        } 
      else {
        path.transition().duration(2000).attr("d",arc);
        d3.transition().duration(1500).transition().duration(d3.event.altKey ? 7500 : 500).each(function() {
      path.exit().transition()
          .style("fill-opacity", function(d) { return d.depth === 1 + (root === p) ? 1 : 0; })
          .attrTween("d", function(d) { return arcTween.call(this, exitArc(d)); })
          .remove();
      path.enter().append("path")
          .style("fill-opacity", function(d) { return d.depth === 2 - (root === p) ? 1 : 0; })
          .style("fill", function(d) { return d.fill; }) //'url(#grad)')//
          .on("click", zoomIn)
          .style("pointer-events","auto")
          .on("mouseover",function(o){
        var h = d3.selectAll(".node").filter(function(e) {return e.comp == o.parent.id && e.suggest != 0 ? this : null;}).node();
        var f = h.__data__;
        if (g.time != null) {
     div.html('<b>Most central article for this cluster:</b><br/><a href=' + f.url + '><b>' + f.title + '</b></a><br/><br/><b>' + f.source  + '   ' + f.time.substr(5,2) + '/' + f.time.substr(8,2) + ' ' + f.time.substr(11,5) + '</b><br/><br/>' + f.summary);}
    else { div.html('<b>Most central article for this cluster:</b><br/><a href=' + f.url + '><b>' + f.title + '</b></a><br/><br/><b>' + f.source  + '</b><br/><br/>' + f.summary);}

        
      })
          .each(function(d) { this._current = enterArc(d); });
        path.transition().style("fill-opacity", 1) //.duration(2000).attr("d",arc2).transition()
          //.attr("d",arc2)
          .attrTween("d", function(d) { return arcTween.call(this, updateArc(d)); });
           });
      }

          //.each(function(d) { this._current = updateArc(d); });

    
            }//end of zoom function


  function zoomSuggest() {
    suggestt = 50;
    var p = d3.selectAll("path").filter(function(d){return d.id == 1? this:null;}).node().__data__;
        if (p.depth > 1) p = p.parent;
    if (!p.children) return;
    
  var newradius = 5*radius;
//partition.size([1/6* Math.PI, radius]);
    zoom(p, p,newradius,1250,750);
    path.style("pointer-events","none");



   chart.transition().duration(750).transition().duration(1250).attr("transform", "translate(" + (-radius*3) + "," + centery + ")")
   center.transition().duration(750).transition().duration(1250).attr("rx", newradius).attr("ry",newradius)
   div.transition().duration(750).transition().duration(1250).style("left","50px").style("top", (centery + 100) + "px");//style("pointer-events","none") // add suggestion here
   //d3.select("#orderdiv").transition().duration(2000).transition().duration(500).style("opacity",1);

    var g = d3.selectAll("circle").filter(function(e) {return e.suggest==1? this : null;}).node().__data__;//viscenter(p.id);//
    recto.transition().duration(2000).style("opacity",0)  // filter(function(e) {return e.id != p.id ? this : null;})
    //div.transition().duration(500).style("opacity",0);
    var h = d3.selectAll("circle").filter(function(e) {return e.suggest==1?  this : null;}).node()
    var cir = d3.selectAll(".node").filter(function(d) {return (d.suggest <= root.comps) && (d.suggest != 0) ? this : null;});
    var circir = d3.selectAll("circle").filter(function(d) {return (d.suggest <= root.comps) && (d.suggest != 0)? this : null;});
    var texts = d3.selectAll("#nodetext").filter(function(d) {return (d.suggest <= root.comps) && (d.suggest != 0) ? this : null;});
    var rects = d3.selectAll("#rect").filter(function(d) {return (d.suggest <= root.comps) && (d.suggest != 0) ? this : null;});

    //d3.selectAll("circle").style("stroke","#fff"); 
    if (g.time != null) {

    div.html('<a href=' + g.url + '><b>' + g.title + '</b></a><br/><br/><b>' + g.source  + '   ' + g.time.substr(5,2) + '/' + g.time.substr(8,2) + ' ' + g.time.substr(11,5) + '</b><br/><br/>' + g.summary)}
    else {div.html('<a href=' + g.url + '><b>' + g.title + '</b></a><br/><br/><b>' + g.source  + '</b><br/><br/>' + g.summary)}
    d3.selectAll("#image").attr("xlink:href",g.images);
     //d3.select(h).style("stroke","#2b2b2b"); 

    div.transition().duration(500).transition().duration(1500).style("left","50px").style("top", (centery + 50) + "px");//style("pointer-events","none") // add suggestion here
    rects.attr("xlink:href",function(d){return d.url;}).style("pointer-events","auto");
    //cir.style("pointer-events","auto");
    d3.selectAll("circle").filter(function(d) {return (d.suggest > root.comps) || d.suggest ==0  ? this : null;}).style("pointer-events","none").transition().duration(2000).style("opacity",0);
    //d3.selectAll(".link").filter(function(d) {return p.id != d.source.comp ? this : null;}).transition().duration(1000).style("opacity",0);
    d3.selectAll(".link").transition().duration(1000).style("opacity",0);
    topichead.style("border-color",color(p.id))
        .style("font-color",color(p.id))
        .html('<br/><h1>Suggestions</h1><br/>').transition().duration(500).transition().duration(1500).style("opacity",1);
  d3.selectAll("#bubble").transition().duration(500).transition().duration(1500).style("opacity",1);
    detail = p.id;
    texts.transition().duration(500).transition().duration(1500)
            .style("opacity",1)
            .attr("dx", function (d) { return computeTextRotation(d) > 180 ? "-23" : "23"; }) // margin
            .attr("dy", ".35em")
            //.attr("transform", function(d) { return "translate(" + arc.centroid(d) + ")rotate(" + computeTextRotation(d) + ")"; })
            .attr('text-anchor', function (d) { return computeTextRotation(d) > 180 ? "end" : "start"; });

          cir.transition().duration(500).transition().duration(1500).attr("transform", function(d) {return around_suggest(d,centerx,centery,radius,newradius,500,clock);})
     circir.transition().duration(500).transition().duration(1500).attr("r",function(d){return 2*nodefac*(d.deg)+2;});

  } // end of zoomsuggest

d3.select('#order').on('change', function() {
      var cir = d3.selectAll(".node").filter(function(d) {return detail == d.comp ? this : null;});
      //var circir = d3.selectAll("circle").filter(function(d) {return detail == d.comp ? this : null;});
      if (this.value == "time") {
        clock = 1;
        time2.transition().duration(2000).style("opacity",1);
        time3.transition().duration(2000).style("opacity",1);
        time4.transition().duration(2000).style("opacity",1);
        time5.transition().duration(2000).style("opacity",1);
        time6.transition().duration(2000).style("opacity",1);
              }

      else if (this.value == "deg") {
        clock = 2;
        time2.transition().duration(2000).style("opacity",0);
        time3.transition().duration(2000).style("opacity",0);
        time4.transition().duration(2000).style("opacity",0);
        time5.transition().duration(2000).style("opacity",0);
        time6.transition().duration(2000).style("opacity",0);}


        cir.transition().duration(500).transition().duration(1500).attr("transform", function(d) {return around(d,centerx,centery,radius,newradius,500,clock);})
     //circir.transition().duration(500).transition().duration(1500).attr("r",function(d){return 2*d.deg+6;});

      
             })


});
function key(d) {
  var k = [], p = d;
  while (p.depth) k.push(p.id), p = p.parent;
  return k.reverse().join(".");
}
function fill(d) {
  var p = d;
  while (p.depth > 1) p = p.parent;
  var c = d3.lab(color(p.id));//function(p) {return p.id == 50? color(p.id):'#2b2b2b';});
  //c.l = luminance(d.sum);
  return c;
}
function arcTween(b) {
  var i = d3.interpolate(this._current, b);
  this._current = i(0);
  return function(t) {
    return arc(i(t));
  };
}
function updateArc(d) {
  return {depth: d.depth, x: d.x, dx: d.dx};
}
d3.select(self.frameElement).style("height", margin.top + margin.bottom + "px");


var detail = 0;

var worksurl,
customsearchurl,
grewsalerturl,
registerurl;


var div = d3.select("body").append("centtext")
    .attr("class", "centtext")
    .style("left",centerx - radius/2 + "px")
    .style("top",centery - radius/3 + "px" )
    .style("width", radius + "px")
    .style("opacity", 1e-6)
    .html(init_message);
   // .html('<h2>Welcome to Graphite</h2><p>Welcome to Graphite! Graphite is a tool that helps you optimize the way you find and read news. It graphically clusters news articles by similarity, allowing you to get an instant overview over their structure and interact with news in a completely new way.</p><p>On top of that, Graphite produces a list of reading suggestions that lets you maximze the breadth of your reading. For this it follows a simple recipe: Pick that article from the largest topic cluster (i.e. the hottest topic) that has the most overlap with the other articles from that cluster, then do the same for the second largest cluster, etc. In this way, by following the suggestion list, you get the most out of your news, however much time you have to read (click <a href=' + worksurl + '>here</a> to learn more about how Graphite works.)</p>                <p>Graphite can work its magic on any bunch of articles that you feed it. On this page you see its ouput on a selection of about 600 recently published articles from around 40 global newspapers. Make the most of Graphite by filtering the above graph, starting your own <a href=' + customsearchurl 
     //               +       '>custom search</a>, creating a <a href=' + grewsalerturl + '>mail alert</a> and managing your searches with a <a href=' + registerurl + '>Graphite-profile</a>.</p>'); 
var topichead = d3.select("body").append("titul")
    .attr("class", "titul")
    .style("opacity", 1e-6);

    

 var defs = svg.append('svg:defs');
  defs.append('svg:pattern')
                .attr('id', 'tile-ww')
                .attr('patternUnits', "objectBoundingBox")//'userSpaceOnUse')
                //.attr('viewBox', '10 10 200 200')
                //.attr('preserverAspectRatio','xMinYMin')
                .attr('width', '100%')
                .attr('height', '100%')
                .attr('x', 0)
                .attr('y', 0)
                //.attr('dx','400px')
                 // .append('div')
                 // .attr("width","100px")
                 // .attr('height','100px')
                .append('image')
                .attr('id', 'image')
                .attr('x', 0)
                .attr('y', 0)
                .attr('width', '200')
                .attr('height', '200')
                // .attr('object-fit', 'contain')
                //.attr("type", "image/svg+xml");
                .attr('preserveAspectRatio',"xMidYMid slice");







d3.json(json, function(error, graph) {
  if (error) throw error;
    

  force
      .nodes(graph.nodes)
      .links(graph.links)
      .start();
    

 var timer = setTimeout(init_positions,2000)
    
  /*var node_positions = force.nodes()*/
  var link = svg.selectAll(".link")
      .data(graph.links)
    .enter().append("line")
      .attr("class", "link")
      .style("stroke-width", 1.5);//function(d) { return 2*Math.sqrt(d.weight); });
     


    //  .on("dblclick", connectedNodes); 
var toggle = 0;
var linkedByIndex = {};
for (i = 0; i < graph.nodes.length; i++) {
    linkedByIndex[i + "," + i] = 1;
};
graph.links.forEach(function (d) {
    linkedByIndex[d.source.index + "," + d.target.index] = 1;
});
//This function looks up whether a pair are neighbours
function neighboring(a, b) {
    return linkedByIndex[a.index + "," + b.index];
}
function connectedNodes() {
  if (toggle == 0) {
        //Reduce the opacity of all but the neighbouring nodes
        d = d3.select(this).node().__data__;
        circle.style("opacity", function (o) {
            return neighboring(d, o) | neighboring(o, d) ? 1 : 0.1;
        });
        link.style("opacity", function (o) {
            return d.index==o.source.index | d.index==o.target.index ? 1 : 0.1;
        });
        //Reduce the op
        toggle = 1;
    } else {
        //Put them back to opacity=1
        circle.style("opacity", 1);
        link.style("opacity", 1);
        toggle = 0;
    }
    
}
  
  var bubble = svg.append("ellipse")
      .attr("transform","translate(150," + (centery - 130) + ")")
      .attr("fill","url(#tile-ww)")
        .attr("id","bubble")
        .attr("rx", "100px")
        .attr("ry","100px")
        .style("opacity",0);



var gotit = d3.select("body")
    .append("button")
    .attr("class", "btn btn-primary btn-sm")
    .attr("id","gotit")
    .attr("type","button")
    .style("opacity", 1e-6)
    .style("left",centerx - radius/10 + "px")
    .style("top",centery + 8*radius/10 + "px" )
    .text("Got it")
    .on("click", gotitclick);

  function gotitclick() { 
      d3.selectAll("path").style("pointer-events","auto");
      chart.transition().duration(1000).style("opacity",1);
      node.style("pointer-events","auto").transition().duration(1000).style("opacity",1);
      d3.selectAll("circle").style("pointer-events","auto").transition().duration(1000).style("opacity",1);
      link.transition().duration(1000).style("opacity",1);
      d3.select('#gotit').style("pointer-events","auto").transition().duration(1000).style("opacity",0);
        d3.select("#helper").transition().duration(3000).style("opacity",0.6);
  d3.select("#suggestbutton").transition().duration(3000).style("opacity",0.6).style("pointer-events","auto");
  d3.select("#sharer").transition().duration(3000).style("opacity",0.6).style("pointer-events","auto");
  }

  var node = svg//.append("g")  
  .selectAll(".node")
    .data(graph.nodes)
  .enter().append("g")
  .attr("class", "node")
  .style("pointer-events","none")
    .call(force.drag)
    .on("mouseover",function(d){if (detail != 0){
      d3.selectAll("circle").style("fill", function(d) { return color(d.comp); });
                  if (d.time != null) {div.html('<a href=' + d.url + '><b>' + d.title + '</b></a><br/><br/><b>' + d.source  + '   ' + d.time.substr(5,2) + '/' + d.time.substr(8,2) + ' ' + d.time.substr(11,5) + '</b><br/><br/>' + d.summary)}
                    else {div.html('<a href=' + d.url + '><b>' + d.title + '</b></a><br/><br/><b>' + d.source  + '</b><br/><br/>' + d.summary)}
      var h = d3.selectAll("circle").filter(function(e) {return d.title == e.title ? this : null;}).node();
      d3.select(h).style("fill","#2b2b2b");
      var cir = d3.selectAll(".node").filter(function(d) {return detail == d.comp ? this : null;});
        cir.style("opacity", function (o) {
            return neighboring(d, o) | neighboring(o, d) ? 1 : 0.3;});
      d3.select("#image").attr('xlink:href', d.images);
               }

       }
        )
        .on("mouseout",function(){
          if (detail != 0) {
            var cir = d3.selectAll(".node").filter(function(d) {return detail == d.comp ? this : null;});
            cir.style("opacity", 1);
          //var cirlink = d3.selectAll(".link").filter(function(d) {return e.comp == d.source.comp ? this : null;});
          //cirlink.style("opacity",1).style("stroke-width","1.5px");
                          }
        });

    node.append("a").attr("id", "rect").style("pointer-events","none")
        .append("rect")
        .attr("x", "10px")
        .attr("y", "-0.4em")
        .attr("width", function(d){return d.title.length*10 + "px";})
        .style("opacity",0)
        //.style("pointer-events","none")
        .attr("height", "1em")  
        .attr("fill", "white");
    

node.append("text").attr("id","nodetext").attr("x", 12)
        .attr("y", '0.35em')
        .style("opacity",0).style({"text-baseline":"left","text-anchor":"left","width":"40px"}).html(function(d){return d.title;});

node.append("circle")
      .style("pointer-events","none")
      .style("opacity",function(d){return d.single ==1 ? 0:1;})
        .attr("r", function(d) {return d.deg*nodefac+6;})//(d.suggest <= 15) && (d.suggest != 0) ? 10 :6;})
        //.style("pointer-events",function(d){return (d.single == 1)? "none":"auto";}) 
        .style("fill", function(d) { return color(d.comp); })
        .style("stroke",function(d) {return (d.suggest <= graph.graph.comps) && (d.suggest != 0) ? '#2b2b2b' :'#fff';})
        .style("opacity",function(d){return (d.single == 1)? 0:1;})
        .on("mouseover", function(d) {
          d3.selectAll("circle").style("fill", function(d) { return color(d.comp); });//"stroke",function(d) {return (d.suggest <= graph.graph.comps) && (d.suggest != 0) ? '#2b2b2b' :'#fff';}); 
                 if (d.time != null) {div.html('<a href=' + d.url + '><b>' + d.title + '</b></a><br/><br/><b>' + d.source  + '   ' + d.time.substr(5,2) + '/' + d.time.substr(8,2) + ' ' + d.time.substr(11,5) + '</b><br/><br/>' + d.summary)}
                    else {div.html('<a href=' + d.url + '><b>' + d.title + '</b></a><br/><br/><b>' + d.source  + '</b><br/><br/>' + d.summary)}
                  d3.select(this).style("fill","#2b2b2b"); 
              })
        .on("click", function(d){return window.open(d.url, '_blank');})
        .on("mouseout",function(){
          if (detail != 0) {
          //e = d3.select(this).node().__data__;
          var cir = d3.selectAll(".node").filter(function(d) {return detail == d.comp ? this : null;});
          cir.style("opacity", 1);
          //var cirlink = d3.selectAll(".link").filter(function(d) {return e.comp == d.source.comp ? this : null;});
          //cirlink.style("opacity",1).style("stroke-width","1.5px");
                            }
        });


function calc_pos(d){
  var x = node.filter(function(e) {return e.comp < d.comp ? this : null;}).size()+node.filter(function(e) {return e.comp == d.comp ? this : null;}).size()/2,
  y = d3.selectAll("circle").size(),
    f = node.filter(function(e) {return e.comp == d.comp? this : null;}).node().__data__; //&& e.suggest != 0 THIS NEEDS TO GO BACK IN!
   if (0<= x/y < 0.25) {var T = Math.tan(2*Math.PI*x/y),TT = radius*2/Math.sqrt(1+Math.pow(T,2)); return [-TT*T+d.x-f.x,TT+d.y-f.y];}
   else if (0.25 <= x/y< 0.5) {var T = Math.tan(2*Math.PI*x/y-Math.PI),TT = radius*2/Math.sqrt(1+Math.pow(T,2)); return [TT*T+d.x-f.x,-TT+d.y-f.y];}
   else if (0.5 <= x/y< 0.75) {var T = Math.tan(2*Math.PI*x/y),TT = radius*2/Math.sqrt(1+Math.pow(T,2)); return [-TT*T+d.x-f.x,TT+d.y-f.y];}
   else if (0.75 <= x/y< 0.1){var T = Math.tan(2*Math.PI*x/y-3*Math.PI),TT = radius*2/Math.sqrt(1+Math.pow(T,2)); return [-TT*T+d.x-f.x,TT+d.y-f.y];}
   else {var T = Math.tan(2*Math.PI*x/y-3*Math.PI),TT = radius*2/Math.sqrt(1+Math.pow(T,2)); return [TT*T+d.x-f.x,-TT+d.y-f.y];}
}




function init_positions() {
  force.stop();
  //.transition().duration(1000)
  //d3.selectAll("nodetext").transition().duration(2000).attr("transform", function(d) {return "translate(" + (centerx+calc_pos(d)[0]) + "," + (centery+ calc_pos(d)[1]) + ")"; });
  if (custom == 0) {

node.transition().duration(2000).style("opacity",0.3).attr("transform", function(d) {return "translate(" + (centerx+calc_pos(d)[0]) + "," + (centery+ calc_pos(d)[1]) + ")"; });

  link.transition().duration(2000).style("opacity",0.3).attr("x1", function(d) {return centerx+calc_pos(d.source)[0];}) 
        .attr("y1", function(d) {return centery+calc_pos(d.source)[1];})
        .attr("x2", function(d) {return centerx+calc_pos(d.target)[0];})
        .attr("y2", function(d) {return centery+calc_pos(d.target)[1];}); 

      gotit.transition().duration(3000).style("opacity",1);
    d3.select("#helper").transition().duration(3000).style("opacity",0.3);
  d3.select("#suggestbutton").transition().duration(3000).style("opacity",0.3);
  d3.select("#sharer").transition().duration(3000).style("opacity",0.3);
  chart.transition().duration(3000).style("opacity",0.3);
}
  else {
  
    node.style("pointer-events","auto").transition().duration(2000).style("opacity",1).attr("transform", function(d) {return "translate(" + (centerx+calc_pos(d)[0]) + "," + (centery+ calc_pos(d)[1]) + ")"; });
d3.selectAll("circle").style("pointer-events","auto");
  link.transition().duration(2000).style("opacity",1).attr("x1", function(d) {return centerx+calc_pos(d.source)[0];}) 
        .attr("y1", function(d) {return centery+calc_pos(d.source)[1];})
        .attr("x2", function(d) {return centerx+calc_pos(d.target)[0];})
        .attr("y2", function(d) {return centery+calc_pos(d.target)[1];}); 
    d3.selectAll("path").style("pointer-events","auto");
      chart.transition().duration(1000).style("opacity",1);
      d3.select('#gotit').style("pointer-events","auto").transition().duration(1000).style("opacity",0);
        d3.select("#helper").transition().duration(3000).style("opacity",0.6);
  d3.select("#suggestbutton").transition().duration(3000).style("opacity",0.6).style("pointer-events","auto");
  d3.select("#sharer").transition().duration(3000).style("opacity",0.6).style("pointer-events","auto");
    gotit.style("pointer-events","none");}


  div.transition().duration(3000).style("opacity",1);
  
  //d3.selectAll("labels").attr("transform", function(d) {return "translate(" + (500+calc_pos(d)[0]) + "," + (500+ calc_pos(d)[1]) + ")"; });
  //d3.selectAll("nodetext").attr("transform", function(d) { return "translate(" + d.x + "," + d.y + ")"; });
}


           
  force.on("tick", function() {
    link.attr("x1", function(d) { return d.source.x; })
        .attr("y1", function(d) { return d.source.y; })
        .attr("x2", function(d) { return d.target.x; })
        .attr("y2", function(d) { return d.target.y; });
    node.attr("transform", function(d) {return "translate(" + d.x + "," + d.y + ")"; });

                  });//end of force.on
    
    

    
  var toggle = 0;
                                               
});
//})();    