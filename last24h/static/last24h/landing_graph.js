var width = 150,
    height = 150;

var color = d3.scale.category20();

var force = d3.layout.force()
    .charge(-400)
    .linkDistance(60)
    .size([width, height]);

var svg = d3.select("#graphbox").append("svg")
    .attr("width", width)
    .attr("height", height)
    .attr("id","landing")
    .style("background","#f2f2f2");

d3.json(landing, function(error, graph) {
  if (error) throw error;

  // force
  //     .nodes(graph.nodes)
  //     .links(graph.links)
  //     .start();

  var link = svg.selectAll(".link")
      .data(graph.links)
    .enter().append("line")
      .attr("class", "link")
      .style("stroke-width", function(d) { return Math.sqrt(d.value); });

  var node = svg.selectAll(".node")
      .data(graph.nodes)
    .enter().append("circle")
    .style("pointer-events","none")
      .attr("class", "node")
      .style("stroke",'#fff')
      .attr("r", 9)
      .style("fill", '#ffbb78')

      .call(force.drag);

  var button = d3.select("#graphbox")
    .append("a")
    .attr("class", "btn btn-secondary btn-lg")
    .attr("href","/")
    // .attr("role","button")
    .html('Check it out')
    .on('mouseover',function(){rot = 1;node.style("fill", '#ff7f0e')})
    .on('mouseout',function(){rot = 80;node.style("fill", '#ffbb78')});


   // var timer = setTimeout(init_positions,4000);

// var timer2 =  setInterval(rotations,5000);

  node.append("title")
      .text(function(d) { return d.name; });

  // force.on("tick", function() {
  //   link.attr("x1", function(d) { return d.source.x; })
  //       .attr("y1", function(d) { return d.source.y; })
  //       .attr("x2", function(d) { return d.target.x; })
  //       .attr("y2", function(d) { return d.target.y; });

  //   node.attr("cx", function(d) { return d.x; })
  //       .attr("cy", function(d) { return d.y; });

var centerx = 277,
centery = 142,
radius = 210;

init_positions()
var i=0,
rot = 80,
ti = 50,
timer=setInterval(function(){i++;return rotations(i);},ti);

function rotations(i) {
      node.attr("transform", function(d) {return "translate(" + (centerx+Math.sin(d.id/7*Math.PI+i/(rot*Math.PI))*radius) + "," + (centery+ Math.cos(d.id/7*Math.PI+i/(rot*Math.PI))*radius) + ")"; });
      link
          .attr("x1", function(d) {return centerx+Math.sin(d.source/7*Math.PI+i/(rot*Math.PI))*radius;}) 
          .attr("y1", function(d) {return centery+Math.cos(d.source/7*Math.PI+i/(rot*Math.PI))*radius;}) 
          .attr("x2", function(d) {return centerx+Math.sin(d.target/7*Math.PI+i/(rot*Math.PI))*radius;}) 
          .attr("y2", function(d) {return centery+Math.cos(d.target/7*Math.PI+i/(rot*Math.PI))*radius;})  

    }


  function init_positions() {
      // force.stop();
      node.attr("transform", function(d) {return "translate(" + (centerx+Math.sin(d.id/7*Math.PI)*radius) + "," + (centery+ Math.cos(d.id/7*Math.PI)*radius) + ")"; });
      link
          .attr("x1", function(d) {return centerx+Math.sin(d.source/7*Math.PI)*radius;}) 
          .attr("y1", function(d) {return centery+Math.cos(d.source/7*Math.PI)*radius;}) 
          .attr("x2", function(d) {return centerx+Math.sin(d.target/7*Math.PI)*radius;}) 
          .attr("y2", function(d) {return centery+Math.cos(d.target/7*Math.PI)*radius;})  

    }

  });