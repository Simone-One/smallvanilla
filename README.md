# SmallVanilla Social App

A simple social media web application with a Minecraft-inspired theme, built with Python and Flask.

## Key Features Implemented

*   User registration and login (with session management)
*   Password hashing for security
*   Post creation by authenticated users
*   Dynamic display of all posts on the homepage
*   AJAX-powered forms for smoother user experience (login, registration, post creation)
*   Basic responsive styling using a shared CSS file
*   Placeholder pages for Account and Notifications (login required)
*   SQLite database for data persistence

## Setup and Run

1.  **Prerequisites:**
    *   Python 3.x
    *   pip (Python package installer)

2.  **Clone the repository (if you haven't already):**
    ```bash
    git clone <repository_url>
    cd <repository_directory>
    ```

3.  **Install dependencies:**
    While this project doesn't have a `requirements.txt` yet, the core dependencies are Flask and Flask-SQLAlchemy. If you were setting this up in a fresh environment, you'd typically do:
    ```bash
    pip install Flask Flask-SQLAlchemy Werkzeug
    ```
    (Werkzeug is for password hashing, usually a Flask dependency).

4.  **Initialize the Database:**
    The application uses SQLite. To set up the `site.db` database file and create the necessary tables for the first time, run the `app.py` script directly with a specific intention if designed (or ensure it creates tables if not present). Based on the current `app.py` structure, running it might attempt to create tables if the `create_tables()` function is called appropriately (e.g., within an `if __name__ == '__main__':` block that also handles table creation before running the app, or if a separate CLI command was added for it).

    For this project, assuming `create_tables()` is called within `app.py` before `app.run()` when `app.py` is executed directly:
    ```bash
    python app.py 
    ```
    *Wait for it to indicate tables are created or for the app to start, then stop it (Ctrl+C) if it started the server. The main goal here is table creation.*
    *(Alternatively, if a Flask CLI command `flask init-db` was defined, that would be used here.)*

5.  **Run the Application:**
    To start the Flask development server:
    ```bash
    flask run
    ```
    If the Flask CLI is not available or configured, you might run it directly if `app.py` includes `app.run(debug=True)`:
    ```bash
    python app.py
    ```
    The application will typically be available at `http://127.0.0.1:5000/`.

## Project Structure

*   `app.py`: Main Flask application, routes, and database models.
*   `static/`: Contains static files (like `style.css`).
*   `templates/`: Contains HTML templates.
*   `site.db`: SQLite database file (created after initialization).