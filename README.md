# Energy Forecasting System

## Overview

This project is an energy consumption forecasting system that predicts future energy usage for different devices and provides predictive maintenance alerts based on anomaly detection. The system uses machine learning models (LightGBM) to forecast energy consumption for the next 1-30 days.

## Features

- **Energy Consumption Forecasting**: Predicts daily energy consumption for multiple devices
- **Anomaly Detection**: Identifies abnormal energy consumption patterns
- **Predictive Maintenance Alerts**: Provides maintenance recommendations based on detected anomalies
- **REST API**: Exposes forecasting capabilities through a FastAPI interface

## Project Structure

```
├── data/                  # Contains JSON data files for each device
│   ├── ac/                # Air conditioning data
│   ├── compressor/        # Compressor data
│   └── tgbt/              # TGBT (Tableau Général Basse Tension) data
├── models/                # Trained machine learning models
│   ├── *_lgbm_model.pkl   # LightGBM model files
│   └── *_feature_columns.pkl # Feature columns for each model
├── main.py                # FastAPI application entry point
├── predict.py             # Prediction logic
├── train_model.py         # Model training pipeline
└── requirements.txt       # Project dependencies
```

## Installation

1. Clone the repository

2. Install dependencies:

```bash
pip install -r requirements.txt
```


## Usage

### Training Models

To train or retrain the models with new data:

```bash
python train_model.py
```

This will:
- Load data from the JSON files in the data directories
- Process and resample the data to hourly intervals
- Create features for the machine learning models
- Train LightGBM models for each device
- Save the models and feature columns to the models directory

### Making Predictions via Command Line

To generate predictions directly from the command line:

```bash
python predict.py
```

This will output a 7-day forecast for each device along with any maintenance alerts.

### Running the API Server

To start the API server:

```bash
python main.py
```

The server will start on http://localhost:8000/docs

### API Usage

The API exposes a single endpoint for predictions:

**POST /predict**

Request body:
```json
{
  "device": "tgbt",  // Options: "tgbt", "ac", "compressor"
  "horizon_days": 7  // Number of days to forecast (1-30)
}
```

Example response:
```json
{
  "device": "tgbt",
  "horizon_days": 7,
  "forecast_kwh": {
    "2025-07-01": 259.13,
    "2025-07-02": 254.53,
    "2025-07-03": 258.78,
    "2025-07-04": 244.65,
    "2025-07-05": 241.87,
    "2025-07-06": 245.67,
    "2025-07-07": 257.2
  },
  "alerts": [
    "✅ No anomalies detected."
  ]
}
```

If anomalies are detected, the alerts field will contain specific warnings.

## Data Format

The system expects JSON data files with the following structure:

```json
{
  "data": {
    "metric_name1": [
      {"ts": 1718409600000, "value": 23.5},
      {"ts": 1718413200000, "value": 24.1}
    ],
    "metric_name2": [
      {"ts": 1718409600000, "value": 421.3},
      {"ts": 1718413200000, "value": 422.1}
    ]
  }
}
```

Where:
- `ts` is a timestamp in milliseconds
- `value` is the metric value

## Key Metrics

The system tracks several key metrics for each device:

- **ActivePowerTotal**: Total active power consumption
- **Current_Avg**: Average current
- **Frequency**: Electrical frequency
- **VoltageL_L_Avg**: Average line-to-line voltage
- **VoltageL_N_Avg**: Average line-to-neutral voltage
- **deltaFiveMinutesEnergyConsumtion**: Energy consumption over 5-minute intervals
- **deltaHalfHourEnergyConsumtion**: Energy consumption over 30-minute intervals
- **deltaHourEnergyConsumtion**: Energy consumption over 1-hour intervals
- **deltaDayEnergyConsumtion**: Energy consumption over 24-hour intervals
- **AccumulatedActiveEnergyDelivered**: Total accumulated energy delivered

## Maintenance and Troubleshooting

### Common Issues

1. **Missing Data**: If data files are missing or corrupted, the system will log warnings during the training process.

2. **Model Performance**: If prediction accuracy decreases, consider retraining the models with more recent data.

3. **API Errors**: Check that the device name is one of the supported options: "tgbt", "ac", or "compressor".

