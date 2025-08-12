# StudentTesting/scripts/server.py
from http.server import BaseHTTPRequestHandler, HTTPServer
import sqlite3
from urllib.parse import urlparse, parse_qs
import html
import logging
from config import SERVER_CONFIG, VULNERABILITIES

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='server.log'
)
logger = logging.getLogger(__name__)

class VulnerableRequestHandler(BaseHTTPRequestHandler):
    """Deliberately vulnerable HTTP handler for educational purposes"""
    
    # Initialize fake database
    def init_db(self):
        self.conn = sqlite3.connect(':memory:')
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE users (
                id INTEGER PRIMARY KEY,
                username TEXT,
                password TEXT
            )
        ''')
        self.cursor.execute("INSERT INTO users VALUES (1, 'admin', 'password123')")
        self.cursor.execute("INSERT INTO users VALUES (2, 'user', 'qwerty')")
        self.conn.commit()

    # Handle GET requests
    def do_GET(self):
        parsed_path = urlparse(self.path)
        endpoint = parsed_path.path
        
        # Route handling
        if endpoint == '/':
            self.serve_file('html/index.html')
        elif endpoint == '/login':
            self.serve_file('html/login.html')
        elif endpoint == '/dashboard':
            self.handle_dashboard(parsed_path.query)
        elif endpoint == '/search':
            self.handle_search(parsed_path.query)
        else:
            self.send_error(404, "Not Found")

    # Serve static files
    def serve_file(self, filename):
        try:
            with open(filename, 'rb') as f:
                content = f.read()
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(content)
        except FileNotFoundError:
            self.send_error(404, "File Not Found")

    # Vulnerable login handler (SQLi vulnerable)
    def handle_dashboard(self, query):
        params = parse_qs(query)
        username = params.get('username', [''])[0]
        password = params.get('password', [''])[0]

        # Deliberately vulnerable SQL query
        if VULNERABILITIES['SQL_INJECTION']:
            query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
            logger.warning(f"Executing vulnerable query: {query}")
            try:
                self.cursor.execute(query)
                user = self.cursor.fetchone()
            except sqlite3.Error as e:
                logger.error(f"SQL Error: {e}")
                user = None
        else:
            # Secure version
            query = "SELECT * FROM users WHERE username=? AND password=?"
            self.cursor.execute(query, (username, password))
            user = self.cursor.fetchone()

        if user:
            response = f"""
            <html>
            <body>
                <h2>Welcome {html.escape(user[1])}!</h2>
                <p>You have successfully logged in.</p>
                <p><a href="/">Back to Home</a></p>
            </body>
            </html>
            """
        else:
            response = """
            <html>
            <body>
                <h2>Login Failed</h2>
                <p>Invalid username or password</p>
                <p><a href="/login">Try Again</a></p>
            </body>
            </html>
            """
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(response.encode())

    # XSS vulnerable search handler
    def handle_search(self, query):
        params = parse_qs(query)
        search_term = params.get('q', [''])[0]
        
        response = f"""
        <html>
        <body>
            <h2>Search Results</h2>
            <p>You searched for: {search_term}</p>
            <p><a href="/">Back to Home</a></p>
        </body>
        </html>
        """
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(response.encode())

def run_server():
    """Start the vulnerable server"""
    server_address = (SERVER_CONFIG['HOST'], SERVER_CONFIG['PORT'])
    httpd = HTTPServer(server_address, VulnerableRequestHandler)
    
    # Initialize fake database
    httpd.RequestHandlerClass().init_db()
    
    logger.info(f"Starting vulnerable server on {SERVER_CONFIG['HOST']}:{SERVER_CONFIG['PORT']}")
    print(f"Server running at http://{SERVER_CONFIG['HOST']}:{SERVER_CONFIG['PORT']}")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    finally:
        httpd.server_close()

if __name__ == '__main__':
    run_server()