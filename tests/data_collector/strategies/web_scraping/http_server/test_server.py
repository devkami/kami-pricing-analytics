import argparse
import http.server
import socketserver
import threading

PORT = 8000


def run_server(directory, port):
    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=directory, **kwargs)

    with socketserver.TCPServer(('', port), Handler) as httpd:
        print(f'Serving {directory} at port {port}')
        httpd.timeout = 1
        while True:
            httpd.handle_request()


def start_http_server(directory='.', port=PORT):
    thread = threading.Thread(
        target=run_server, args=(directory, port), daemon=True
    )
    thread.start()
    return thread


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--directory', '-d', default='.')
    parser.add_argument('--port', '-p', type=int, default=PORT)
    args = parser.parse_args()
    server_thread = start_http_server(args.directory, args.port)
    try:
        while server_thread.is_alive():
            server_thread.join(1)
    except KeyboardInterrupt:
        print('Server is shutting down.')


if __name__ == '__main__':
    main()
