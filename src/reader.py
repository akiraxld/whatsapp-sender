import pandas as pd

def read_contacts(file_path: str) -> list[dict]:
    df = pd.read_csv(file_path)
    # Убеждаемся что нужные колонки есть
    if 'phone' not in df.columns or 'message' not in df.columns:
        raise ValueError("CSV должен содержать колонки: phone, message")
    return df.to_dict(orient='records')