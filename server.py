import socket
import ssl

def start_server(host='127.0.0.1', port=8443):
    # Create a TCP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # Allow the socket to reuse a local address right after the socket is closed 
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    # Bind socket to host and port
    # Specify where the server should listen for incoming network requests
    server_socket.bind((host, port))
    
    # Listen for incoming connections, queuing up to 5
    server_socket.listen(5)

    # Set up SSL with secure default settings
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)

    # Load the server's certificate and private key
    # The certificate (public key) authenticates the server's identity to the clients
    # The private key is used to decrypt data that's encrypted with the public key
    try:
        context.load_cert_chain(certfile="cert.pem", keyfile="key.pem")
    except Exception as e:
        print(f"Error: Certificate files not found.")
        server_socket.close()
        return

    # Wrap the socket with SSL/TLS encryption so it encrypts all data transmission
    secure_socket = context.wrap_socket(server_socket, server_side=True)

    # If everything is successful, print the server address
    print(f"Server listening on https://{host}:{port}")
    
    try:
        # Continuously listen for incoming client connections
        while True:
            # Initialize client_socket 
            client_socket = None

            try:
                # Accept a connection from a client
                client_socket, client_address = secure_socket.accept()
                print(f"Connection from {client_address}")

                # Receive data from client (up to 1024 bytes)
                # recv() returns bytes, so we must decode it into a unicode string
                request_data = client_socket.recv(1024).decode('utf-8')
                print(f"Request:\n{request_data}\n")

                # HTTP request information:
                # 1) Request line: HTTP method, path, HTTP version used to send request
                # 2) Header (contains metadata about the request)
                # 3) Optional body message (not in GET requests)

                # Parse the first line to get the requested method and path
                request_lines = request_data.split('\n')
                first_line = request_lines[0]
                method, path, protocol = first_line.split()
                
                print(f"Method: {method}, Path: {path}")
                
                # HTTP response
                response_body = f"""
                <html>
                <head><title>My HTTPS Server</title></head>
                <body>
                    <h1>Hello!</h1>
                    <p>This connection is encrypted using SSL/TLS</p>
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

            except Exception as e:
                # Catch any exceptions that occur while handling the client
                print(f"Error handling client: {e}")
            finally:
                # Close the client connection
                if client_socket:
                    client_socket.close()

    # Ensure cleanup even if an error occurs
    except KeyboardInterrupt:
        print("\nShutting down server.")
    finally:
        # Close the main server socket to release the port
        secure_socket.close()

if __name__ == "__main__":
    # Start the server with default settings (localhost:8443)
    start_server()

# Generate self-signed certificate 
# openssl req -x509 -newkey rsa:2048 -keyout key.pem -out cert.pem -days 365 -nodes
