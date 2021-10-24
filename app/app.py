from flask import Flask
from flask.json import JSONEncoder
from flask_request_id_header.middleware import RequestID
from flask_cors import CORS
from app.util.app_logging import get_logger, init_logger
from app.config.app_config import conf
from datetime import datetime
from flask_wtf import CSRFProtect

# blueprints
from app.blueprints.core import bp as coreBp
# from app.blueprints.user import bp as userBp
# from app.blueprints.internal import bp as internalBp


logger = get_logger(__name__)


app = Flask(__name__)
app.secret_key = conf.APP_SECRET  # for the csrf to work
init_logger(app=app)
CSRFProtect(app)
# app.json_encoder = some custom json encoder... (to deal with some datetime issues)


class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        try:
            if isinstance(obj, datetime):
                return obj.isoformat()
            iterable = iter(obj)
        except TypeError:
            pass
        else:
            return list(iterable)
        return JSONEncoder.default(self, obj)


app.config["REQUEST_ID_UNIQUE_VALUE_PREFIX"] = ""
RequestID(app)
CORS(app, resources={r"/api/*": {"origins": conf.CORS_ALLOWED_ORIGINS}})

app.json_encoder = CustomJSONEncoder


app.register_blueprint(coreBp)
# app.register_blueprint(userBp)
# app.register_blueprint(internalBp)

