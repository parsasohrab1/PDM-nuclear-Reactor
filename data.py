import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# تنظیمات
seconds_in_month = 30 * 24 * 3600  # 30 روز
start_time = datetime(2025, 1, 1, 0, 0, 0)
timestamps = [start_time + timedelta(seconds=i) for i in range(seconds_in_month)]

# توابع شبیه‌سازی سیگنال‌های نرمال رآکتور
def normal_temperature(t):
    # دما با نوسان روزانه + روند آرام
    daily = 5 * np.sin(2 * np.pi * t / 86400)
    trend = 1e-6 * t
    noise = np.random.normal(0, 0.2, len(t)) if isinstance(t, np.ndarray) else 0
    return 300 + daily + trend + noise

def normal_pressure(t):
    return 150 + 2 * np.sin(2 * np.pi * t / 43200) + np.random.normal(0, 0.1)

def normal_neutron_flux(t):
    # نوتورن‌ها با نویز پواسون
    base = 1000 + 0.5 * np.sin(2 * np.pi * t / 3600)
    return np.random.poisson(base)

def normal_vibration(t):
    return 0.5 * np.sin(2 * np.pi * t / 300) + np.random.normal(0, 0.05)

# تولید داده‌های اولیه نرمال
t_seconds = np.arange(seconds_in_month)
data = {
    'timestamp': timestamps,
    'temp_c': normal_temperature(t_seconds),
    'pressure_bar': normal_pressure(t_seconds),
    'neutron_flux': [normal_neutron_flux(ts) for ts in t_seconds],
    'vibration_ms2': normal_vibration(t_seconds)
}
df = pd.DataFrame(data)

# تزریق آنومالی‌های مصنوعی (شامل ۴ نوع عیب)
np.random.seed(42)
anomaly_indices = []

# نوع ۱: افزایش ناگهانی دما (نشانه خرابی خنک‌کننده)
anom1 = np.random.choice(seconds_in_month, size=200, replace=False)
df.loc[anom1, 'temp_c'] += np.random.uniform(15, 30, size=200)
anomaly_indices.extend(anom1)

# نوع ۲: نوسان فشار غیرعادی (نشت)
anom2 = np.random.choice(seconds_in_month, size=150, replace=False)
df.loc[anom2, 'pressure_bar'] += np.random.normal(10, 2, size=150)
anomaly_indices.extend(anom2)

# نوع ۳: افت ناگهانی نوترون (کنترل میله‌ها)
anom3 = np.random.choice(seconds_in_month, size=100, replace=False)
df.loc[anom3, 'neutron_flux'] = df.loc[anom3, 'neutron_flux'] * 0.3
anomaly_indices.extend(anom3)

# نوع ۴: لرزش فرکانس بالا (نشانه عدم تعادل مکانیکی)
anom4 = np.random.choice(seconds_in_month, size=250, replace=False)
df.loc[anom4, 'vibration_ms2'] += np.random.uniform(0.8, 1.5, size=250)
anomaly_indices.extend(anom4)

# ساخت برچسب آنومالی (۱ برای ناهنجاری، ۰ برای نرمال)
df['label'] = 0
df.loc[anomaly_indices, 'label'] = 1

# ذخیره به صورت فایل CSV (فقط یک نمونه کوچک برای نمایش)
df_sample = df.iloc[::3600, :]  # نمونه‌برداری ساعتی برای نمایش
df_sample.to_csv('nuclear_reactor_synthetic_data.csv', index=False)

# نمایش خلاصه
print(f"تعداد کل رکوردها: {len(df)}")
print(f"درصد آنومالی: {df['label'].mean()*100:.2f}%")
print(df.head())