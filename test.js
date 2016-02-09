/*
using skewer: https://github.com/skeeto/skewer-mode
  1. make sure skewer-mode.el is loaded
  2. M-x httpd-start
  3. M-x run-skewer
  4. make sure <script src="http://localhost:8080/skewer"></script> in html
  5. M-x skewer-repl

(defun skewer-eval-region (beg end)
  "Execute the region as JavaScript code in the attached browsers."
  (interactive "r")
  (skewer-eval (buffer-substring beg end) #'skewer-post-minibuffer))

(define-key skewer-mode-map (kbd "C-c C-r") 'skewer-eval-region)
*/

orig = $("#content").html();
orig_txt = $("#content").text();

support_list = [
["Definition", 0, 0],
["Justification", 0, 0],
["Example", 0, 0],
["suggested", 0, 0],
["eliminating", 0, 0],
["distinguish", 0, 0]
];

c = $("#content");

colored_span = function(c, s) {
  return "<span style=\"background-color:"+c+";\">" + s + "</span>";
};

highlight = function(s) {
  return colored_span("yellow",s);
};
idsupport = function(s) {
  return colored_span("pink",s);
};

find_match_list = function(txt, token) {
  var rtn = [], i = -1;
  while( (i=txt.indexOf(token,i+1)) >= 0 ) {
    rtn.push(i);
  }
  return rtn;
};

highlight_all_matching = function(token) {
  if(!token) {
    return;
  }
  console.log(token);
  
  var r = new RegExp("\\b"+token+"\\b", "g");
  c.html(orig.replace(r, highlight(token)));
};

get_verified_support_list = function(txt, support_list) {
  var verified_support_list = [];

  support_list.forEach(function(support) {
    var token = support[0], index_target = support[1];

    // find closest
    var buf = [];
    find_match_list(txt, token).forEach(function(index_actual) {
      buf.push([Math.abs(index_target-index_actual), index_actual]);
    });
    buf.sort();
    var index_best = buf[0][1];
    verified_support_list.push([index_best, token]);
  });
  return verified_support_list;
};

apply_transform_at_index = function(txt, transformer, index, length) {
  return txt.substring(0, index) + transformer(txt.substring(index, index+length)) + txt.substring(index+length);
};

label_support = function(support_list) {
  var tmp = c.html();

  get_verified_support_list(tmp, support_list).sort().reverse().forEach(function(pair) {
    var index = pair[0], token = pair[1];
    tmp = apply_transform_at_index(tmp, idsupport, index, token.length);
  });
  c.html(tmp);
};

find_anchor = function(support_list, token, index) {

  var tmp = c.html();

  var verified_support_list = get_verified_support_list(tmp, support_list);
  var mean_offset_buf = [];
  find_match_list(tmp, token).forEach(function(token_index) {
    var buf = [];
    verified_support_list.forEach(function(pair) {
      var index_best = pair[0], support_token = pair[1];
      buf.push(Math.abs(token_index - index_best));
    });
    mean_offset_buf.push([buf.reduce(function(a,b){return a+b;}), token_index]);
  });
  
  var min_mean = Math.min.apply(this, mean_offset_buf.map(function(pair){return pair[0]}));
  var max_mean = Math.max.apply(this, mean_offset_buf.map(function(pair){return pair[0]}));
  mean_offset_buf.sort(function(b,a){return a[1]-b[1]}).forEach(function(pair) {
    var token_index = pair[1];
    if(pair[0] == min_mean) {
      var color = "red";
    } else {
      var v = Math.round(pair[0]/max_mean*230);
      var color = "rgb("+v+","+v+","+v+")"
    }
    c.html(apply_transform_at_index(c.html(),
                                    function(token){return colored_span(color, token);}, token_index, token.length));
  });
  return mean_offset_buf.sort()[0][1];
};


(function() {

label_support(support_list);

var t = "document";
var i = find_anchor(support_list, t);
c.html(apply_transform_at_index(c.html(), function(token){return colored_span("lime", token);}, i, t.length));


  });

$("#btn").click(function() {
  var token = $("#txt").val();
  highlight_all_matching(token);
});

