#!/bin/bash

# Check if certificate files exist
if [ ! -f "cert.pem" ] || [ ! -f "key.pem" ]; then
    echo ""
    echo "Certificate files not found."
    echo "Generating self-signed SSL certificates..."
    echo ""
    
    # Generate self-signed certificate
    openssl req -x509 -newkey rsa:2048 -keyout key.pem -out cert.pem -days 365 -nodes -subj "/CN=localhost"

    if [ $? -eq 0 ]; then
        echo ""
        echo "Certificates generated."
    else
        echo ""
        echo "Failed to generate certificates."
        exit 1
    fi
else
    echo "Certificate files found."
fi

# Run the Python server
python3 server.py