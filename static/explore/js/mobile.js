var w = window.innerWidth,
    h = 800,
    x = d3.scale.linear().range([0, 4*w]),
    y = d3.scale.linear().range([0, h]);



var vis = d3.select("body").append("div")
    .attr("class", "chart")
    .style("width", w + "px")
    .style("height", h + "px")
  .append("svg:svg")
    .attr("class", "svg-mobile")
    .attr("width", w)
    .style("height", h);

var partition = d3.layout.partition()
  //.children(function(d, depth) { return d._children; })
    .value(function(d) { return d.size; });

  
d3.json(tgt, function(root) {

  h = root.comps*50;
  y = d3.scale.linear().range([0, h]);
  vis.style("height", h + "px");
  d3.select("svg").style("height",h);
  var g = vis.selectAll("g")
      .data(partition.nodes(root))
    .enter().append("svg:g")
      .attr("transform", function(d) { return "translate("+ x(d.y) + "," + y(d.x) + ")"; })
      .style("width",1/2*w) //maybe this is a mistake, need to check it out
      .on("click", click);

  var kx = w / root.dx,
      ky = h / 1;
  g.append("svg:rect")
      .attr("width", w)//root.dy * kx)
      .attr("height", h)//function(d) { return d.dx * ky; })
      .style("fill", function(d) { return color(d.id); })
      .attr("class", function(d) { return d.children ? "parent" : "child"; });


  g
  //   .append("svg:div").attr("class","centtext")
  //     .style("left","0px")
  //     .style("top","0px")
  //     .style("width", w)
      .append("svg:foreignObject")
      .attr("transform", function(d) { return "translate("+ x(d.y) + "," + y(d.x) + ")"; })
      .attr("width",4/5*w)
      .attr("height", h)
      .style("position","relative")
      //.attr("transform", transform)
      //.attr("dy", ".35em")
      .style("opacity", function(d) { return d.dx * ky > 12 ? 1 : 0; })
      .append("xhtml:text")
      .attr("transform", transform)
      .attr("class","text_mobile")
      .style("position","relative")
      .html(function(d) { return d.name; })  

  // g.append("svg:text")
  //     .attr("transform", transform)
  //     .attr("dy", ".35em")
  //     .style("opacity", function(d) { return d.dx * ky > 12 ? 1 : 0; })
  //     .text(function(d) { return d.name; })

  d3.select(window)
      .on("click", function() { click(root); })

  function click(d) {
    //if (!d.parent) return;

    if (d.id == 0 ) {
      x.range([0,16/5*w]);
      console.log(d.x)
      var t = g.transition()
        .duration(d3.event.altKey ? 7500 : 750)
        .attr("transform", function(d) { return "translate(" + (x(d.y)-4/5*w) + "," + y(d.x) + ")"; });

        t.select("rect")
          .attr("width", 4*w/5)//d.dy * kx)
          .attr("height", function(d) { return d.dx * ky; });


        t.select("text")
          .attr("transform", transform)
          .style("opacity", function(d) { return d.dx * ky > 12 ? 1 : 0; });

        }

       else if (d.parent == root) {

      x.domain([0,1]).range([0,16/5*w]);
      y.domain([0,1]);
      ky = h / d.dx;
      var t = g.transition()
        .duration(d3.event.altKey ? 7500 : 750)
        .attr("transform", function(d) { return "translate(" + (x(d.y)-4/5*w) + "," + y(d.x) + ")"; });

        t.select("rect")
          .attr("width", 4*w/5)//d.dy * kx)
          .attr("height", function(d) { return d.dx * ky; });


        t.select("text")
          .attr("transform", transform)
          .style("opacity", function(d) { return d.dx * ky > 12 ? 1 : 0; });
          

        }

        else{
      //kx = (d.y ? w - 40 : w) / (1 - d.y);
      ky = h / d.dx;
      //console.log(d.y)

      x.domain([d.y, 1+d.y]).range([d.y ?40 : 0,16/5*w]);
      y.domain([d.parent.x, d.parent.x + d.parent.dx]);

      var t = g.transition()
          .duration(d3.event.altKey ? 7500 : 750)
          .attr("transform", function(d) { return "translate(" + (x(d.y))+ "," + y(d.x) + ")"; });

        t.select("rect")
          .attr("width", w)//d.dy * kx)
          .attr("height", function(d) { return d.dx * ky; });


        t.select("text")
          .attr("transform", transform)
          .style("opacity", function(d) { return d.dx * ky > 12 ? 1 : 0; });
          

        }

      d3.event.stopPropagation();



}

  function transform(d) {
    return "translate(8," + d.dx * ky / 2 + ")";
  }

});

function fill(d) {
  var p = d;
  while (p.depth > 1) p = p.parent;
  var c = d3.lab(p.id == 50? '#fff':color(p.id));//;d3.lab(color(p.id));
  //c.l = luminance(d.sum);
  return c;
}

function getlength(number) {
    return number.toString().length;
}

var color = d3.scale.category20(); //maybe 20c was the better choice
