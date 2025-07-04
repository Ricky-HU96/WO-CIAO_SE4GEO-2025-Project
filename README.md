# WO-CIAO_SE4GEO-2025-Project - Lombardy Air Quality Dashboard
**Author:** TIANQI HU (ID: 10948367)  SHINUO YAN(ID: 11063707)  JIAYI SU(ID: 10962393)

This is a full-stack web application project designed to provide a complete solution for fetching, processing, storing, and visualizing air quality monitoring data from the Lombardy region in Italy.
The project includes a backend data processing pipeline, a PostGIS database for data storage, a Flask web server that provides a RESTful API, and an interactive web dashboard and Jupyter Notebook for data exploration and visualization.

---

# ✨ Key Features
- **One-Click Data Pipeline:**
  Triggered via a web interface, it automates the entire process of downloading, processing, and loading data into the database.
- **Geospatial Data Processing:**
  Uses GeoPandas to handle sensor location data and saves the results to a GeoPackage file.
- **Robust Database Support:**
  Leverages PostgreSQL with the PostGIS extension for efficient storage and querying of geospatial data.
- **Dynamic Configuration:**
  Loads database settings from config.json on startup and provides a web interface for dynamic updates.
- **RESTful API:**
  Offers API endpoints that allow third-party applications or data analysis scripts (like Jupyter Notebooks) to easily access the processed data.
- **nteractive Dashboard:**
  A front-end built with Flask, Leaflet.js, and Chart.js to display pollutant types and their geospatial distribution.
- **Data-Analysis Friendly:**
  Includes dashboard.ipynb to demonstrate how to call the API for data retrieval and perform in-depth analysis and visualization with Folium and Plotly.

---

# 🏛️ System Architecture
The core workflow of the project is as follows:

    subgraph "1. Data Pipeline (Triggered via Web UI)"
        A[Fetch Sensor Metadata CSV] --> C{Data Integration & Processing<br/>(combined_air_quality_measurements.py)};
        B[Fetch Air Quality Measurements CSV] --> C;
        C --> D[Generate<br/>lombardia_air_quality.gpkg];
        D --> E{Load into Database<br/>(load_to_db.py)};
        E --> F[(PostGIS Database)];
    end

    subgraph "2. Data Serving & Presentation"
        F --> G[Flask Application<br/>(app.py)];
        G --> H{RESTful API<br/>(/api/...)};
        H --> I[Web Dashboard<br/>(/dashboard)];
        H --> J[Jupyter Notebook<br/>(dashboard.ipynb)];
        I --> K((User));
        J --> K;
    end

    subgraph "3. Application Configuration"
        K --> L[Web Configuration Page<br/>(/)];
        L --> M[Save Configuration<br/>(config.json)];
        M --> G;
    end

---

# 📂 Project Structure

```
├── app.py                      # Flask main application, contains API and web page routes
├── combined_air_quality_measurements.py # Data integration script (ETL Step 1)
├── load_to_db.py               # Data loading script (ETL Step 2)
├── dashboard.ipynb             # Jupyter Notebook for data analysis and visualization
├── config.json                 # Database connection configuration file
├── templates/
│   ├── index.html              # Homepage for configuration and running the pipeline
│   └── dashboard.html          # Data dashboard page
├── static/
│   └── ...                     # Static files like CSS, JavaScript, images
├── output_data/
│   └── lombardia_air_quality.gpkg # Geospatial data file generated after the pipeline runs
└── readme.md                   # This document
```

---

# 🛠️ Prerequisites
1. Before running this project, ensure you have the following software installed:
2. Python 3.8+ and pip
3. PostgreSQL 12+
4. PostGIS 3+ extension (must be enabled for your PostgreSQL database)
5. pgAdmin 4 (Recommended for database management)

---

# ⚙️ Installation & Setup
1. Clone the Repository
git clone <your-repository-url>
cd <repository-directory>

2. Create and Activate a Python Virtual Environment
- Linux / macOS:

```
python3 -m venv venv
source venv/bin/activate
```

- Windows:

```
python -m venv venv
.\venv\Scripts\activate
```

3. Install Dependencies
Project dependencies are listed in requirements.txt. Run the following command to install them:

```
pip install flask flask_sqlalchemy sqlalchemy geoalchemy2 psycopg2-binary pandas geopandas shapely requests plotly folium
```

(Alternatively, if a requirements.txt file is provided, simply run pip install -r requirements.txt)

