# smallvanilla

## How to Run

To get this application running locally, follow these steps:

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/user/smallvanilla.git
    cd smallvanilla
    ```

2.  **Create and Activate a Virtual Environment (Recommended):**
    *   **For macOS/Linux:**
        ```bash
        python3 -m venv venv
        source venv/bin/activate
        ```
    *   **For Windows:**
        ```bash
        python -m venv venv
        .\venv\Scripts\activate
        ```

3.  **Install Dependencies:**
    Make sure your virtual environment is activated, then run:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Initialize the Database (First Time Setup):**
    The application is set up to create the database and tables automatically if they don't exist when the app starts. If you need to manually ensure this or reset it, you can do so from a Python shell within the activated virtual environment:
    ```python
    from app import app, db
    with app.app_context():
        db.create_all()
    print("Database initialized!")
    ```
    *Note: For development, running the app (next step) usually handles this automatically.*


5.  **Run the Application:**
    Once the dependencies are installed, you can start the Flask development server:
    ```bash
    flask run
    ```
    Alternatively, you can run it using `python app.py` if `app.py` is configured to run the app (e.g., `if __name__ == '__main__': app.run(debug=True)`). The current `app.py` should support this.

6.  **Access the Application:**
    Open your web browser and go to:
    [http://127.0.0.1:5000/](http://127.0.0.1:5000/)

    You should see the homepage of the SmallVanilla application.

---

**Note on `flask run` vs `python app.py`:**
- `flask run` is the standard way to run Flask development servers. It will automatically detect your `app.py` (or what's set in `FLASK_APP` environment variable).
- `python app.py` works if your `app.py` contains the `app.run()` conditional block. The current `app.py` created by the worker should have this.
