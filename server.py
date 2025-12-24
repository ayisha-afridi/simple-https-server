import socket

def start_server(host='127.0.0.1', port=8000):
    # Create a TCP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # Allow the socket to reuse a local address right after the socket is closed 
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    # Bind socket to host and port
    # Specify where the server should listen for incoming network requests
    server_socket.bind((host, port))
    
    # Listen for incoming connections, queuing up to 5
    server_socket.listen(5)
    
    # If everything is successful, print the server address
    print(f"Server listening on http://{host}:{port}")
    
    try:
        # Continuously listen for incoming client connections
        while True:
            # Accept a connection from a client
            client_socket, client_address = server_socket.accept()
            print(f"Connection from {client_address}")
            
            # Receive data from client (up to 1024 bytes)
            # recv() returns bytes, so we must decode it into a unicode string
            request_data = client_socket.recv(1024).decode('utf-8')
            print(f"Request:\n{request_data}\n")

            # HTTP request information:
            # 1) Request line: HTTP method, path, HTTP version used to send request
            # 2) Header (contains metadata about the request)
            # 3) Optional body message (not in GET requests)

            # Parse the first line to get the requested path
            # Split the request string by the newline character 
            request_lines = request_data.split('\n')
            first_line = request_lines[0]
            method, path, protocol = first_line.split()
            
            print(f"Method: {method}, Path: {path}")
            
            # HTTP response
            response_body = f"""
            <html>
            <head><title>My HTTP Server</title></head>
            <body>
                <h1>Hello!</h1>
                <p>You requested: {path}</p>
                <p>Method: {method}</p>
            </body>
            </html>
            """
            
            # HTTP response to send to a client in response to an HTTP request
            # Consists of a status line, headers, and a body (optional)
            # Response code 200 indicates that the request succeeded
            # "Content-Length: {len(response_body)}": tells the browser how many bytes to expect in the response body
            response_headers = f"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nContent-Length: {len(response_body)}\r\n\r\n"
            response = response_headers + response_body
            
            # Send response back to client
            # Encode the response because the socket requires bytes for transmission
            client_socket.sendall(response.encode('utf-8'))
            
            # Close the client connection
            client_socket.close()
            
    # Ensure cleanup even if an error occurs
    except KeyboardInterrupt:
        print("\nShutting down server.")
    finally:
        # Close the main server socket to release the port
        server_socket.close()

if __name__ == "__main__":
    # Start the server with default settings (localhost:8000)
    start_server()