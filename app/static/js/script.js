
$(document).ready(function() {
  $('#mytable').DataTable();
});
const url='http://0.0.0.0:5000'

var socket = io.connect(url);