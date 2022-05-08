from website import create_app
from ml import init_ml_models


init_ml_models()
app = create_app()


if __name__=='__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
