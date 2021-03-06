import os

from flask import Flask


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True) # instance/ の中にある config.py を読み込めるようになる
    app.config.from_mapping(
        # APPLICATION_ROOT="/tuat-syllabus/",
        SECRET_KEY="dev",
        DATABASE=os.path.join(app.instance_path, "temp.sqlite3")
    )

    if test_config is None:
        app.config.from_pyfile("config.py", silent=True)
    else:
        app.config.update(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    from app import search, course
    app.register_blueprint(search.bp)
    app.register_blueprint(course.bp)

    # app.add_url_rule("/", endpoint="search")
    
    return app