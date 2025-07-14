# Energy Forecasting System - User Guide

## Introduction

This user guide provides step-by-step instructions for using the Energy Forecasting System. The system predicts energy consumption for different devices (TGBT, AC, and compressor) and provides maintenance alerts based on anomaly detection.

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Required Python packages (install using `pip install -r requirements.txt`)

### Installation

1. Ensure all dependencies are installed:

```bash
pip install -r requirements.txt
```

2. Verify the data directory structure:

```
data/
├── ac/         # Air conditioning data files
├── compressor/ # Compressor data files
└── tgbt/       # TGBT data files
```

## Using the Command Line Interface

### Running Predictions

For a quick 7-day forecast for all devices:

1. Open a terminal/command prompt
2. Navigate to the project directory
3. Run the prediction script:

```bash
python predict.py
```

4. View the results in the console output

### Training Models

If you have new data and need to retrain the models:

1. Ensure your new data files are in the correct format and placed in the appropriate data subdirectories
2. Run the training script:

```bash
python train_model.py
```

3. The script will train new models and save them to the `models/` directory

## Using the API

### Starting the API Server

1. Open a terminal/command prompt
2. Navigate to the project directory
3. Start the API server:

```bash
python main.py
```

4. The server will start on http://localhost:8000/docs

### Making API Requests

#### Using the API Examples Script

I did provide an example script to demonstrate API usage:

```bash
python api_examples.py
```

This will:
- Get a 7-day forecast for TGBT
- Get a 14-day forecast for AC
- Compare forecasts for all devices
- Generate visualization plots

#### Using cURL

You can also use cURL to make API requests:

```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"device":"tgbt","horizon_days":7}'
```

#### Using Python Requests

```python
import requests

response = requests.post(
    "http://localhost:8000/predict",
    json={"device": "tgbt", "horizon_days": 7}
)

print(response.json())
```

## Interpreting Results

### Forecast Data

The forecast data includes:

- **device**: The device name ("tgbt", "ac", or "compressor")
- **horizon_days**: The number of days in the forecast
- **forecast_kwh**: A dictionary mapping dates to predicted energy consumption in kWh
- **alerts**: A list of maintenance alerts (if any)

Example:

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

### Maintenance Alerts

The system detects two types of anomalies:

1. **High Anomaly**: Abnormally high energy consumption that may indicate inefficiency or malfunction
2. **Low Anomaly**: Abnormally low energy consumption that may indicate device failure or downtime

When an anomaly is detected, the system will provide a specific alert message with the date of the anomaly.

## Troubleshooting

### Common Issues

1. **API Connection Errors**
   - Ensure the API server is running
   - Check that you're using the correct URL and port
   - Verify network connectivity

2. **Missing Data Errors**
   - Ensure all required data files are present in the data directories
   - Check that data files are in the correct JSON format

3. **Model Errors**
   - If you get model-related errors, try retraining the models
   - Ensure the models directory contains all required model files

### Getting Help

If you encounter issues not covered in this guide, please contact the development team for assistance.

## Advanced Usage

### Customizing Prediction Parameters

You can modify the following parameters in the `predict.py` file:

- `MIN_KWH`: Minimum predicted kWh value (default: 10.0)
- `NOISE_STD_PCT`: Standard deviation for noise addition (default: 0.01)
- Anomaly detection threshold in the `detect_anomaly` function (default: 2.0)

### Adding New Devices

To add a new device to the system:

1. Create a new data directory for the device under the `data/` directory
2. Add data files in the correct JSON format
3. Update the `DEVICE_LIST` in `main.py` to include the new device
4. Run the training script to create models for the new device

## Conclusion

This Energy Forecasting System provides valuable insights into future energy consumption patterns and helps identify potential maintenance issues before they become critical. By following this guide, you should be able to effectively use all features of the system.