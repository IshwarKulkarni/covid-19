"""
Ishwar Kulkarni, 03/31/2020
One really simple server that's unsecure af
"""
import http.server
import io
import sys

from covid_dataset import load_db
from vizualization import draw_charts

class ImageServerHandler(http.server.SimpleHTTPRequestHandler):
    """Simple server that serves up and HMLT image with 1 image of the charts"""

    def parse_query(self):
        """Making sense of the http GET path"""
        path = self.path
        path = path.replace('%20', ' ').lower().split('&')
        q_county, q_state, q_days = None, None, None
        for pth in path:
            if 'county' in pth:
                q_county = pth.split('=')
                if len(q_county) > 1:
                    q_county = q_county[1]
            elif 'state' in pth:
                q_state = pth.split('=')
                if len(q_state) > 1:
                    q_state = q_state[1]
            if 'days' in pth:
                q_days = pth.split('=')
                if len(q_days) > 1:
                    q_days = q_days[1]

        if q_county and q_county.upper() in ['NONE', 'NIL', '']:
            q_county = None

        if q_state and q_state.upper() in ['NONE', 'NIL', '']:
            q_state = None

        return q_county, q_state, q_days

    def do_GET(self):
        if not hasattr(self, 'con'):
            self.con = load_db()

        if self.path.endswith('.png'):
            header = self.send_head()
            self.copyfile(header, self.wfile)
            header.close()
            return

        path = None
        q_county, q_state, q_days = self.parse_query()
        try:
            path = draw_charts(self.con, q_county, q_state, q_days)
        except:
            self.send_error(500)
            return

        if not path:
            self.send_error(404)
            return

        html = self.send_html(path)
        self.copyfile(html, self.wfile)
        html.close()
        return


    def send_html(self, path):
        """"Write a bare bones HTML to embed image"""
        enc = sys.getfilesystemencoding()
        encoded =\
f"""
<html>
    <body>
        <br> <img src=\'{path}\'>
    </body>
</html>
""".encode(enc)
        msg = io.BytesIO()
        msg.write(encoded)
        msg.seek(0)
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=%s" % enc)
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        return msg
