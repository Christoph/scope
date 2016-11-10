//(function(){
//var this_js_script = $('script[src*=somefile]');

var width = window.innerWidth,

height = 1300;

var centerx = width/2,
centery = 500;

var detail = 0;

var worksurl,
customsearchurl,
grewsalerturl,
registerurl;

var svg = d3.select("body").append("svg");//.attr("preserveAspectRatio","xMidYMid slice").attr("viewBox", "0 0 1024 768")

var select = d3.select("body").append("div").text("Sort by: ").attr("id","orderdiv").append("select").attr("id","order");//.on("change", change);
	select.append("option").text("Centrality").attr("value","deg");
	select.append("option").text("Time").attr("value","time");    
	select.append("option").text("Source (to come)"); // Data join
	select.append("option").text("Sentimental analysis (to come)"); 

var radius = 230//Math.min(width/4,200), //Math.min(margin.top, margin.right, margin.bottom, margin.left);
	margin = {top: 500, right: 500, bottom: 500, left: 500};//{top: 200, right: (width-3*radius)/2, bottom: 300, left: (width-3*radius)/2};

d3.select(self.frameElement).style("height", margin.top + margin.bottom + "px");


var div = d3.select("body").append("centtext")
	.attr("class", "centtext")
	.style("left",centerx - radius/2 - 5+ "px")
	.style("top",centery - radius/3 + "px" )
	//.style("width", radius + "px")
	.style("opacity", 1e-6)
	.html(init_message);
 

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

var color = d3.scale.category20();

var force = d3.layout.force()
	.charge(function(){return width <= 800? -20 : -80;})
	.linkDistance(function(){return width <= 800? linkdist/2 : linkdist;})
	.size([width, height]);

