#!/usr/bin/env python3
import http.server
import json
import urllib.parse
import uuid
from key_generator import get_or_create_key

class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        
        if parsed_path.path == '/api/key':
            self.handle_api_key()
        else:
            super().do_GET()

    def handle_api_key(self):
        # Get user ID from cookie or create new one
        user_id = self.get_user_id()
        
        key = get_or_create_key(user_id)
        
        if key is not None:
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Set-Cookie', f'user_id={user_id}; Path=/; Max-Age=31536000')
            self.end_headers()
            
            response = {'key': key, 'user_id': user_id}
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            response = {'error': 'Failed to generate key'}
            self.wfile.write(json.dumps(response).encode())

    def get_user_id(self):
        cookies = self.headers.get('Cookie')
        if cookies:
            for cookie in cookies.split(';'):
                if cookie.strip().startswith('user_id='):
                    return cookie.strip().split('=', 1)[1]
        
        return str(uuid.uuid4())

if __name__ == "__main__":
    import socketserver
    import os
    
    PORT = 5000
    os.chdir('.')
    
    with socketserver.TCPServer(("0.0.0.0", PORT), CustomHandler) as httpd:
        httpd.allow_reuse_address = True
        print(f"Server running at http://0.0.0.0:{PORT}")
        httpd.serve_forever()
