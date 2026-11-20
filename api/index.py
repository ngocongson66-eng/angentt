import os
import sys
import json
import urllib.parse
import traceback
from http.server import BaseHTTPRequestHandler

# Đảm bảo thư mục gốc dự án nằm trong sys.path để import server và src
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)
try:
    os.chdir(root_dir)
except Exception:
    pass

from server import RequestHandler

class handler(RequestHandler):
    """
    Entrypoint Serverless Function chuẩn mực dành riêng cho Vercel (@vercel/python).
    Kế thừa RequestHandler của server.py và hỗ trợ rewrite URL thông minh.
    """
    def get_real_path(self):
        # Vercel truyền URL gốc của người dùng qua các header x-forwarded-uri hoặc x-matched-path
        real = (
            self.headers.get("x-forwarded-uri")
            or self.headers.get("x-matched-path")
            or self.headers.get("x-vercel-matched-path")
            or self.path
        )
        return real

    def do_GET(self):
        try:
            real_path = self.get_real_path()
            if real_path and real_path not in ["/api/index.py", "/api/index", "/api"]:
                self.path = real_path
            elif self.path in ["/api/index.py", "/api/index", "/api"]:
                self.path = "/"
            return super().do_GET()
        except Exception as e:
            traceback.print_exc()
            self.send_response(500)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write(f"500 Internal Server Error:\n{traceback.format_exc()}".encode("utf-8"))

    def do_POST(self):
        try:
            real_path = self.get_real_path()
            if real_path and real_path not in ["/api/index.py", "/api/index", "/api"]:
                self.path = real_path
            return super().do_POST()
        except Exception as e:
            traceback.print_exc()
            self.send_response(500)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            err_json = json.dumps({"error": str(e), "traceback": traceback.format_exc()})
            self.wfile.write(err_json.encode("utf-8"))

    def do_OPTIONS(self):
        return super().do_OPTIONS()

    def do_HEAD(self):
        try:
            real_path = self.get_real_path()
            if real_path and real_path not in ["/api/index.py", "/api/index", "/api"]:
                self.path = real_path
            elif self.path in ["/api/index.py", "/api/index", "/api"]:
                self.path = "/"
            return super().do_HEAD()
        except Exception:
            return super().do_HEAD()

# Export alias tương thích cả hai kiểu nhận diện của Vercel
app = handler
