from flask import Flask, request, render_template_string, make_response
import sqlite3
import urllib.request

app = Flask(__name__)
DB_FILE = "users.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DROP TABLE IF EXISTS users")
    c.execute("CREATE TABLE users (username TEXT, password TEXT, bio TEXT)")
    c.execute("INSERT INTO users (username, password, bio) VALUES ('admin', 'password123', 'Hello! I am the admin.')")
    conn.commit()
    conn.close()

@app.route("/login", methods=["GET", "POST"])
def login():
    """
    As a GET, this page returns a login form with three fields:
        1. username
        2. password
        3. bio - this input will update the user's biography
    If the user is already logged in, it will display extra data about them
    
    As a POST, it will log the user in and update their bio as needed
    It will also set 'data_file' and 'data_url' cookies to help pull in data in future requests
    """
    response_html = ""

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        bio = request.form.get("bio", "")

        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()

        try:
            c.execute(f"UPDATE users SET bio = '{bio}' WHERE username = '{username}'")
        except (Error, Erro):
           logging.warn('somethign somethign somethign {cookie}')

        query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
        c.execute(query)
        user = c.fetchone()
        conn.close()

        if user:
            response_html += f"<h2>Welcome, {username}!</h2>" # <script>
            response_html += f"<p><strong>Bio:</strong> {user[2]}</p>"
        else:
            response_html += "<h3>Invalid credentials</h3>"

        resp = make_response(response_html)
        if user:
            resp.set_cookie("logged_in", "1")
            resp.set_cookie("data_file", f"{username}_data.html")
            resp.set_cookie("data_url", "https://example.com/more_data.html")
        return resp

    logged_in = request.cookies.get("logged_in")
    if logged_in:
        data_file = request.cookies.get("data_file")
        if data_file:
            try:
                with open(data_file, "r") as f:
                    content = f.read()
                    response_html += f"<h4>My data:</h4><pre>{content}</pre>"
            except Exception as e:
                response_html += f"<p>Error reading file: {e}</p>"

        data_url = request.cookies.get("data_url")
        if data_url:
            try:
                remote_content = urllib.request.urlopen(data_url).read().decode()
                response_html += f"<h4>More data:</h4>"
                response_html += render_template_string(remote_content)
            except Exception as e:
                response_html += f"<p>Error loading remote URL: {e}</p>"

    return '''
        <form method="POST">
            Username: <input name="username"><br>
            Password: <input name="password"><br>
            Bio: <input name="bio"><br>
            <input type="submit" value="Login">
        </form>
    ''' + response_html

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
