# run.py
from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True) # debug=True para desarrollo, cambiar a False en producción
