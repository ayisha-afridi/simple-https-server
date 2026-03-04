import socket
import ssl
import logging

# Configure logging system
# Logs are written to server.log  
logging.basicConfig(
    level = logging.INFO, 
    format = '%(asctime)s [%(levelname)s] %(message)s',
    handlers = [
        logging.FileHandler("server.log"),  # Write to file 
        logging.StreamHandler()             # Print to terminal
    ]
)
logger = logging.getLogger(__name__)


# HTTP responses 
def build_response(status_code, status_text, body):
    headers = (
        f"HTTP/1.1 {status_code} {status_text}\r\n"
        f"Content-Type: text/html\r\n"
        f"Content-Length: {len(body.encode('utf-8'))}\r\n"
        f"\r\n"
    )
    return headers + body

def response_200(body):
    # 200 means "OK", the request was successful
    return build_response(200, "OK", body)

def response_400():
    # 400 means "Bad Request", the request was malformed
    return build_response(400, "Bad Request", "<html><body><h1>400 Bad Request</h1></body></html>")

def response_404(path):
    # 404 means "Not Found", the requested resource could not be found
    return build_response(404, "Not Found", f"<html><body><h1>404 Not Found</h1><p>No resource found at {path}</p></body></html>")

def response_405():
    # 405 means "Method Not Allowed", the request method is not supported
    return build_response(405, "Method Not Allowed", "<html><body><h1>405 Method Not Allowed</h1></body></html>")

# Route handling
def handle_home(method, path):
    if method == "GET":
        return response_200("<html><body><h1>Welcome to the Home Page</h1></body></html>")
    else:
        return response_405()
    
def handle_about(method, path):
    if method == "GET":
        return response_200("<html><body><h1>About</h1><p>This is a simple HTTPS server built from scratch in Python</p></body></html>")
    else:
        return response_405()

def handle_status(method, path):
    if method == "GET":
        return response_200("<html><body><h1>Status</h1><p>The server is running smoothly.</p></body></html>")
    else:
        return response_405()

        
# Routing
# Map URLs to their handler functions
ROUTES = {
    "/": handle_home,
    "/about": handle_about,
    "/status": handle_status
}

def route_request(method, path):
    # Find the right handler function for the given path
    handler = ROUTES.get(path)
    if handler:
        # If the path is found, call the handler function and return its response
        return handler(method, path)
    else:
        # If no path is found, return a 404 response
        return response_404(path)
    

# Request Parsing
def parse_request(request_data):

    if not request_data.strip():
        raise ValueError("Empty Request")

    # Split the request into lines
    lines = request_data.split('\n')

    # Get the request method, path, and protocol from the first line
    parts = lines[0].split()

    if len(parts) != 3:
        raise ValueError("Invalid request line")

    method, path, _ = parts
    path = path.split('?')[0]  # Remove query parameters
    return method, path

# Client handling
def handle_client(client_socket, client_address):

    try:
        # Receive data from the client
        request_data = client_socket.recv(4096).decode('utf-8')

        # Try to parse the request into a method and path
        try:
            method, path = parse_request(request_data)
        except ValueError as e:
            # The request was malformed, respond with 400 Bad Request
            logger.warning(f"{client_address} - Bad request: {e}")
            client_socket.sendall(response_400().encode('utf-8'))
            return

        # Route the request to the correct handler
        response = route_request(method, path)

        # Determine the status code, check if the path exists in the routes
        if path not in ROUTES:
            status = "404"
        elif method != "GET":
            status = "405"
        else:
            status = "200"

        logger.info(f"{client_address} - {method} {path} - {status}")

        # Send response back to client, ensuring strings are encoded to bytes before transmission
        client_socket.sendall(response.encode('utf-8'))

    except Exception as e:
        # Catch unexpected errors so that a bad client cannot crash the entire server
        logger.error(f"Error handling client {client_address}: {e}")
    
    finally:
        # Always close the client socket 
        client_socket.close()

# Server
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
    except Exception:
        logger.error("Certificate files not found.")
        server_socket.close()
        return

    # Wrap the socket with SSL/TLS encryption so it encrypts all data transmission
    secure_socket = context.wrap_socket(server_socket, server_side=True)
    logger.info(f"Server listening on https://{host}:{port}")
    
    try:
        # Continuously listen for incoming client connections
        while True:
            try:
                # Accept a connection from a client
                client_socket, client_address = secure_socket.accept()
                handle_client(client_socket, client_address)

            except Exception as e:
                logger.error(f"Error accepting connection: {e}")

    except KeyboardInterrupt:
        logger.info("Shutting down server.")

    finally:
        secure_socket.close()

if __name__ == "__main__":
    # Start the server with default settings (localhost:8443)
    start_server()

