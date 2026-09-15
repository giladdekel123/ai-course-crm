from flask import Flask
from flask_wtf import CSRFProtect

from app.config import Config


def create_app(config_class: type = Config) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_class)

    CSRFProtect(app)

    from app.blueprints.courses.routes import bp as courses_bp
    from app.blueprints.dashboard.routes import bp as dashboard_bp
    from app.blueprints.leads.routes import bp as leads_bp
    from app.blueprints.predictions.routes import bp as predictions_bp

    app.register_blueprint(dashboard_bp)
    app.register_blueprint(leads_bp)
    app.register_blueprint(courses_bp)
    app.register_blueprint(predictions_bp)

    @app.template_filter("currency")
    def currency_filter(value):
        return f"${value:,.2f}" if value is not None else "-"

    @app.template_filter("date")
    def date_filter(value):
        return value.split("T")[0] if value else "-"

    return app
