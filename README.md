# Simple HTTPS Server

A simple HTTPS server built from scratch in Python using only the standard library!

---

## What It Does

- Accepts encrypted HTTPS connections over SSL/TLS
- Routes requests to different pages based on the URL path
- Returns proper HTTP responses with correct status codes
- Logs every request to both the terminal and a log file
- Handles malformed requests and unknown paths gracefully

---

## How It Works

Each incoming request is:

1. Received as raw bytes over a TCP connection
2. Decrypted by the SSL layer
3. Parsed to extract the HTTP method and path
4. Routed to the correct handler function
5. Responded to with a full HTTP response string


---

## Project Structure

```
simple-https-server/
├── server.py       # Main server 
├── cert.pem        # SSL certificate (you generate this)
├── key.pem         # SSL private key (you generate this)
├── server.log      # Request log (created automatically on first run)
└── README.md
```

---

## Setup and Usage

### Run with the startup script (recommended)

`script.sh` checks whether `cert.pem` and `key.pem` already exist, generates them automatically if not, then starts the server.

```bash
chmod +x script.sh
./script.sh
```
No manual certificate setup is needed.


### OR Run manually

**1. Generate a self-signed SSL certificate**

```bash
openssl req -x509 -newkey rsa:2048 -keyout key.pem -out cert.pem -days 365 -nodes
```

**2. Start the server**

```bash
python3 server.py
```

### Open in your browser

```
https://127.0.0.1:8443
```

Your browser will show a security warning because the certificate is self-signed, not issued by a trusted authority. Click "Advanced" and proceed. The connection is still encrypted!

---

## Logging

Every request is logged to `server.log` and printed to the terminal.

Log levels used:
- `INFO` — successful requests
- `WARNING` — malformed requests (client's fault)
- `ERROR` — unexpected server-side failures

---

## What I Learned

**How HTTPS actually works**  
By wrapping a plain TCP socket with Python's `ssl` module, it becomes clear that HTTPS is just HTTP running inside a TLS encryption layer. The server needs a certificate to prove its identity and a private key for encryption.

**How HTTP is structured**  
HTTP requests and responses are plain text with a specific format: a status/request line, headers, a blank line, then an optional body. Writing `build_response()` on my own made this concrete.

**Error handling and status codes**  
There's a meaningful difference between 400, 404, and 405. Returning the right code matters for clients and debugging.

**Structured logging**  
Using Python's `logging` module instead of `print()` means log messages have severity levels and can be written to a file automatically.

---

## Requirements

- Python 3.x
- OpenSSL (for generating certificates)
- Bash (for running `script.sh`)