4. Database Setup
- Open pgAdmin 4.
- In the left-hand server tree, right-click on "Databases" -> Create -> Database....
- Set the database name to se4geo_project and save.
- Connect to the newly created se4geo_project database and open a Query Tool.
- Execute the following SQL command to enable the PostGIS extension:

```
CREATE EXTENSION postgis;
```

You should see a "CREATE EXTENSION" success message if it works.

---

# 🚀 Running the Application (First Time)
**Step 1: Start the Flask Server**
In the project's root directory, run app.py:

```
python app.py
```

The server will start on http://127.0.0.1:5000.

**Step 2: Configure the Database Connection**
1. Open a web browser and navigate to http://127.0.0.1:5000.
2. You will see a configuration form. Fill in your PostgreSQL User, Password, Host, Port, and Database Name (se4geo_project).
3. Click the "Test Connection" button. You should see a "Database connection successful!" message if your credentials are correct.
4. Click the "Save Configuration" button. This will write your settings to the config.json file.

**Step 3: Run the Data Pipeline**
1. On the same page, click the "Run Data Pipeline" button.
2. This will start the backend data processing flow. You can monitor the detailed progress in the terminal where you ran app.py (look for logs starting with "[PIPELINE]").
3. This process may take several minutes as it downloads data, processes it, and loads it into the database.
4. You will see a "Pipeline completed!" success message on the web page when the data has been successfully loaded.

**Step 4: Restart the Server**
**This is a crucial step!** To ensure the Flask application loads the database connection with the newly populated data, you must restart the server.
1. Go back to the terminal running app.py.
2. Press Ctrl + C to stop the server.
3. Run python app.py again to restart it.

---

# 📊 Usage
**Web Dashboard**
- Navigate to http://127.0.0.1:5000/dashboard in your browser.
- The dashboard will feature:
  - A dropdown menu listing all available pollutant types from the database.
  - An interactive map showing the locations of monitoring stations for the selected pollutant.
  - A time-series chart displaying pollutant concentration changes across different stations.

**API Endpoints**
The application provides the following API endpoints for data querying:

- **Get All Pollutant Types**
  - **Endpoint:** /api/pollutants
  - **Method:** GET
  - **Description:** Returns a list of all unique pollutant names in the database.
  - **Example Response:**
```
[
  "Ammoniaca",
  "Arsenico",
  "Benzene",
  "Benzo(a)pirene",
  "Biossido di Azoto",
  ...
]
```

- **Get Measurement Data**
  - Endpoint: /api/measurements
  - Method: GET
  - Parameters:
    - pollutant (required): The name of the pollutant to query (e.g., Ozono).
    - limit (optional, default 100): The maximum number of records to return.
  - Description: Returns geospatial measurement data based on the pollutant type.
  - Example Request: http://127.0.0.1:5000/api/measurements?pollutant=Ozono&limit=2
  - Example Response:
```
[
  {
    "location": {
      "type": "Point",
      "coordinates": [9.16464919, 45.19468231]
    },
    "pollutant": "Ozono",
    "sensor_id": 6625,
    "station_name": "Pavia v. Folperti",
    "timestamp": "2024-05-22T17:00:00+00:00",
    "value": 46.1
  },
  {
    "location": {
      "type": "Point",
      "coordinates": [9.49528589, 45.30278678]
    },
    "pollutant": "Ozono",
    "sensor_id": 10454,
    "station_name": "Lodi S.Alberto",
    "timestamp": "2024-05-22T17:00:00+00:00",
    "value": 47.9
  }
]
```

**Data Analysis with Jupyter Notebook**
1. Make sure the Flask server is running.
2. Start Jupyter Notebook from the project's root directory:
   
```
jupyter notebook
```

3. Open the dashboard.ipynb file.
4. Execute the cells sequentially to see how to use the requests library to call the API and folium and plotly to create advanced maps and charts.

---

# 💡 Future Improvements
- User Authentication: Add a login system to protect the configuration and pipeline execution pages.
- Advanced API Filtering: Add functionality to query data by date range or a geospatial bounding box (BBOX).
- Caching: Implement a caching mechanism for API responses to improve performance.
- Containerization: Use Docker and Docker Compose to simplify deployment.
- Unit/Integration Testing: Write test cases for the data pipeline and API endpoints.
- UI/UX Enhancements: Improve the dashboard's user experience and add more chart types.
