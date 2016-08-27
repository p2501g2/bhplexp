import sys
import socket
import threading


def hexdump(src, length=16):
    # http://code.activestate.com/recipes/142812-hex-dumper/   
    '''
    This function produce a classic 3 columns hex dump of a string. * The first column print the offset in hexadecimal. * The second colmun print the hexadecimal byte values. * The third column print ASCII values or a dot for non printable characters.  Is unicode-aware, but makes no attempt to display characters outside the 7-bit printable ASCII range -- too difficult in a Windows console.
    '''
    result = []
    digits = 4 if isinstance(src, unicode) else 2
    for i in xrange(0, len(src), length):
        s = src[i:i+length]
        hexa = b' '.join(["%0*2X" % (digits, ord(x)) for x in s])
        text = b''.join([x if 0x20 <= ord(x) < 0x7F else b'.' for x in s])
        result.append( b"%04X   %-*s   %s" % (i, length*(digits + 1), hexa, text) )
        
    return b'\n'.join(result)


def receive_from(connection):
    buffer = ""
    #set a 2 second timeout; depending on target, could require adjustments
    connection.settimeout(2)
    
    try:
        #keep reading into the buffer until no more data
        while True:
            data = connection.recv(4096)
                
            if not data:
                break
            
            buffer += data
            
    except:
        pass
    
    return buffer


# modify any requests destined for th remote host
def request_handler(buffer):
    # perform packet modifications
    return buffer


# modify any responses destined for the local host
def response_handler(buffer):
    # perform packet modifications
    return buffer


def server_loop(local_host, local_port, remote_host, remote_port, receive_first):
    
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        server.bind((local_host, local_port))
    except:
        print "[!!] Failed to lesten on %s%d" % (local_host, local_port)
        print "[!!] Check for other lestening sockets or correct permissions."
        sys.exit(0)
        
    print "[*] Listening on %s:%d" % (local_host, local_port)
    
    server.listen(5)
    
    while True:
        client_socket, addr = server.accept()
        
        #print out the local connection information
        print '[==>] Received incoming connection from %s:%d' % (addr[0], addr[1])
        
        #start a thrad to talk to the remote host
        proxy_thread = threading.Thread(target=proxy_handler, args=(client_socket, remote_host, remote_port, receive_first))
        
        proxy_thread.start()


def proxy_handler(client_socket, remote_host, remote_port, receive_first):
    
    # connect to the remote host
    remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    remote_socket.connect((remote_host, remote_port))
    
    # receive data from the remote end if necessary
    if receive_first:
        
        remote_buffer = receive_from(remote_socket)
        hexdump(remote_buffer)
        
        # send it to response handler
        remote_buffer = response_handler(remote_buffer)
        
        # if we have data, send it to our local client
        if len(remote_buffer):
            print "[ <== ] Sending %d bytes to localhost." % len(remote_buffer)
            client_socket.send(remote_buffer)
            
    '''
    Now loop and read form local,
        send to remote, send to local
    rinse, wash, repeat
    '''
    while True:
        
        #read from local host
        local_buffer = receive_from(client_socket)
        
        if len(local_buffer):
            
            print " [==>] Received %d bytes from localhost." % len(local_buffer)
            hexdump(local_buffer)
            
            # send it to our request handler
            local_buffer = request_handler(local_buffer)
            
            # send off the data to the remote host
            remote_socket.send(local_buffer)
            print "[ ==> ] Sent to remote."
            
            # receive back the response
            remote_buffer = receive_from(remote_socket)
            
        if len(remote_buffer):
            
            print "[ <== ] received %d bytes from remote." % len(remote_buffer)
            hexdump(remote_buffer)
            
            #send to our response handler
            remote_buffer = response_handler(remote_buffer)
            
            # send the response to the local socket
            client_socket.send(remote_buffer)
            
            print "[ <== ] Sent to localhost."
        
        # if no more data on either side, close the connections
        if not len(local_buffer) or not len(remote_buffer):
            client_socket.close()
            remote_socket.close()
            print "[*] No more data. Closing connections."
            
            break
    


def main():
    
    if len(sys.argv[1:]) != 5:
        print "Usage: ./proxy.py [localhost] [localport] [remotehost] [remoteport] [receive_first]"
        print "Example: ./proxy.py 127.0.0.1 9000 10.12.132.1 9000 True"
        sys.exit(0)
        
    # setup local listening parameters
    local_host = sys.argv[1]
    local_port = int(sys.argv[2])
    
    # setup remote target
    remote_host = sys.argv[3]
    remote_port = int(sys.argv[4])
    
    #this tells proxy to connect and receive data before sending to remote host
    receive_first = sys.argv[5]
    
    if "True" in receive_first:
        receive_first = True
    else:
        receive_first = False
        
    # now spin uip our listening socket
    server_loop(local_host, local_port, remote_host, remote_port, receive_first)


main()
    