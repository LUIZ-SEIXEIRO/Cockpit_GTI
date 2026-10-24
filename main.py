# H:\Cockpit_GTI\main.py

from app import app

if __name__ == "__main__":
    print("Iniciando Cockpit GTI em http://localhost:5000")
    app.run(host="0.0.0.0", port=5000, debug=True)