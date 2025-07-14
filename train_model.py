import pandas as pd
import lightgbm as lgb
import joblib
from pathlib import Path
import json


def parse_nested_json(file_path):
    with open(file_path) as f:
        raw_json = json.load(f)

    if "data" not in raw_json:
        raise ValueError(f"'data' section missing in {file_path.name}")

    raw_data = raw_json["data"]
    dfs = []

    for metric_name, records in raw_data.items():
        if not isinstance(records, list) or len(records) == 0:
            print(f"⚠️ Skipping metric '{metric_name}' in file {file_path.name} — not a list or empty")
            continue

        try:
            df = pd.DataFrame(records)
            if 'ts' not in df.columns or 'value' not in df.columns:
                print(f"⚠️ Skipping metric '{metric_name}' in file {file_path.name} — missing 'ts' or 'value'")
                continue

            df['value'] = pd.to_numeric(df['value'], errors='coerce')
            df = df.dropna(subset=['value'])

            df['ts'] = pd.to_datetime(df['ts'], unit='ms')
            df = df.set_index('ts')
            df = df.rename(columns={'value': metric_name})
            dfs.append(df[[metric_name]])
        except Exception as e:
            print(f"❌ Failed to load '{metric_name}' in {file_path.name}: {e}")
            continue

    if not dfs:
        raise ValueError(f"No usable metrics found in {file_path}")

    combined = pd.concat(dfs, axis=1).sort_index()
    return combined


def load_json_folder(folder_path):
    all_files = list(Path(folder_path).glob("*.json"))
    dfs = [parse_nested_json(file_path) for file_path in all_files]
    combined = pd.concat(dfs).sort_index()
    combined = combined[~combined.index.duplicated(keep='first')]
    return combined


def resample_hourly(df):
    sensors = ['ActivePowerTotal', 'Current_Avg', 'Frequency', 'VoltageL_L_Avg', 'VoltageL_N_Avg']
    energy_cols = ['deltaFiveMinutesEnergyConsumtion', 'deltaHalfHourEnergyConsumtion', 'deltaHourEnergyConsumtion', 'deltaDayEnergyConsumtion', 'AccumulatedActiveEnergyDelivered']

    agg_dict = {col: 'mean' for col in sensors}
    agg_dict.update({col: 'sum' for col in energy_cols})

    df_resampled = df.resample('1h').agg(agg_dict)
    return df_resampled


def create_features(df, target_col='deltaDayEnergyConsumtion'):
    df_feat = df.copy()

    for lag in [24, 48, 72]:
        df_feat[f"{target_col}_lag_{lag}h"] = df_feat[target_col].shift(lag)

    df_feat[f"{target_col}_rolling_mean_72h"] = df_feat[target_col].shift(1).rolling(window=72).mean()
    df_feat[f"{target_col}_rolling_std_72h"] = df_feat[target_col].shift(1).rolling(window=72).std()

    df_feat['hour'] = df_feat.index.hour
    df_feat['dayofweek'] = df_feat.index.dayofweek

    sensor_cols = ['Frequency', 'VoltageL_L_Avg', 'VoltageL_N_Avg', 'ActivePowerTotal']
    for col in sensor_cols:
        df_feat[f"{col}_lag_1h"] = df_feat[col].shift(1)

    df_feat = df_feat.dropna()
    return df_feat


def train_model_for_device(device_name, df):
    print(f"\n--- Training model for device: {device_name} ---")
    df_hourly = resample_hourly(df)
    target_col = 'deltaDayEnergyConsumtion'
    df_feat = create_features(df_hourly, target_col=target_col)
    df_feat['target'] = df_feat[target_col].shift(-24)

    df_feat = df_feat.dropna()

    train = df_feat.iloc[:-72]
    test = df_feat.iloc[-72:]

    X_train = train.drop(columns=[target_col, 'target'])
    y_train = train['target']
    X_test = test.drop(columns=[target_col, 'target'])
    y_test = test['target']

    model = lgb.LGBMRegressor(n_estimators=100)
    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    from sklearn.metrics import mean_absolute_error
    mae = mean_absolute_error(y_test, preds)
    print(f"{device_name} Test MAE: {mae:.4f}")

    model_dir = Path("models")
    model_dir.mkdir(exist_ok=True)

    model_path = model_dir / f"{device_name}_lgbm_model.pkl"
    features_path = model_dir / f"{device_name}_feature_columns.pkl"

    joblib.dump(model, model_path)
    joblib.dump(X_train.columns.tolist(), features_path)
    print(f"✅ Saved model to {model_path}")
    print(f"✅ Saved feature columns to {features_path}")


def main():
    device_folders = {
        "tgbt": "data/tgbt",
        "ac": "data/ac",
        "compressor": "data/compressor"
    }

    for device_name, folder_path in device_folders.items():
        print(f"\n📦 Loading data for {device_name}...")
        df = load_json_folder(folder_path)
        train_model_for_device(device_name, df)


if __name__ == "__main__":
    main()
