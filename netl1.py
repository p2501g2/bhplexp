import socket
#TCP Client

def tcper():
    target_host = "0.0.0.0"
    target_port = 9999
    
    #Create socket object
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    #CONNECT THE CLIENT
    client.connect((target_host, target_port))
    
    #send some data
    client.send("WTF am i doing?")
    
    #receive some data
    response = client.recv(4096)
    
    print response

def udper():
    target_host = "127.0.0.1"
    target_port = 80
    
    #create a socket object
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    #send some data
    client.sendto("AAABBBCCC",(target_host, target_port))
    
    #receive some data
    data, addr = client.recvfrom(4096)
    
    print data

if __name__ == '__main__':
    tcper()