var hue = d3.scale.category20();
// var luminance = d3.scale.sqrt()
//     .domain([0, 1e6])
//     .clamp(true)
//     .range([90, 20]);
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
  var zoomfac = 2,
		clock = 2,
		suggestt = 0;

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
	  //.style("stroke","#2b2b2b")
	  .style("fill","#ffffff")
	  .on("click", zoomOut);

  center.append("title")
	  .text("zoom out");
  var path = chart.selectAll("path")
	  	.data(partition.nodes(root).slice(1))
		.enter().append("path")
		.attr("class","path")
	  	.attr("d", arc)
	  	.style("fill", function(d) { return d.fill; })
	 	.style("pointer-events","none")
	  	.each(function(d) { this._current = updateArc(d); })
	  	.on("click", function(p){if (detail == 0) {return zoomIn(p);} else {return zoomOut(p);}})
	  	.on("mouseover",function(o){
			if (detail == 0) {
			var h = d3.selectAll(".node").filter(function(e) {return e.comp == o.parent.id && e.suggest != 0 ? this : null;}).node();
			var g = d3.selectAll("circle").filter(function(e) {return e.comp == o.parent.id && e.suggest != 0 ? this : null;}).node();
			d3.selectAll("circle").style("fill", function(d) { return color(d.comp); });
	  		d3.select(g).style("fill","#2b2b2b");
			var f = h.__data__;
			if (f.time != null) {
				div.html('<u align="center">Central cluster article:</u><br/><br/><a href=' + f.url + '>' + f.title + '</a><br/><br/>' + f.source  + '   ' + f.time.substr(5,2) + '/' + f.time.substr(8,2) + ' ' + f.time.substr(11,5) + '</><br/><br/>' + f.summary);
					}
			else { 
				div.html('<u align="center">Central cluster article:</u><br/><br/><a href=' + f.url + '><b>' + f.title + '</b></a><br/><br/><b>' + f.source  + '</b><br/><br/>' + f.summary);
					}
			
	  			}
	  		});

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
		.html('<span class="glyphicon glyphicon-star" aria-hidden="true"></span>')
		.on("click",function() {
			if (suggestt == 50) {
				
				return zoomOut(root);}
			else {return zoomSuggest();}});

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

	var recto = chart.selectAll("text")
	  .data(partition.nodes(root).slice(1))
	.enter().append("text")
	.attr("dx", function (d) { return computeTextRotation(d) > 180 ? "-23" : "23"; }) // margin
	.attr("dy", ".35em")
	.attr("transform", function(d) { return "translate(" + arc.centroid(d) + ")rotate(" + computeTextRotation(d) + ")"; })
		.attr('text-anchor', function (d) { return computeTextRotation(d) > 180 ? "end" : "start"; })
	.html(function(d) { return d.children ? d.name:null; });

	function computeTextRotation(d) {
  var ang = (d.x + d.dx/2-Math.PI/2)/ Math.PI*180; // add +1/8*Math.PI in case you open up the initial circle
		return (ang > 90) ? 180 + ang : ang;

	}

	var newradius = 5*radius;
	var radiansss = 1.5*height/newradius+ 0.75*height/newradius;
	var time6 = svg.append("text")
		  .attr("class","tim")
		  .attr("x", -3*radius + Math.cos(0.12*radiansss)*newradius*1.06)
		  .attr("y",centery + Math.sin(0.12*radiansss)*newradius*1.06)
		  .html('')
		  .style("opacity",0)
		  .style({"text-baseline":"right","text-anchor":"right"})
		  .attr("transform", function(d) { return "rotate(" + 0.12*radiansss/Math.PI*180 + ")"; });

	var time5 = svg.append("text")
		.attr("class","tim")
		.attr("x", -3*radius + Math.cos(0.06*radiansss)*newradius*0.98)
		.attr("y",centery + Math.sin(0.06*radiansss)*newradius*0.98)
		.html('')
		.style("opacity",0)
		.style({"text-baseline":"right","text-anchor":"right","width":"40px"})
		.attr("transform", function(d) { return "rotate(" + 0.06*radiansss/Math.PI*180 + ")"; })

	var time4 = svg.append("text")
		.attr("class","tim")
		.attr("x", -3*radius + Math.cos(0*radiansss)*newradius*0.92)
		.attr("y",centery)
		.html('no timestamp')
		.style("opacity",0)
		.style({"text-baseline":"right","text-anchor":"right","width":"40px"})
		.attr("transform", function(d) { return "rotate(" + 0*radiansss/Math.PI*180 + ")"; })
	
	var time3 = svg.append("text")
		.attr("class","tim")
		.attr("x", -3*radius + Math.cos(-0.075*radiansss)*newradius*0.87)
		.attr("y",centery + Math.sin(-0.075*radiansss)*newradius*0.87)
		.html('')
		.style("opacity",0)
		.style({"text-baseline":"right","text-anchor":"right","width":"40px"})
		.attr("transform", function(d) { return "rotate(" + -0.075*radiansss/Math.PI*180 + ")"; })
	
	var time2 = svg.append("text")
		.attr("class","tim")
		.attr("x", -3*radius + Math.cos(-0.15*radiansss)*newradius*0.86)
		.attr("y",centery + Math.sin(-0.15*radiansss)*newradius*0.86)
		.html('')
		.style("opacity",0)
		.style({"text-baseline":"right","text-anchor":"right","width":"40px"})
		.attr("transform", function(d) { return "rotate(" + -0.15*radiansss/Math.PI*180 + ")"; })
	  //d3.selectAll("text").attr("transform","rotate(45)");




	function zoomIn(p) {
		if (p.depth > 1) p = p.parent;
		if (!p.children) return;
		detail = p.id;
		var newradius = 5*radius;
		zoom(p, p,newradius,1250,750);

		var h = d3.selectAll("circle").filter(function(e) {return e.comp == p.id && e.suggest != 0 ? this : null;}).node(),
			g = h.__data__,
			cir = d3.selectAll(".node").filter(function(d) {return p.id == d.comp ? this : null;}),
			circir = d3.selectAll("circle").filter(function(d) {return p.id == d.comp ? this : null;}),
			texts = d3.selectAll("#nodetext").filter(function(d) {return p.id == d.comp ? this : null;}),
			rects = d3.selectAll("#rect").filter(function(d) {return p.id == d.comp ? this : null;});
	 
		
		//Zomming
		cir.transition().duration(500).transition().duration(1500).attr("transform", function(d) {return around(d,centerx,centery,radius,newradius,500,clock);})
		//circir.transition().duration(500).transition().duration(1500).attr("r",function(d){return 2*nodefac*(d.deg)+2;});
 	   	chart.transition().duration(750).transition().duration(1250)
	   			.attr("transform", "translate(" + (-radius*3) + "," + centery + ")")
	   	center.transition().duration(750).transition().duration(1250)
	   			.attr("rx", newradius).attr("ry",newradius)
		//Stuff for big circle
		d3.select("#orderdiv")
				.transition().duration(1500)
				.transition().duration(500)
	   			.style("opacity",1);
	  	d3.selectAll("#image")
	   			.attr("xlink:href",g.images);
	   	rects.attr("xlink:href",function(d){return d.url;})
				.style("pointer-events","auto");
		if (g.time != null) {
		  div.html('<a href=' + g.url + '>' + g.title + '</a><br/><br/>' + g.source  + '   ' + g.time.substr(5,2) + '/' + g.time.substr(8,2) + ' ' + g.time.substr(11,5) + '<br/><br/>' + g.summary);
							}
		else {
		  div.html('<a href=' + g.url + '>' + g.title + '</a><br/><br/>' + g.source  + '<br/><br/>' + g.summary)
		
					}
		div
			   			.style("opacity",0)
			   			.style("height","450px")
			   			.transition().duration(1500)
			   			// .transition().duration(1250)
			   			.style("left","50px")
			   			.style("top", (centery + 50) + "px")
			   			.transition().duration(500)
			   			.style("opacity",1)
			   			;
		// div.transition().duration(500).transition().duration(1500)
		// 	  .style("left","50px")
		// 	  .style("top", (centery + 50) + "px")
		// 	  .style("overflow","visible");

		if (clock == 0 && typeof p.timeinf == "object") {}
		else if (clock == 1 && typeof p.timeinf == "object") { 
			time2.html(p.timeinf[0]).transition().duration(1500).transition().duration(500).style("opacity",1);
			time3.html("-" + p.timeinf[1]).transition().duration(1500).transition().duration(500).style("opacity",1);
			time4.html("-" + p.timeinf[2]).transition().duration(1500).transition().duration(500).style("opacity",1);
			time5.html("-" + p.timeinf[3]).transition().duration(1500).transition().duration(500).style("opacity",1);
			time6.html("-" + p.timeinf[4]).transition().duration(1500).transition().duration(500).style("opacity",1);
		}
		 //end if clock==1 

		else if (clock == 2 && typeof p.timeinf == "object") {
		  	time2.html(p.timeinf[0]).transition().duration(2000).style("opacity",0);
			time3.html("-" + p.timeinf[1]).transition().duration(2000).style("opacity",0);
			time4.html("-" + p.timeinf[2]).transition().duration(2000).style("opacity",0);
			time5.html("-" + p.timeinf[3]).transition().duration(2000).style("opacity",0);
			time6.html("-" + p.timeinf[4]).transition().duration(2000).style("opacity",0);
		} 
		//Others
		topichead
				.html('<h1>'+ p.name +'</h1><br/><p># of articles: '+ cir.size()+ '<p>Clustering: ' + p.clustering + '%')
				.transition().duration(1500)
				.transition().duration(500)
				.style("opacity",1);

		d3.select("#suggestbutton").style("pointer-events","none");
		d3.selectAll("path").style("pointer-events","none");
	   	recto.transition().duration(2000)
	   			.style("opacity",0); 
		d3.selectAll("circle").filter(function(d) {return p.id != d.comp ? this : null;})
				.style("pointer-events","none")
				.transition().duration(2000)
				.style("opacity",0);
		d3.selectAll(".link").transition().duration(1000)
				.style("opacity",0);
		d3.selectAll("#bubble")
				.transition().duration(1500)
				.transition().duration(500)
	  			.style("opacity",1);
		texts.transition().duration(500).transition().duration(1500)
				.style("opacity",1)
				.attr("dx", function (d) { return computeTextRotation(d) > 180 ? "-23" : "23"; }) 
				.attr("dy", ".35em")
				.attr('text-anchor', function (d) { return computeTextRotation(d) > 180 ? "end" : "start"; });





  		} // end of zoomin function

	function movetocenter(g,d,zoomfac,centerx,centery){
		return "translate(" + (centerx+zoomfac*(d.x-g.x)) + "," + (centery+zoomfac*(d.y-g.y)) + ")";
		}
	function movetocenter_link(g,d,zoomfac,center){
		return center+zoomfac*(d-g);
		}

  	function aroundtheclock(d,centerx,centery,radius){
		var radians = d.time_pos*Math.PI/180 + Math.PI/2;
		return "translate(" + (centerx + Math.cos(radians)*radius) + "," + (centery + Math.sin(radians)*radius) + ")";
		}

	function around(d,centerx,centery,radius,newradius,height,clock){
	  	if (clock == 1) {var radians = 1.5*d.time_pos*height/(360*newradius)+ -0.75*height/newradius; }//+ Math.PI/2-height/(4*Math.PI*newradius);
	  	if (clock == 2) {var radians = 1.5*d.deg_pos*height/(360*newradius)+ -0.75*height/newradius; }
		return "translate(" + (-3*radius + Math.cos(radians)*newradius) + "," + (centery + Math.sin(radians)*newradius) + ")rotate(" + radians/Math.PI*180 + ")";
		}

	function around_suggest(d,centerx,centery,radius,newradius,height,clock){
	  	if (clock == 1) {var radians = 1.5*d.time_pos*height/(360*newradius)+ -0.75*height/newradius; }//+ Math.PI/2-height/(4*Math.PI*newradius);
	  	if (clock == 2) {var radians = 1.5*d.suggest/root.comps*360*height/(360*newradius)+ -0.75*height/newradius; }
		return "translate(" + (-3*radius + Math.cos(radians)*newradius) + "," + (centery + Math.sin(radians)*newradius) + ")rotate(" + radians/Math.PI*180 + ")";
		}

  	function aroundtheclock_link(d,center,radius,bin){
		var radians = d.time_pos*Math.PI/180 + Math.PI/2;
		return center;
		} 

	function calc_pos(d){
		var x = d3.selectAll("circle").filter(function(e) {return e.comp < d.comp ? this : null;}).size()+d3.selectAll("circle").filter(function(e) {return e.comp == d.comp ? this : null;}).size()/2,
		 	y = d3.selectAll("circle").size(),
			f = d3.selectAll("circle").filter(function(e) {return e.comp == d.comp? this : null;}).node().__data__;
		if (0<= x/y < 0.25) {var T = Math.tan(2*Math.PI*x/y),TT = radius*2/Math.sqrt(1+Math.pow(T,2)); return [-TT*T+d.x-f.x,TT+d.y-f.y];}
		   else if (0.25 <= x/y< 0.5) {var T = Math.tan(2*Math.PI*x/y-Math.PI),TT = radius*2/Math.sqrt(1+Math.pow(T,2)); return [TT*T+d.x-f.x,-TT+d.y-f.y];}
		   else if (0.5 <= x/y< 0.75) {var T = Math.tan(2*Math.PI*x/y),TT = radius*2/Math.sqrt(1+Math.pow(T,2)); return [-TT*T+d.x-f.x,TT+d.y-f.y];}
		   else if (0.75 <= x/y< 0.1){var T = Math.tan(2*Math.PI*x/y-3*Math.PI),TT = radius*2/Math.sqrt(1+Math.pow(T,2)); return [-TT*T+d.x-f.x,TT+d.y-f.y];}
		   else {var T = Math.tan(2*Math.PI*x/y-3*Math.PI),TT = radius*2/Math.sqrt(1+Math.pow(T,2)); return [TT*T+d.x-f.x,-TT+d.y-f.y];}
		}

  	function zoomOut(p) {
		detail = 0;
		if (!p.parent) return;
		d3.selectAll("path").filter(function(d){return d.id == 50? this:null;}).style("stroke","#fff");
		zoom(p.parent, p,radius,2000,150);
		d3.select("#suggestbutton")
				.style("pointer-events","auto");
		
	   	chart
	   			.transition().duration(2000)
	   			.attr("transform", "translate(" + centerx + "," + centery + ")")
	   	center
	   			.transition().duration(2000)
	   			.attr("rx", radius)
	   			.attr("ry",radius)
	   	div
	   			.style("height","250px")
	   			.transition().duration(500)
	   			.style("opacity",0)
	   			.style("pointer-events","auto")
	   			.transition().duration(1500)
	   			.style("left",centerx - radius/2 + "px")
	   			.style("top",centery - radius/3 + "px" )
	   			.transition().duration(500)
	   			.style("opacity",1);
	   	d3.select("#orderdiv")
	   			.transition().duration(2000)
	   			.style("opacity",0);
		recto
				.transition().duration(2000)
				.style("opacity",1);

		if (clock ==1) {
				time2.transition().duration(200).style("opacity",0);
				time3.transition().duration(200).style("opacity",0);
				time4.transition().duration(200).style("opacity",0);
				time5.transition().duration(200).style("opacity",0);
				time6.transition().duration(200).style("opacity",0);
			}
		
		if (suggestt == 0){
			var cir = d3.selectAll(".node").filter(function(d) {return p.id == d.comp ? this : null;});
			var circir = d3.selectAll("circle").filter(function(d) {return p.id == d.comp ? this : null;});
		   	d3.selectAll("circle").filter(function(d) {return p.id != d.comp ? this : null;}).style("pointer-events","auto")
		   			.transition().duration(2000)
		   			.style("opacity",1);//.style("stroke",function(d) {return (d.suggest <= root.comps) && (d.suggest != 0) ? '#2b2b2b' :'#fff';});       

	  		}
		  else if (suggestt == 50){
			var cir = d3.selectAll(".node").filter(function(d) {return (d.suggest <= root.comps) && (d.suggest != 0) ? this : null;});
			var circir = d3.selectAll("circle").filter(function(d) {return (d.suggest <= root.comps) && (d.suggest != 0)? this : null;});
			d3.selectAll("circle").style("pointer-events","auto").transition().duration(2000).style("opacity",1);      
			suggestt = 0;
			}
		cir
				.transition().duration(2000)
				.attr("transform", function(d){ return "translate(" + (centerx+calc_pos(d)[0]) + "," + (centery+ calc_pos(d)[1]) + ")";})
				.style("pointer-events","none");
		circir
				.transition().duration(2000)
				.attr("r",function(d){return nodefac*d.deg+6;});
		d3.selectAll("#rect")
				.style("pointer-events","none");
		d3.selectAll("#nodetext")
				.transition().duration(2000)
				.style("opacity",0);
		d3.selectAll(".link")
				.transition().duration(2000)
				.style("opacity",1)
		d3.selectAll(".link").filter(function(d) {return p.id == d.source.comp ? this : null;})
				.attr("stroke-width", "1.5px" )
				.transition().duration(2000)
				.transition().duration(500)
				.style("opacity",1)
				.attr("x1", function(d) {return centerx+calc_pos(d.source)[0];}) 
				.attr("y1", function(d) {return centery+calc_pos(d.source)[1];})
				.attr("x2", function(d) {return centerx+calc_pos(d.target)[0];})
				.attr("y2", function(d) {return centery+calc_pos(d.target)[1];})
			 
		topichead
				.transition().duration(200)
				.style("opacity",0);
		d3.select("#bubble")
				.transition().duration(200)
				.style("opacity",0);

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
		  		.attr("class","path")
			  .style("fill-opacity", function(d) { return d.depth === 2 - (root === p) ? 1 : 0; })
			  .style("fill", function(d) { return d.fill; }) //'url(#grad)')//
			  .on("click", zoomIn)
			  .each(function(d) { this._current = enterArc(d); });
			  path.transition()
			  .style("fill-opacity", 1)
			  .style("stroke",function(d) {return d.parent.id == 50? "#2b2b2b":null})
			  .attrTween("d", function(d) { return arcTween.call(this, updateArc(d)); })
			  .transition().duration(sig).attr("d",arc2);

		  });
			} 
		else {
			path.transition().duration(2000).attr("d",arc);
			d3.transition().duration(2000)
				.each(function() {
					 	path.exit().transition()
						  .style("fill-opacity", function(d) { return d.depth === 1 + (root === p) ? 1 : 0; })
						  .attrTween("d", function(d) { return arcTween.call(this, exitArc(d)); })
						  .remove();
					  	path.enter()
					  		.append("path")
						  	.style("fill-opacity", function(d) { return d.depth === 2 - (root === p) ? 1 : 0; })
						  	.style("fill", function(d) { return d.fill; }) //'url(#grad)')//
						  	.on("click", zoomIn)
						  	.style("pointer-events","auto")
						  	.on("mouseover",function(o){
								var h = d3.selectAll(".node").filter(function(e) {return e.comp == o.parent.id && e.suggest == o.parent.id ? this : null;}).node();
								var g = d3.selectAll("circle").filter(function(e) {return e.comp == o.parent.id && e.suggest != 0 ? this : null;}).node();
								d3.selectAll("circle").style("fill", function(d) { return color(d.comp); });
	  							d3.select(g).style("fill","#2b2b2b");
								var f = h.__data__;
								if (f.time != null) {
							 		div.html('<u>Central cluster article:</u><br/><br/><a href=' + f.url + '>' + f.title + '</a><br/><br/>' + f.source  + '   ' + f.time.substr(5,2) + '/' + f.time.substr(8,2) + ' ' + f.time.substr(11,5) + '</><br/><br/>' + f.summary);
							 		}
								else { 
									div.html('<u>Central cluster article:</u><br/><br/><a href=' + f.url + '><b>' + f.title + '</b></a><br/><br/><b>' + f.source  + '</b><br/><br/>' + f.summary);
									}
								

						  		})
							.each(function(d) { this._current = enterArc(d); });
						path.transition()
								.style("fill-opacity", 1) 
								.attrTween("d", function(d) { return arcTween.call(this, updateArc(d)); });
				   	});
		  		}
			}//end of zoom function


  	function zoomSuggest() {
  				clock = 2;
				suggestt = 50;
				d3.selectAll("path").filter(function(d){return d.id == 50? this:null;}).style("stroke","#2b2b2b");
				var p = d3.selectAll("path").filter(function(d){return d.id == 50? this:null;}).node().__data__;
					if (p.depth > 1) p = p.parent;
				detail = p.id;
				if (!p.children) return;
				
			  	var newradius = 5*radius;
				zoom(p, p,newradius,1250,750);
				
				var h = d3.selectAll("circle").filter(function(e) {return e.suggest==1?  this : null;}).node(),
					g = h.__data__,
					cir = d3.selectAll(".node").filter(function(d) {return (d.suggest <= root.comps) && (d.suggest != 0) ? this : null;}),
					circir = d3.selectAll("circle").filter(function(d) {return (d.suggest <= root.comps) && (d.suggest != 0)? this : null;}),
					texts = d3.selectAll("#nodetext").filter(function(d) {return (d.suggest <= root.comps) && (d.suggest != 0) ? this : null;}),
					rects = d3.selectAll("#rect").filter(function(d) {return (d.suggest <= root.comps) && (d.suggest != 0) ? this : null;});

				cir.transition().duration(750)
						.transition().duration(1250)
						.attr("transform", function(d) {return around_suggest(d,centerx,centery,radius,newradius,500,clock);})
				circir.transition().duration(750)
				 		.transition().duration(1250)
				 		.attr("r",function(d){return 2*nodefac*(d.deg)+2;});

				path.style("pointer-events","none");
				// d3.select("#orderdiv")
				// 		.transition().duration(500)
				// 		.transition().duration(1500)
	   // 					.style("opacity",1);
				recto.transition().duration(2000).style("opacity",0)

			   	chart.transition().duration(750)
			   			.transition().duration(1250)
			   			.attr("transform", "translate(" + (-radius*3) + "," + centery + ")")
			   	center.transition().duration(750)
			   			.transition().duration(1250)
			   			.attr("rx", newradius)
			   			.attr("ry",newradius)
			   	div
			   			.style("opacity",0)
			   			.style("height","450px")
			   			.transition().duration(1500)
			   			// .transition().duration(1250)
			   			.style("left","50px")
			   			.style("top", (centery + 50) + "px")
			   			.transition().duration(500)
			   			.style("opacity",1)
			   			;
 
				if (g.time != null) {
					div.html('<a href=' + g.url + '>' + g.title + '</a><br/><br/>' + g.source  + '   ' + g.time.substr(5,2) + '/' + g.time.substr(8,2) + ' ' + g.time.substr(11,5) + '<br/><br/>' + g.summary)
					}
				else {
					div.html('<a href=' + g.url + '>' + g.title + '</a><br/><br/>' + g.source  + '<br/><br/>' + g.summary)
					}
				d3.selectAll("#image").attr("xlink:href",g.images);
				rects
						.attr("xlink:href",function(d){return d.url;})
						.style("pointer-events","auto");
				d3.selectAll("circle").filter(function(d) {return (d.suggest > root.comps) || d.suggest ==0  ? this : null;})
						.style("pointer-events","none")
						.transition().duration(2000)
						.style("opacity",0);
				d3.selectAll(".link")
						.transition().duration(1000)
						.style("opacity",0);
				topichead
						.html('<br/><h1>Graphite \n Reading List</h1><br/> The most central article from each cluster, ordered by cluster size. Going down this list maximises your overview!')
						.transition().duration(1500)
						.transition().duration(500)
						.style("opacity",1);
			  	d3.selectAll("#bubble").transition().duration(1500)
			  			.transition().duration(500)
			  			.style("opacity",1);
				texts.transition().duration(750)
						.transition().duration(1250)
						.style("opacity",1)
						.attr("dx", function (d) { return computeTextRotation(d) > 180 ? "-23" : "23"; }) // margin
						.attr("dy", ".35em")
						//.attr("transform", function(d) { return "translate(" + arc.centroid(d) + ")rotate(" + computeTextRotation(d) + ")"; })
						.attr('text-anchor', function (d) { return computeTextRotation(d) > 180 ? "end" : "start"; });



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

				cir.transition().duration(500)
						.transition().duration(1500)
						.attr("transform", function(d) {return around(d,centerx,centery,radius,newradius,500,clock);});
			})


	}); //end of d3.json(tgt)




