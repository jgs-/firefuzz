#!/usr/bin/python

from BaseHTTPServer import BaseHTTPRequestHandler
import SocketServer
import subprocess, os, urlparse, select, fcntl, sys, httplib
import random, string

class FuzzHandler(BaseHTTPRequestHandler):
	def do_GET(self):
		path = urlparse.urlparse(self.path)

		if (path.path == '/'):
			setup = open('setup.html', 'r').read()
			self.send_response(200)
			self.send_header('Content-type', 'text/html')
			self.end_headers()
			self.wfile.write(setup)
		else:
			tests = fetch_cases(1)

			for t in tests:
				if (len(test_cache) > 20):
					test_cache.pop(0)
				test_cache.append(t)

			if (len(tests) == 0):
				self.send_response(404)
				self.send_header('Content-type', 'text/plain')
				self.end_headers()
				self.wfile.write("DOLLA DOLLA BILL Y'ALL")
			else:
				self.send_response(200)
				self.send_header('Content-type', tests[0]['ctype'])
				self.end_headers()
				self.wfile.write(tests[0]['payload'])
def fetch_cases(n):
	c = httplib.HTTPConnection("tests.lmpws.net:1337")
	tests = []

	for i in xrange(n):
		c.request('GET', '/gimme')
		r = c.getresponse()

		if (r.status != 200):
			return tests

		tests.append({ 'ctype': r.getheader('content-type'), 'payload': r.read() })

	return tests

def restart_browser(p = None):
	if (p != None):
		os.system("rm -rf ~/.mozilla/firefox/*" + p.profile + "*")
		os.system("rm -rf ~/.cache/mozilla")
		p.kill()

	profile = ''.join([random.choice(string.ascii_letters + string.digits) for n in xrange(10)])
	os.system("DISPLAY=:1 ./firefox -no-remote -CreateProfile " + profile)

	target_env = os.environ.copy()
	target_env['DISPLAY'] = ':1'

	new = subprocess.Popen(["./firefox", "-no-remote", "-P", profile, "http://localhost:9138/"],
		stdin = subprocess.PIPE,
		stdout = subprocess.PIPE,
		stderr = subprocess.PIPE,
		env=target_env)

	for pipe in [new.stdout, new.stderr]:
		fd = pipe.fileno()
		fl = fcntl.fcntl(fd, fcntl.F_GETFL)
		fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)

	new.profile = profile
	return new

def is_asan_log(data):
	if (data.find('AddressSanitizer') != -1):
		return True
	return False

def asan_hit(log, tests):
	results_dir = '/home/jim/rezults/'
	crash_dir = results_dir + ''.join([random.choice(string.ascii_letters + string.digits) for n in xrange(16)]) + '/'
	os.mkdir(crash_dir)

	f = open(crash_dir + 'asan.log', 'w+')
	f.write(log)
	f.close()

	for i in xrange(len(tests)):
		f = open(crash_dir + str(i) + '.test', 'w+')
		f.write(tests[i]['payload'])
		f.close()

SocketServer.TCPServer.allow_reuse_address = True

test_cache = []
handler = FuzzHandler
httpd = SocketServer.TCPServer(('localhost', 9138), handler)
httpd.timeout = 2

tick = 0
console_out = ''

process = restart_browser()

while True:
	reads,writes,excs = select.select([process.stdout, process.stderr], [], [], 0)

	for r in reads:
		try:
			console_out += r.read()
		except:
			pass

		if (is_asan_log(console_out)):
			asan_hit(console_out, test_cache)
			console_out = ''
			test_cache = []

	httpd.handle_request()

	tick += 1
	if (tick >= 50):
		print "restarting browser.."
		process = restart_browser(process)
		tick = 0
