import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import os
from urllib.parse import urlencode

def run_integration():
    """
    Executes the full data integration pipeline.
    
    Returns:
        bool: True if the process completes successfully, False otherwise.
    """
    try:
        print("--- [TASK 1] Data Integration Started ---")

        # --- Step 1: Define Data Sources ---
        stations_url = "https://www.dati.lombardia.it/resource/ib47-atvt.csv"
        measurements_url = "https://www.dati.lombardia.it/resource/g2hp-ar79.csv"

        # --- Step 2: Retrieve and Process Sensor Metadata ---
        print("[1/5] Retrieving and processing sensor metadata...")
        stations_df = pd.read_csv(stations_url)
        required_columns = ['idsensore', 'nomestazione', 'nometiposensore', 'lat', 'lng']
        stations_df = stations_df[required_columns]
        stations_df.dropna(subset=['idsensore', 'lat', 'lng'], inplace=True)
        stations_df['idsensore'] = stations_df['idsensore'].astype(int)
        
        geometry = [Point(xy) for xy in zip(stations_df['lng'], stations_df['lat'])]
        stations_gdf = gpd.GeoDataFrame(stations_df, geometry=geometry, crs="EPSG:4326")
        stations_gdf = stations_gdf.drop(columns=['lat', 'lng'])
        print(f"Successfully processed {len(stations_gdf)} unique sensors.")

        # --- Step 3: Retrieve and Process Air Quality Measurements ---
        print("[2/5] Retrieving and processing air quality measurements...")
        # For a robust setup, let's fetch a significant but manageable number of recent records.
        params = {'$limit': 500000, '$order': 'data DESC'}
        query_string = urlencode(params)
        measurements_url_limited = f"{measurements_url}?{query_string}"
        
        measurements_df = pd.read_csv(measurements_url_limited)
        measurements_df = measurements_df[['idsensore', 'data', 'valore', 'stato']]
        measurements_df.rename(columns={'data': 'timestamp', 'valore': 'measurement_value'}, inplace=True)
        measurements_df['timestamp'] = pd.to_datetime(measurements_df['timestamp'])
        measurements_df['measurement_value'] = pd.to_numeric(measurements_df['measurement_value'], errors='coerce')
        measurements_df = measurements_df[measurements_df['stato'] == 'VA'].dropna(subset=['measurement_value'])
        measurements_df = measurements_df.drop(columns=['stato'])
        print(f"Successfully processed {len(measurements_df)} valid measurements.")

        # --- Step 4: Combine Datasets and Ensure GeoDataFrame Type ---
        print("[3/5] Combining measurements with sensor metadata...")
        merged_df = pd.merge(
            measurements_df,
            stations_gdf,
            on='idsensore',
            how='inner'
        )
        
        # Critical step: Convert the merged DataFrame back to a GeoDataFrame
        print("[4/5] Ensuring the combined data is a GeoDataFrame...")
        combined_gdf = gpd.GeoDataFrame(merged_df, geometry='geometry', crs="EPSG:4326")
        
        final_columns_order = ['timestamp', 'nomestazione', 'nometiposensore', 'measurement_value', 'idsensore', 'geometry']
        combined_gdf = combined_gdf[final_columns_order]
        combined_gdf.rename(columns={'nometiposensore': 'pollutant'}, inplace=True)
        print(f"Final combined dataset created with {len(combined_gdf)} records.")

        # --- Step 5: Save the result to a GeoPackage file ---
        print("[5/5] Saving combined data to GeoPackage file...")
        output_dir = "output_data"
        os.makedirs(output_dir, exist_ok=True)
        
        gpkg_path = os.path.join(output_dir, "lombardia_air_quality.gpkg")
        
        # The GeoPackage format is ideal for preserving all data types, including geometry.
        combined_gdf.to_file(gpkg_path, driver="GPKG", layer="air_quality_measurements")
        
        print(f"✅ Data successfully saved to: {gpkg_path}")
        print("--- [TASK 1] Data Integration Complete ---")
        return True

    except Exception as e:
        print(f"An error occurred during data integration: {e}")
        return False


# This block allows the script to be run directly from the command line for testing
# e.g., `python combined_air_quality_measurements.py`
if __name__ == '__main__':
    print("Running data integration script independently for testing...")
    success = run_integration()
    if success:
        print("\nScript finished successfully.")
    else:
        print("\nScript finished with errors.")