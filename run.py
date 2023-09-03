from app.routes import create_app

app = create_app()

# Check if the script is the main entry point
if __name__ == "__main__":
    app.run(debug=True)  # Run the Flask application with debugging enabled
