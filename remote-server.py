import http.server
import socketserver
import subprocess

PORT = 1337  # Choose an available port

class ConfigRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/config':
            try:
                # Use ip6tables-save to get the current configuration
                result = subprocess.run(['ip6tables-save'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True, text=True)
                config_data = result.stdout.encode('utf-8')
                self.send_response(200)
                self.send_header('Content-type', 'application/octet-stream')
                self.end_headers()
                self.wfile.write(config_data)
            except subprocess.CalledProcessError as e:
                self.send_error(500, f'Failed to retrieve ip6tables configuration: {e.stderr}')
        else:
            self.send_error(404, 'Endpoint not found')

    def do_POST(self):
        if self.path == '/config':
            content_length = int(self.headers['Content-Length'])
            new_config = self.rfile.read(content_length).decode('utf-8')
            try:
                # Use ip6tables-restore to apply the new configuration
                subprocess.run(['ip6tables-restore'], input=new_config, text=True, check=True)
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b'Configuration updated successfully')
            except subprocess.CalledProcessError as e:
                self.send_error(500, f'Failed to update ip6tables configuration: {e.stderr}')
        else:
            self.send_error(404, 'Endpoint not found')

if __name__ == '__main__':
    with socketserver.TCPServer(('', PORT), ConfigRequestHandler) as httpd:
        print(f'Serving on port {PORT}')
        httpd.serve_forever()
