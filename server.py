#!/usr/bin/env python

import socket, os, sys, errno, select

serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

serverSocket.bind(("0.0.0.0", 8000))
serverSocket.listen(5)

while (True):
	(incomingSocket, address) = serverSocket.accept()
	print "Got a connection from %s" % (repr(address))

	# Reaped the child process
	try:
		reaped = os.waitpid(0, os.WNOHANG)
	except OSError, e:
		if e.errno == errno.ECHILD:
			pass
		else:
			raise
	else:
		print "Reaped %s" % (repr(reaped))

	# fork process 
	if (os.fork() != 0):
		continue

	clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	# AF_INET means we want an IPv4 socket
	# SOCK_STREAM means we want a TCP socket

	clientSocket.connect(("www.google.com", 80))

	incomingSocket.setblocking(0)
	clientSocket.setblocking(0)

	while True:

		# receive from client and forwording to target server
		request = bytearray()
		while True:
			try:
				part = incomingSocket.recv(1024)
			except IOError, e:
				if e.errno == socket.errno.EAGAIN:
					break
				else:
					raise

			if (part):
				request.extend(part)
				clientSocket.sendall(part)
			else:
				sys.exit(0) # quit the program

		if len(request) > 0:
			print (request)

		# receive form target server and forwording to client
		response = bytearray()
		while True:
			try:
				part = clientSocket.recv(1024)
			except IOError, e:
				if e.errno == socket.errno.EAGAIN:
					break
				else:
					raise

			if (part):
				response.extend(part)
				incomingSocket.sendall(part)
			else:
				sys.exit(0) # quit the program

		if len(response) > 0:
			print (response)

		# setup to talk to either one of client and target server
		select.select(
			[incomingSocket, clientSocket], # read
			[], 														# write
			[incomingSocket, clientSocket], # exceptions
			1.0) 														# timeout