d3.json(json, function(error, graph) {
	if (error) throw error;

	force
	.nodes(graph.nodes)
	.links(graph.links)
	.start();

	var timer = setTimeout(init_positions,2000);
	var link = svg.selectAll(".link")
			.data(graph.links)
			.enter().append("line")
			.attr("class", "link")
			.style("stroke-width", 1.5);

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

	var bubble = svg.append("ellipse")
	.attr("transform","translate(150," + (centery - 130) + ")")
	.attr("fill","url(#tile-ww)")
	.attr("id","bubble")
	.attr("rx", "100px")
	.attr("ry","100px")
	.style("opacity",0);

	var gotit = d3.select("body")
	.append("button")
	.attr("class", "btn btn-primary btn-md")
	.attr("id","gotit")
	.attr("type","button")
	.style("opacity", 1e-6)
	.style("left",centerx - radius/5 + "px")
	.style("top",centery + 8*radius/10 + "px" )
	.text("Get me going")
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
	  //.call(force.drag)
	  .on("mouseover",function(d){if (detail != 0){
	  		if (d.time != null) {
	  			div.html('<a href=' + d.url + '>' + d.title + '</a><br/><br/>' + d.source  + '   ' + d.time.substr(5,2) + '/' + d.time.substr(8,2) + ' ' + d.time.substr(11,5) + '<br/><br/>' + d.summary)
	  			}
	  		else {
	  			div.html('<a href=' + d.url + '>' + d.title + '</a><br/><br/>' + d.source  + '<br/><br/>' + d.summary)
			  	}
	  		var h = d3.selectAll("circle").filter(function(e) {return d.title == e.title ? this : null;}).node(),
	  			cir = d3.selectAll(".node").filter(function(d) {return detail == d.comp ? this : null;});
	  		
	  		d3.selectAll("circle").style("fill", function(d) { return color(d.comp); });
	  		d3.select(h).style("fill","#2b2b2b");
	  		cir.style("opacity", function (o) {
	  			return neighboring(d, o) | neighboring(o, d) ? 1 : 0.3;});
	  		d3.select("#image").attr('xlink:href', d.images);
	  				}

	  		})	  		
	  	.on("mouseout",function(){
		  	if (detail != 0) {
		  		var cir = d3.selectAll(".node").filter(function(d) {return detail == d.comp ? this : null;});
		  		cir.style("opacity", 1);
				}
			});

	  	node.append("a")
	  		.attr("id", "rect")
	  		.style("pointer-events","none")
		  	.append("rect")
		  	.attr("x", "10px")
		  	.attr("y", "-0.4em")
		  	.attr("width", function(d){return d.title.length*10 + "px";})
		  	.style("opacity",0)
			.attr("height", "1em")  
			.attr("fill", "white");


		node.append("text")
			.attr("id","nodetext")
			.attr("x", 12)
			.attr("y", '0.35em')
			.style("opacity",0)
			.style({"text-baseline":"left","text-anchor":"left","width":"40px"})
			.html(function(d){return d.title;});

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
			  if (d.time != null) {div.html('<a href=' + d.url + '>' + d.title + '</a><br/><br/>' + d.source  + '   ' + d.time.substr(5,2) + '/' + d.time.substr(8,2) + ' ' + d.time.substr(11,5) + '<br/><br/>' + d.summary)}
			  	else {div.html('<a href=' + d.url + '>' + d.title + '</a><br/><br/>' + d.source  + '<br/><br/>' + d.summary)}
			  		d3.select(this).style("fill","#2b2b2b"); 
			  })
			.on("click", function(d){return window.open(d.url, '_blank');})
			.on("mouseout",function(){
				if (detail != 0) {
					  var cir = d3.selectAll(".node").filter(function(d) {return detail == d.comp ? this : null;});
					  cir.style("opacity", 1);
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
			gotit.style("pointer-events","none");
			}

			div.transition().duration(3000).style("opacity",1);
		}



	force.on("tick", function() {
		link.attr("x1", function(d) { return d.source.x; })
		.attr("y1", function(d) { return d.source.y; })
		.attr("x2", function(d) { return d.target.x; })
		.attr("y2", function(d) { return d.target.y; });
		node.attr("transform", function(d) {return "translate(" + d.x + "," + d.y + ")"; });

				  });//end of force.on
	

}); // end of d3.json(json)




function key(d) {
  var k = [], p = d;
  while (p.depth) k.push(p.id), p = p.parent;
  return k.reverse().join(".");
}
function fill(d) {
  var p = d;
  while (p.depth > 1) p = p.parent;
  var c = d3.lab(p.id == 50? '#fff':color(p.id));//;d3.lab(color(p.id));
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
//})();    

