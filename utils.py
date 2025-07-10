def remove_water_columns(df):
    drop_keywords = ["water", "Water"]
    cols_to_drop = [col for col in df.columns if any(key in col for key in drop_keywords)]
    return df.drop(columns=cols_to_drop, errors='ignore')
