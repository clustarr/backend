from main import app


# command to run app in production:
# gunicorn --bind 0.0.0.0:5000 wsgi:app

if __name__ == "__main__":
    app.run()
