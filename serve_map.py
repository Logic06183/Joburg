import http.server
import socketserver
import webbrowser
import os

# Configure the server
PORT = 8004
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

def serve_maps():
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print("\nPeak Summer LST Maps are now available at:")
        print(f"Early Period (1980-1995): http://localhost:{PORT}/lst_map_1980_1995.html")
        print(f"Mid Period (1995-2010): http://localhost:{PORT}/lst_map_1995_2010.html")
        print(f"Recent Period (2010-2023): http://localhost:{PORT}/lst_map_2010_2023.html")
        
        # Open all maps in browser
        webbrowser.open(f"http://localhost:{PORT}/lst_map_1980_1995.html")
        webbrowser.open(f"http://localhost:{PORT}/lst_map_1995_2010.html")
        webbrowser.open(f"http://localhost:{PORT}/lst_map_2010_2023.html")
        
        print("\nPress Ctrl+C to stop the server")
        httpd.serve_forever()

if __name__ == "__main__":
    serve_maps()
