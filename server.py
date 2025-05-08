import http.server
import socketserver
import os
import cgi

def find_circuitpy():
    from string import ascii_uppercase
    for drive in ascii_uppercase:
        path = f"{drive}:\\"
        if os.path.exists(os.path.join(path, "code.py")):
            return path
    return None

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        ctype, pdict = cgi.parse_header(self.headers.get("content-type"))
        if ctype == "multipart/form-data":
            pdict["boundary"] = bytes(pdict["boundary"], "utf-8")
            pdict["CONTENT-LENGTH"] = int(self.headers["content-length"])
            fields = cgi.parse_multipart(self.rfile, pdict)
            uploaded = fields["file"][0]
            filename = self.headers.get("X-Filename", "uploaded_file.bin")

            dest = find_circuitpy()
            if dest:
                try:
                    with open(os.path.join(dest, filename), "wb") as f:
                        f.write(uploaded)
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(b"Saved to CIRCUITPY")
                except Exception as e:
                    self.send_response(500)
                    self.end_headers()
                    self.wfile.write(f"Error writing file: {e}".encode())
            else:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(b"CIRCUITPY not found")
        else:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Invalid upload type")

PORT = 8000
with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print("Serving at port", PORT)
    httpd.serve_forever()
