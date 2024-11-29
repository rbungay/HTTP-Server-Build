# Custom HTTP Server Implementation

This project is my personal implementation of an HTTP/1.1 server. The goal was to build a lightweight and efficient HTTP server capable of handling multiple client requests. Through this project, I gained hands-on experience with TCP socket programming, HTTP request handling, and server architecture.

## Overview

The project involves creating a basic HTTP server from scratch. The server processes HTTP requests, handles different HTTP methods (such as GET and POST), and returns appropriate responses. Key objectives of this project include:

- Implementing a functioning HTTP/1.1 server
- Understanding and managing TCP socket connections
- Handling HTTP requests and responses
- Building a server capable of serving multiple clients simultaneously

## Getting Started

To run the HTTP server locally, follow the instructions below:

### Prerequisites

Make sure you have the following installed:

- Python 3.12 or later
- `pipenv` for managing dependencies (optional but recommended)

### Setup

1. **Clone the repository:**

   ````sh
   git clone <your-repo-url>
   cd <your-project-directory>```

   ````

2. **Install dependencies:**

   If you're using pipenv, install the required packages:

   ````sh
   pipenv install```

   ````

3. **Run the server:**
   To start the HTTP server, use the following command:

   `sh pipenv run python3 -m app.main`

   This will launch the server which will begin listening for incoming HTTP requests.

## Project Structure

- **`app/main.py`**: This is the main entry point for the HTTP server. It contains the server logic and handles the core functionality of processing HTTP requests.
- **`requirements.txt`**: This file lists the Python dependencies required for the project. You can use it to easily install all necessary packages.
- **`README.md`**: This file! It provides an overview of the project, setup instructions, and other important information.
- **`.gitignore`**: Specifies which files and directories should be ignored by Git. It ensures that unnecessary files, such as temporary or compiled files, are not included in version control.

## Features

- **HTTP/1.1 Support**: The server fully supports HTTP/1.1 requests, allowing for efficient handling and communication between the client and the server.
- **Multiple Client Handling**: The server is designed to manage multiple client connections at the same time, making it more robust for real-world usage.
- **Basic Request Processing**: The server handles basic HTTP methods such as `GET` and `POST`, allowing for fundamental request processing and response generation.
