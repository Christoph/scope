//(function(){
//var this_js_script = $('script[src*=somefile]');

var width = window.innerWidth,
height = window.innerHeight;


if (window.innerWidth >= max_width) {

var centerx = 0,
centery = height/2;

var svg = d3.select("#intro-container").append("svg").attr("viewBox", "0 0 " + width + " " + height + "");//.attr("preserveAspectRatio","xMidYMid slice");

var radius = height/5

var div = d3.select("#intro-container").append("centtext")
	.attr("class", "centtext")

var chart = d3.select("svg").append("svg:svg")
  .append("svg:g")

var arc = d3.svg.arc()
	.startAngle(function(d) { return d.x; }) // + 1/8*Math.PI
	.endAngle(function(d) { return d.x + d.dx ; }) // + 1/8*Math.PI
	.padAngle(.01)

	var radius = height/5

	var force = d3.layout.force()
		.charge(function(){return width <= 800? -20 : -80;})
		.linkDistance(function(){return width <= 800? linkdist/2 : linkdist;})
		.size([width, height]);

	var hue = d3.scale.category20();


	div.style("opacity", 1e-6)
		.style("left",width/2.2 + "px")
	.style("top", height/5 + "px" )
	.style("max-width", width/3 + "px")
	.html("<img src='static/homepage/img/logos/scope_logo1.png' style='width:"+ width/5 + "px'><br /><br /><h2>We help you find and exploit the structure in the documents relevant to you.</h2><h2>Tame information overflow with our Scope Curation Technology. Now.</h2><br /><br /><br /><div class='row'><div class='col-xs-12 col-md-12 wow fadeInUp' data-wow-delay='1s'><a href='#services' class='btn btn-secondary btn-lg page-scroll'>Learn More</a></div></div>");   
	chart.style('opacity',0)
		.attr("width", height/2)
	.attr("height",height/2)
	.attr("transform", "translate(0," + centery + ")");

	arc.padRadius(radius /3 )
	.innerRadius(function(d) { return radius*1.3; })
	.outerRadius(function(d) { return radius*1.3 - 50; });


var partition = d3.layout.partition()
	.sort(function(a, b) { return d3.ascending(a.id, b.id); })
	.size([2*Math.PI, radius]); // 7/4* 

var json //= //"/static/last24h/ug_nl_cluster.json"
,tgt;// = "/static/last24h/tgt_cluster.json";

d3.json(tgt, function(error, root) {
  if (error) throw error;

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
	  .attr("rx", radius + 50)
	  .attr("ry",radius + 50)
	  .style("fill","#ffffff");

  var path = chart.selectAll("path")
	  	.data(partition.nodes(root).slice(1))
		.enter().append("path")
		.attr("class","path")
	  	.attr("d", arc)
	  	.style("fill", function(d) { return d.fill; })
	  	.each(function(d) { this._current = updateArc(d); });

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

	var node = svg//.append("g")  
	  .selectAll(".node")
	  .data(graph.nodes)
	  .enter().append("g")
	  .attr("class", "node");

		node.append("circle")
			.style("opacity",function(d){return d.single ==1 ? 0:1;})
			.attr("r", function(d) {return d.deg*nodefac+6;})
			.style("fill", function(d) { return colors(d.comp); })
			.style("stroke",function(d) {return (d.suggest <= graph.graph.comps) && (d.suggest != 0) ? '#2b2b2b' :'#fff';})
			.style("opacity",function(d){return (d.single == 1)? 0:1;});

	function calc_pos(d){
				var x = node.filter(function(e) {return e.comp < d.comp ? this : null;}).size()+node.filter(function(e) {return e.comp == d.comp ? this : null;}).size()/2,
					y = 68//d3.selectAll("circle").size(),
					f = node.filter(function(e) {return e.comp == d.comp? this : null;}).node().__data__; //&& e.suggest != 0 THIS NEEDS TO GO BACK IN!
				if (0<= x/y < 0.25) {var T = Math.tan(2*Math.PI*x/y),TT = radius*2/Math.sqrt(1+Math.pow(T,2)); return [-TT*T+d.x-f.x,TT+d.y-f.y];}
				else if (0.25 <= x/y< 0.5) {var T = Math.tan(2*Math.PI*x/y-Math.PI),TT = radius*2/Math.sqrt(1+Math.pow(T,2)); return [TT*T+d.x-f.x,-TT+d.y-f.y];}
				else if (0.5 <= x/y< 0.75) {var T = Math.tan(2*Math.PI*x/y),TT = radius*2/Math.sqrt(1+Math.pow(T,2)); return [-TT*T+d.x-f.x,TT+d.y-f.y];}
				else if (0.75 <= x/y< 0.1){var T = Math.tan(2*Math.PI*x/y-3*Math.PI),TT = radius*2/Math.sqrt(1+Math.pow(T,2)); return [-TT*T+d.x-f.x,TT+d.y-f.y];}
				else {var T = Math.tan(2*Math.PI*x/y-3*Math.PI),TT = radius*2/Math.sqrt(1+Math.pow(T,2)); return [TT*T+d.x-f.x,-TT+d.y-f.y];}
		}

	function init_positions() {


		force.stop();
			node.transition().duration(2000).style("opacity",1).attr("transform", function(d) {return "translate(" + (centerx+calc_pos(d)[0]) + "," + (centery+ calc_pos(d)[1]) + ")"; });
			link.transition().duration(2000).style("opacity",1).attr("x1", function(d) {return centerx+calc_pos(d.source)[0];}) 
			.attr("y1", function(d) {return centery+calc_pos(d.source)[1];})
			.attr("x2", function(d) {return centerx+calc_pos(d.target)[0];})
			.attr("y2", function(d) {return centery+calc_pos(d.target)[1];}); 
			chart.transition().duration(1000).style("opacity",1);
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

}

else {
	var single,
	landscape,
	short,
	long;

	if (width > height) {landscape = true; short = height; long=width} 
	else {landscape = false; short = width; long=height;}

var svg = d3.select("#intro-container").append("svg").attr("viewBox", "0 0 " + width + " " + height + "");
var text = d3.select("#intro-container").append("centtext")
	.attr("class", "centtext")
	.style("opacity", 0);


	if (height > 400) {
		text.html("<h2 style='margin-top:0;'>Find and exploit structure in the documents relevant to you.</h2><br /><div class='row'><div class='col-xs-12 col-md-12 wow' ><a href='#services' class='btn btn-secondary btn-lg page-scroll'>Learn More</a></div></div>");   
	}
	else {
		text.html("<h3 style='margin-top:0;'>Find and exploit structure in the documents relevant to you.</h3><br /><div class='row'><div class='col-xs-12 col-md-12 wow' ><a href='#services' class='btn btn-secondary btn-lg page-scroll'>Learn More</a></div></div>");   
	}
var logo_width = 150;
var logo = d3.select("#intro-container").append("centtext")
	.attr("class", "centtext")
	.style("left",(width - logo_width)/2 + "px")
	.style("top", "20px" )
	.style("max-width", logo_width + "px")
	.style("opacity",0)
	.html("<img src='static/homepage/img/logos/scope_logo1.png' style='width:"+ logo_width + "px'>");

if (landscape) {
	text.style("left",width/2 + "px")
		.style("top", height/3 + "px" )
		.style("max-width", width*7/16 + "px")
		}

else {	
	text.style("left",width/10 + "px")
		.style("top", height/2 + "px" )
		.style("max-width", width*4/5 + "px")

}


d3.json(single, function(error, graph) {
	if (error) throw error;

	var timer = setTimeout(show_points,500);
	var link = svg.selectAll(".link")
			.data(graph.links)
			.enter().append("line")
			.attr("class", "link")
			.style("stroke-width", 2.5)
			.style("opacity", 0);

			if (landscape) {
			link.attr("x1", function(d) {return d.source*width/6})
			.attr("x2", function(d) {return d.target*width/6})
			.attr("y1", height/2)
			.attr("y2", height/2);
			}

			else {
			link.attr("x1", width/2)
			.attr("x2", width/2)
			.attr("y1", function(d) {return d.source*height/6})
			.attr("y2", function(d) {return d.target*height/6});

			}
	var node = svg
	  .selectAll(".node")
	  .data(graph.nodes)
	  .enter().append("g")
	  .attr("class", "node")
	  .style("pointer-events","none");

		node.append("circle")
			.style("pointer-events","none")
			.style("opacity",0)
			.attr("r", short/30)
			.style("fill", colors(0))//function(d) { return colors(d.id); })
			.style("stroke", "#fff")
			.style("stroke-width", short/200)
			.attr("transform", function(d) {
				if (landscape) {return "translate(" + d.id*width/6 + "," + height/2 + ")"}
				else {return "translate(" + width/2 + "," + d.id*height/6 + ")"; }
			});
		

function show_points() {
		d3.selectAll("circle").transition().duration(function(d) {return d.id*500;}).style("opacity",1);
		var timer = setTimeout(turn_to_cluster,1000);	
		}

function turn_to_cluster() {
		node.transition().duration(2000)
			.attr("transform", function(d) {
			var [x,y] = calc_pos2(d.id);
			if (landscape) {
				x = x - d.id*width/6;
				y = y - height/2;
			}
			else {
				x = x - width/2;
				y = y - d.id*height/6;
			}

			return "translate(" + x + "," + y + ")";});
		link.transition().duration(2000).style("opacity",1).attr("x1", function(d) {return calc_pos2(d.source)[0];}) 
			.attr("y1", function(d) {return calc_pos2(d.source)[1];})
			.attr("x2", function(d) {return calc_pos2(d.target)[0];})
			.attr("y2", function(d) {return calc_pos2(d.target)[1];}); 
		d3.selectAll("circle").transition().duration(500)
			.attr("r", function(d) {
				return d.id == 4 ? short*1.1/30:short/30;
			})
			.style("stroke", function(d) {
				return d.id == 4 ? "#94949":"#fff";
			})
			.style("fill", function(d) {
				return d.id == 4 ? colors(1):colors(0);
			})
		logo.transition().duration(500).transition().duration(1000).style("opacity", 1);
		text.transition().duration(500).transition().duration(1000).style("opacity", 1);
		}

function calc_pos2(d) {
	var x,y;

	if (d == 1) {
		x = short*1/3;
		y = long*1.5/6;
	} 

	else if (d == 2) {
		x = short*2/3;
		y = long*1.5/8;
	} 
	else if (d == 3) {
		x = short*2.25/3;
		y = long*1.5/6;
	} 

	else if (d == 4) {
		x = short*1/2;
		y = long*2/6;
	} 
	else if (d == 5) {
		x = short*1/2;
		y = long*2.5/6;
	} 
	if (landscape) {return [y,x];}
	else {return [x,y];}
}

		})
}

function colors(d) {
	var list = ['#1E5184','#A8290D','#588B8B','#EDEDED','#494949'];
	return list[d%5];
}

function key(d) {
  var k = [], p = d;
  while (p.depth) k.push(p.id), p = p.parent;
  return k.reverse().join(".");
}
function fill(d) {
  var p = d;
  while (p.depth > 1) p = p.parent;
  var c = d3.lab(p.id == 50? '#fff':colors(p.id));//;d3.lab(color(p.id));
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
 




