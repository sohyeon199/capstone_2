from flask import Flask
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    CORS(app)

    # 개별 모듈에서 블루프린트 등록하는 곳
    import controller
    app.register_blueprint(controller.home)

    # 설정
    app.config['JSON_AS_ASCII'] = False
    
    from database import init_db
    init_db()
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=8080)