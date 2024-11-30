from typing import Tuple, Optional, Union, List
import socket  # noqa: F401
import threading
import sys
import os
import gzip

class HTTPServer:

    def __init__(self, host: str = 'localhost', port: int = 4221) -> None:
        self.host: str = host
        self.port: int = port
        self.files_directory: Optional[str] = None #To store directory path for file operations.

    def handle_file_operations(self,
        file_path: str,
        mode: str ='rb',
        data: Optional[Union[str, bytes]]= None) -> Optional[Union[Tuple[int,bytes], bool]]:
        """Handle both reading and writing operations"""

        try:
            # To read a file
            if mode == 'rb':
                with open(file_path, mode) as file:
                    file_size: int = os.stat(file_path).st_size
                    file_data: bytes = file.read()
                return file_size, file_data
            # To writing a file
            elif mode == 'wb':
                with open(file_path, mode) as file:
                    # Convert string to bytes if necessary
                    file_data: bytes = data.encode('utf-8') if isinstance(data, str) else data
                    file.write(file_data)
                return True
        except Exception as e:
            print(f'File operation error: {e}')
            return None


    def extract_user_agent(self, request: bytes) -> str:
        """Extract User-Agent from request headers"""
        headers: List[str] = request.decode('utf-8').split('\r\n')
        for header in headers:
            if header.startswith('User-Agent:'):
                return header.split(': ')[1]
        return ''



    def process_get_request(self,
        decoded_request: List[str],
        file_path: str,
        request: bytes) -> bytes:
        #Root path
        if decoded_request[1] == '/':
            return b"HTTP/1.1 200 OK\r\n\r\n"

        #Echo path
        elif 'echo' in decoded_request[1]:
            #Extract echo content
            echo_endpoint: str = decoded_request[1].split('/')[2]
            response = (
                f'HTTP/1.1 200 OK\r\n'
                f'Content-Type: text/plain\r\n'
                f'Content-Length: {len(echo_endpoint)}\r\n\r\n'
                f'{echo_endpoint}'
            )
            return response.encode('utf-8')

        #user-agent path
        elif "user-agent" in decoded_request[1]:
            user_agent = self.extract_user_agent(request)
            response = (
                f"HTTP/1.1 200 OK\r\n"
                f"Content-Type: text/plain\r\n"
                f"Content-Length: {len(user_agent)}\r\n\r\n"
                f"{user_agent}"
            )
            return response.encode('utf-8')

        #file requests path
        elif 'files' in decoded_request[1] and os.path.exists(file_path):
            file_size, file_data = self.handle_file_operations(file_path)
            response = (
                b"HTTP/1.1 200 OK\r\n"
                b"Content-Type: application/octet-stream\r\n"
                f"Content-Length: {file_size}\r\n\r\n".encode('utf-8')
            ) + file_data
            return response

        # Return 404 if no matching endpoint
        return b'HTTP/1.1 404 Not Found\r\n\r\n'

    def process_post_request(
        self,
        decoded_request: List[str],
        request: bytes,
        file_path: str
    )-> bytes:

        if 'files' in decoded_request[1]:
            position = request.find(b'\r\n\r\n')
            body = request[position + 4:]
            # Write file as bytes and return success response
            self.handle_file_operations(file_path, 'wb', body)
            return b"HTTP/1.1 201 Created\r\n\r\n"
        return b"HTTP/1.1 404 Not Found\r\n\r\n"


    def handle_gzip_encoding(
        self,
        response: Union[bytes, str],
        request: bytes) -> bytes:
        """Compress response with gzip if client supports it"""
        if b"Accept-Encoding" not in request or b"gzip" not in request:
            return response if isinstance(response, bytes) else response.encode('utf-8')

        try:
            # If response is already bytes, try to decode it
            if isinstance(response, bytes):
                header_part, body_part = response.split(b"\r\n\r\n", 1)
                header_part = header_part.decode('utf-8')
                compressed_data = gzip.compress(body_part)
            else:
                header_part, body_part = response.split("\r\n\r\n", 1)
                compressed_data = gzip.compress(body_part.encode('utf-8'))

            # Update Content-Length for compressed data
            updated_file_size = len(compressed_data)
            header_lines = header_part.split("\r\n")
            header_part = "\r\n".join(
                line if not line.startswith("Content-Length:")
                else f"Content-Length: {updated_file_size}"
                for line in header_lines
            )
            # Add gzip encoding header
            header_part += "\r\nContent-Encoding: gzip"

            # Combine headers with compressed body
            return f"{header_part}\r\n\r\n".encode('utf-8') + compressed_data
        except Exception as e:
            print(f"Compression error: {e}")
            return response

    def handle_client(self, client_socket) -> None:
        try:
            request = client_socket.recv(1024)
            decoded_request = request.decode("utf-8").split()
            # Construct file path for file operations
            # Validate directory path
            if not self.files_directory:
                raise ValueError("Files directory not set")
            file_path = os.path.join(self.files_directory, decoded_request[1].split("/")[-1])

            # Route request based on HTTP method
            if decoded_request[0] == "GET":
                response = self.process_get_request(decoded_request, file_path, request)
            elif decoded_request[0] == "POST":
                response = self.process_post_request(decoded_request, request, file_path)
            else:
                response = b"HTTP/1.1 405 Method Not Allowed\r\n\r\n"

            # Apply gzip compression if supported
            response = self.handle_gzip_encoding(response, request)
            client_socket.send(response)
        except Exception as e:
            print(f"Error handling client request: {e}")
            client_socket.send(b"HTTP/1.1 500 Internal Server Error\r\n\r\n")
        finally:
            client_socket.close()

    def start(self):
        #Start HTTP Server and listen for connections
        # Validate command line arguments
        if len(sys.argv) < 2:
            raise ValueError("Files directory not provided")

        self.files_directory = sys.argv[-1]
        if not os.path.isdir(self.files_directory):
            raise NotADirectoryError("Invalid directory path")

        server_socket = socket.create_server((self.host, self.port), reuse_port=True)

        try:
            while True:
                # Accept new client connections
                client_socket, _ = server_socket.accept()
                # Create new thread for each client
                client_thread = threading.Thread(
                    target=self.handle_client,
                    args=(client_socket,)
                )
                client_thread.start()
        except KeyboardInterrupt:
            print("\nShutting down server...")
            server_socket.close()


def main():
    server = HTTPServer()
    server.start()

if __name__ == "__main__":
    main()
