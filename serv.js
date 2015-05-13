#!/usr/bin/nodejs

var incoming = '';
var tests = 0;
var count = 0;
var cache = new Array();
var http = require('http');

console.log("let's do it..");

http.createServer(function(req, res) {
	if (req.method === 'POST') {
		if (req.url === '/new') {
			req.on('data', function(chunk) {
				incoming += chunk.toString();
			});

			req.on('end', function() {
				cache.push([req.headers['content-type'], incoming]);
				tests++;
				incoming = '';

				res.writeHead(200, 'OK', { 'Content-Type': 'text/plain' });
				res.end('' + tests);
			});
		} 
	}

	if (req.method === 'GET') {
		if (req.url === '/gimme') {
			if (tests == 0) {
				res.writeHead(404, 'Not Found', { 'Content-Type': 'text/plain' });
				res.end('<script>TODO</script>');
			} else {
				count++;
				if (count % 10 == 0) {
					console.log(";PppPPp");
				}
				tests--;
				var stuff = cache.pop();
				res.writeHead(200, 'OK', { 'Content-Type': stuff[0] });
				res.end(stuff[1]);
			}
		}

		if (req.url === '/howmany') {
			res.writeHead(200, 'OK', { 'Content-Type': 'text/plain' });
			res.end('' + tests);
		}

		if (req.url === '/clear') {
			tests = 0
			cache = new Array();
			res.writeHead(200, 'OK', {'Content-Type': 'text/plain' });
			res.end('');
		}
	}
}).listen(1337, '0.0.0.0');
