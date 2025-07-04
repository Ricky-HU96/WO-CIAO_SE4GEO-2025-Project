import os
import json
from flask import Flask, render_template, request, jsonify
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError, ProgrammingError
from flask_sqlalchemy import SQLAlchemy    
from geoalchemy2 import Geometry

# 导入数据处理函数
from combined_air_quality_measurements import run_integration
from load_to_db import run_db_load

# --- 1. 初始化扩展，但不绑定到特定的 app ---
# 这允许我们在之后创建和配置 app 实例
db = SQLAlchemy()
CONFIG_FILE = os.path.join(os.path.dirname(__file__),'config.json')

# --- 2. 创建数据库模型 (保持不变) ---
class Measurement(db.Model):
    __tablename__ = 'air_quality_measurements'
    idsensore = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime(timezone=True), primary_key=True)
    nomestazione = db.Column(db.String)
    pollutant = db.Column(db.String)
    measurement_value = db.Column(db.Float)
    geometry = db.Column(Geometry(geometry_type='POINT', srid=4326))


# --- 3. 创建应用工厂函数 ---
def create_app():
    """
    创建并配置 Flask 应用实例。
    """
    app = Flask(__name__)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # 动态从 config.json 加载数据库配置
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
            db_uri = (
                f"postgresql://{config['user']}:{config['password']}@"
                f"{config['host']}:{config.get('port', '5432')}/{config['dbName']}"
                f"?client_encoding=utf8"
            )
            app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
        except (KeyError, FileNotFoundError):
            print(f"Warning: '{CONFIG_FILE}' is missing or invalid. Database will not be configured.")
            app.config['SQLALCHEMY_DATABASE_URI'] = None
    else:
        print(f"Warning: '{CONFIG_FILE}' not found. Database will not be configured.")
        app.config['SQLALCHEMY_DATABASE_URI'] = None

    # --- 4. 将扩展绑定到 app 实例 ---
    # 这个操作现在只在应用创建时执行一次
    db.init_app(app)

    # --- 5. 在工厂函数内部定义路由 ---
    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/dashboard')
    def dashboard_page():
        return render_template('dashboard.html')

    @app.route('/api/pollutants', methods=['GET'])
    def get_pollutant_types():
        if not app.config.get('SQLALCHEMY_DATABASE_URI'):
             return jsonify({"error": "Database is not configured."}), 503
        try:
            results = db.session.query(Measurement.pollutant).distinct().order_by(Measurement.pollutant).all()
            pollutant_list = [item[0] for item in results]
            return jsonify(pollutant_list)
        except (OperationalError, ProgrammingError) as e:
            return jsonify({"error": "Database connection failed or table not found."}), 503
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route('/api/measurements', methods=['GET'])
    def get_measurements():
        if not app.config.get('SQLALCHEMY_DATABASE_URI'):
             return jsonify({"error": "Database is not configured."}), 503
        
        pollutant_filter = request.args.get('pollutant')
        limit = request.args.get('limit', default=100, type=int)

        if not pollutant_filter:
            return jsonify({"error": "Pollutant parameter is required."}), 400

        try:
            query = db.session.query(Measurement).filter(Measurement.pollutant == pollutant_filter).limit(limit)
            results = query.all()
            output = []
            for res in results:
                point_geojson = json.loads(db.session.scalar(res.geometry.ST_AsGeoJSON()))
                output.append({
                    'timestamp': res.timestamp.isoformat(),
                    'station_name': res.nomestazione,
                    'pollutant': res.pollutant,
                    'value': res.measurement_value,
                    'sensor_id': res.idsensore,
                    'location': point_geojson
                })
            return jsonify(output)
        except (OperationalError, ProgrammingError) as e:
             return jsonify({"error": "Database connection failed or table not found."}), 503
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    # 后台任务路由
    @app.route('/set-config', methods=['POST'])
    def set_config():
        config_data = request.json
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump(config_data, f, indent=4)
            # 在这里重新加载应用配置，或者提示用户重启服务器
            return jsonify({"status": "success", "message": "Configuration saved! Please restart the server for changes to take effect."})
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500

    @app.route('/test-connection', methods=['POST'])
    def test_connection():
        config = request.json
        try:
            conn_str = f"postgresql://{config['user']}:{config['password']}@{config['host']}:{config.get('port', 5432)}/{config['dbName']}"
            engine = create_engine(conn_str)
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            return jsonify({"status": "success", "message": "Database connection successful!"})
        except Exception as e:
            return jsonify({"status": "error", "message": "Connection failed. Please check credentials."}), 400

    @app.route('/run-pipeline', methods=['POST'])
    def run_pipeline():
        print("\n--- [PIPELINE] Starting data pipeline... ---")
        try:
            print("--- [PIPELINE] Step 1: Running Data Integration ---")
            if not run_integration():
                raise Exception("Data integration step failed.")
            print("--- [PIPELINE] Step 1: Completed. ---")

            if not os.path.exists(CONFIG_FILE):
                raise Exception("Config file not found.")
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)

            print("--- [PIPELINE] Step 2: Running Database Load ---")
            if not run_db_load(config):
                raise Exception("Database loading step failed.")
            print("--- [PIPELINE] Step 2: Completed. ---")
            
            return jsonify({"status": "success", "message": "Pipeline completed! Please restart the server to use the dashboard."})
        except Exception as e:
            error_message = f"Pipeline failed: {e}"
            print(f"--- [PIPELINE] ERROR: {error_message} ---")
            return jsonify({"status": "error", "message": error_message}), 500

    return app

# --- 6. 创建并运行应用 ---
app = create_app()

if __name__ == '__main__':
    # 注意：debug=True 会导致应用重启，这对于动态配置是理想的
    app.run(debug=True, port=5000)
