#!/usr/bin/env python3
import http.server
import socketserver
import json
import urllib.parse
from key_generator import get_or_create_key

PORT = 8000

class APIHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        
        if parsed_path.path == '/api/key':
            # Get the key from the database
            key = get_or_create_key()
            
            if key:
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                response = {'key': key}
                self.wfile.write(json.dumps(response).encode())
            else:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                response = {'error': 'Failed to generate key'}
                self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.end_headers()

if __name__ == "__main__":
    with socketserver.TCPServer(("0.0.0.0", PORT), APIHandler) as httpd:
        httpd.allow_reuse_address = True
        print(f"API server running at http://0.0.0.0:{PORT}")
        httpd.serve_forever()
