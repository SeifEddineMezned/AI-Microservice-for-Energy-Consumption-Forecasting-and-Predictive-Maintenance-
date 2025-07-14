import pandas as pd
import joblib
import numpy as np
from pathlib import Path
from train_model import parse_nested_json, resample_hourly, create_features

MIN_KWH = 10.0
NOISE_STD_PCT = 0.01

def load_latest_data(device_folder):
    all_files = sorted(Path(device_folder).glob("*.json"))
    dfs = [parse_nested_json(f) for f in all_files]
    df = pd.concat(dfs).sort_index()
    return df

def detect_anomaly(predicted, mean, std, threshold=2.0):
    if std == 0 or np.isnan(std):
        return "Normal", ""
    z = (predicted - mean) / std
    if z > threshold:
        return "High Anomaly", "⚠️ Potential abnormal over-consumption detected — please investigate this device."
    elif z < -threshold:
        return "Low Anomaly", "⚠️ Potential abnormal under-consumption detected — please investigate this device."
    else:
        return "Normal", ""

def predict_next_days(device_name, days=7):
    print(f"\n📊 Predicting for device: {device_name}")

    data_folder = f"data/{device_name}"
    model_path = f"models/{device_name}_lgbm_model.pkl"
    feat_path = f"models/{device_name}_feature_columns.pkl"

    model = joblib.load(model_path)
    feature_cols = joblib.load(feat_path)

    df = load_latest_data(data_folder)
    df_hourly = resample_hourly(df)
    df_feat = create_features(df_hourly)

    full_df = df_feat.copy()
    forecast = []
    maintenance_flags = []

    for i in range(days):
        last_known = full_df.iloc[-1:].copy()
        next_time = last_known.index[0] + pd.Timedelta(days=1)
        next_input = last_known.copy()
        next_input.index = [next_time]

        for lag in [24, 48, 72]:
            col = f"deltaDayEnergyConsumtion_lag_{lag}h"
            if col in full_df.columns:
                try:
                    next_input[col] = full_df["deltaDayEnergyConsumtion"].iloc[-lag]
                except IndexError:
                    next_input[col] = full_df["deltaDayEnergyConsumtion"].mean()

        last_72 = full_df["deltaDayEnergyConsumtion"].iloc[-72:]
        rolling_mean = last_72.mean()
        rolling_std = last_72.std()

        next_input["deltaDayEnergyConsumtion_rolling_mean_72h"] = rolling_mean
        next_input["deltaDayEnergyConsumtion_rolling_std_72h"] = rolling_std

        next_input["hour"] = next_time.hour
        next_input["dayofweek"] = next_time.dayofweek

        for col in ["Frequency", "VoltageL_L_Avg", "VoltageL_N_Avg", "ActivePowerTotal"]:
            lag_col = f"{col}_lag_1h"
            if col in df_hourly.columns:
                next_input[lag_col] = df_hourly[col].iloc[-1]
            else:
                next_input[lag_col] = df_hourly[col].mean()

        X = next_input[feature_cols].copy()
        y_pred = model.predict(X)[0]

        y_pred = max(y_pred, MIN_KWH)
        noise = np.random.normal(0, NOISE_STD_PCT * y_pred)
        y_pred = round(y_pred + noise, 2)

        status, message = detect_anomaly(y_pred, rolling_mean, rolling_std)
        forecast.append((next_time.date(), y_pred, status))
        if message:
            maintenance_flags.append(f"{next_time.date()}: {message}")

        full_df.loc[next_time, "deltaDayEnergyConsumtion"] = y_pred
        for col in X.columns:
            full_df.loc[next_time, col] = next_input[col].values[0]

    return forecast, maintenance_flags

def main():
    for device in ["tgbt", "ac", "compressor"]:
        forecast, alerts = predict_next_days(device, days=7)
        print(f"\n📅 7-Day Forecast for {device}:")
        for date, value, status in forecast:
            if status == "Normal":
                print(f"{date}: {value:.2f} kWh")
            else:
                print(f"{date}: {value:.2f} kWh → {status}")

        if alerts:
            print(f"\n🚨 Predictive Maintenance Alert for {device}:")
            for msg in alerts:
                print(msg)
        else:
            print(f"\n✅ No predictive maintenance issues detected for {device}.")

if __name__ == "__main__":
    main()
