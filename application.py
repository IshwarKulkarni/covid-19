
"""
Ishwar Kulkarni, 03/31/2020
Kicks off a simple HTTP server.
"""

import socketserver

from server import ImageServerHandler

PORT_NUMBER = 8080

def main():
    """Starting point for this app """
    try:
        server = socketserver.TCPServer(('', 8000), ImageServerHandler)
        print('Started httpserver on port ', PORT_NUMBER)
        server.serve_forever()

    except KeyboardInterrupt:
        print('^C received, shutting down the web server')
        server.socket.close()

if __name__ == "__main__":
    main()
