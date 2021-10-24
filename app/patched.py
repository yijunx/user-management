def get_patched_app():
    from gevent import monkey
    from psycogreen.gevent import patch_psycopg

    monkey.patch_all()
    patch_psycopg()
    from app.app import app

    return app


app = get_patched_app()
