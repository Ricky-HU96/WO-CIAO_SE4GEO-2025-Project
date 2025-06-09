import geopandas as gpd
from sqlalchemy import create_engine
import os

# 将核心逻辑包裹在一个函数中，它接收数据库配置作为参数
def run_db_load(db_config):
    try:
        print("--- [TASK 2] Database Load Started ---")
        
        # 从传入的配置字典中获取信息
        DB_USER = db_config['user']
        DB_PASSWORD = db_config['password']
        DB_HOST = db_config['host']
        DB_PORT = db_config.get('port', '5432') # 使用默认端口 5432
        DB_NAME = db_config['dbName']

        # 创建数据库连接字符串
        db_connection_str = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        engine = create_engine(db_connection_str)

        # 加载数据 (假设集成脚本已经生成了 gpkg 文件)
        gpkg_path = os.path.join("output_data", "lombardia_air_quality.gpkg")
        if not os.path.exists(gpkg_path):
            print(f"Error: GeoPackage file not found at {gpkg_path}")
            return False
            
        print(f"Loading data from {gpkg_path}...")
        gdf = gpd.read_file(gpkg_path)

        # 写入 PostGIS
        table_name = 'air_quality_measurements'
        print(f"Writing data to table '{table_name}'...")
        gdf.to_postgis(name=table_name, con=engine, if_exists='replace', index=False)
        
        print("--- [TASK 2] Database Load Complete ---")
        return True

    except Exception as e:
        print(f"Error during database load: {e}")
        return False