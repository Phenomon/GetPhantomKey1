#!/usr/bin/env python3
import http.server
import socketserver
import json
import urllib.parse
import os
import uuid
from key_generator import get_or_create_key

PORT = 5000

class CombinedHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        
        if parsed_path.path == '/api/key':
            # Handle API request for key
            # Get user ID from cookie or create new one
            user_id = self.get_user_id()
            
            key = get_or_create_key(user_id)
            
            if key is not None:
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Set-Cookie', f'user_id={user_id}; Path=/; Max-Age=31536000')  # 1 year
                self.end_headers()
                
                response = {'key': key, 'user_id': user_id}
                self.wfile.write(json.dumps(response).encode())
            else:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                response = {'error': 'Failed to generate key'}
                self.wfile.write(json.dumps(response).encode())
        else:
            # Handle static file requests (HTML, CSS, JS, etc.)
            super().do_GET()

    def get_user_id(self):
        """Get user ID from cookie or generate a new one"""
        cookies = self.headers.get('Cookie')
        if cookies:
            for cookie in cookies.split(';'):
                if cookie.strip().startswith('user_id='):
                    return cookie.strip().split('=', 1)[1]
        
        # Generate new user ID if none exists
        return str(uuid.uuid4())

    def end_headers(self):
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()

if __name__ == "__main__":
    os.chdir('.')
    
    httpd = socketserver.TCPServer(("0.0.0.0", PORT), CombinedHandler)
    httpd.allow_reuse_address = True
    httpd.socket.setsockopt(socketserver.socket.SOL_SOCKET, socketserver.socket.SO_REUSEADDR, 1)
    print(f"Server running at http://0.0.0.0:{PORT}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped")
    finally:
        httpd.server_close()
