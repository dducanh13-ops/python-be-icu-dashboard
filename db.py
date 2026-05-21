import sqlite3
import os
from datetime import datetime

# Lấy đường dẫn file hiện hành để tạo file database
current_dir = os.path.dirname(__file__)
DB_PATH = os.path.join(current_dir, "patients.db")

def get_db_connection():
    # Tạo kết nối đến SQLite
    conn = sqlite3.connect(DB_PATH)
    # Lấy dữ liệu dưới dạng từ điển (có thể dùng tên cột)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Tạo bảng nếu chưa có
    sql = """
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            gender TEXT NOT NULL,
            icu INTEGER NOT NULL,
            heart_rate INTEGER NOT NULL,
            oxygen_saturation INTEGER NOT NULL,
            admission_date TEXT NOT NULL
        )
    """
    cursor.execute(sql)
    conn.commit()
    conn.close()

def get_all_patients():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM patients ORDER BY id DESC")
    rows = cursor.fetchall()
    
    # Chuyển đổi thành danh sách dict
    patients = []
    for row in rows:
        patient_dict = dict(row)
        patients.append(patient_dict)
        
    conn.close()
    return patients

def add_patient(name, age, gender, icu, heart_rate, oxygen_saturation, admission_date):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    sql = """
        INSERT INTO patients (name, age, gender, icu, heart_rate, oxygen_saturation, admission_date)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """
    cursor.execute(sql, (name, age, gender, icu, heart_rate, oxygen_saturation, admission_date))
    conn.commit()
    
    new_id = cursor.lastrowid
    conn.close()
    return new_id

def delete_patient(patient_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM patients WHERE id = ?", (patient_id,))
    conn.commit()
    
    rows_affected = cursor.rowcount
    conn.close()
    
    if rows_affected > 0:
        return True
    else:
        return False

def delete_all_patients():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM patients")
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='patients'")
    conn.commit()
    conn.close()
    return True

def get_age_group(age):
    if age < 20:
        return "0-19"
    elif age < 40:
        return "20-39"
    elif age < 60:
        return "40-59"
    elif age < 80:
        return "60-79"
    else:
        return "80+"

def get_dashboard_stats():
    patients = get_all_patients()
    total_patients = len(patients)
    
    if total_patients == 0:
        return {
            "total_patients": 0,
            "icu_count": 0,
            "non_icu_count": 0,
            "icu_rate": 0,
            "avg_heart_rate": 0,
            "avg_oxygen": 0,
            "pie_data": {"icu": 0, "non_icu": 0, "icu_rate": 0},
            "bar_data": [],
            "line_data": []
        }
    
    icu_count = 0
    sum_heart_rate = 0
    sum_oxygen = 0
    
    # Tính tổng số ca ICU và tổng các chỉ số
    for p in patients:
        if p['icu'] == 1:
            icu_count = icu_count + 1
        sum_heart_rate = sum_heart_rate + p['heart_rate']
        sum_oxygen = sum_oxygen + p['oxygen_saturation']
        
    non_icu_count = total_patients - icu_count
    icu_rate = round((icu_count / total_patients) * 100, 1)
    
    avg_heart_rate = round(sum_heart_rate / total_patients, 1)
    avg_oxygen = round(sum_oxygen / total_patients, 1)
    
    pie_data = {
        "icu": icu_count,
        "non_icu": non_icu_count,
        "icu_rate": icu_rate
    }
    
    # Thống kê theo nhóm tuổi
    age_groups_list = ["0-19", "20-39", "40-59", "60-79", "80+"]
    
    age_stats = {}
    for group in age_groups_list:
        age_stats[group] = {
            "total": 0,
            "icu": 0,
            "heart_rate_sum": 0,
            "oxygen_sum": 0
        }
        
    # Phân nhóm bệnh nhân
    for p in patients:
        group = get_age_group(p['age'])
        age_stats[group]["total"] = age_stats[group]["total"] + 1
        age_stats[group]["heart_rate_sum"] = age_stats[group]["heart_rate_sum"] + p['heart_rate']
        age_stats[group]["oxygen_sum"] = age_stats[group]["oxygen_sum"] + p['oxygen_saturation']
        if p['icu'] == 1:
            age_stats[group]["icu"] = age_stats[group]["icu"] + 1
            
    bar_data = []
    line_data = []
    
    for group in age_groups_list:
        stats = age_stats[group]
        total = stats["total"]
        
        if total > 0:
            group_icu_rate = round((stats["icu"] / total) * 100, 1)
            avg_hr = round(stats["heart_rate_sum"] / total, 1)
            avg_o2 = round(stats["oxygen_sum"] / total, 1)
        else:
            group_icu_rate = 0
            avg_hr = 0
            avg_o2 = 0
            
        bar_data.append({
            "age_group": group,
            "total_patients": total,
            "icu_patients": stats["icu"],
            "icu_rate": group_icu_rate
        })
        
        line_data.append({
            "age_group": group,
            "avg_heart_rate": avg_hr,
            "avg_oxygen_saturation": avg_o2
        })
        
    return {
        "total_patients": total_patients,
        "icu_count": icu_count,
        "non_icu_count": non_icu_count,
        "icu_rate": icu_rate,
        "avg_heart_rate": avg_heart_rate,
        "avg_oxygen": avg_oxygen,
        "pie_data": pie_data,
        "bar_data": bar_data,
        "line_data": line_data
    }

def get_time_series_data():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            admission_date,
            COUNT(*) as patient_count,
            ROUND(AVG(heart_rate), 1) as avg_heart_rate,
            ROUND(AVG(oxygen_saturation), 1) as avg_oxygen_saturation
        FROM patients
        GROUP BY admission_date
        ORDER BY admission_date ASC
    """)
    rows = cursor.fetchall()
    conn.close()
    
    result = []
    for r in rows:
        result.append({
            "admission_date": r[0],
            "patient_count": r[1],
            "avg_heart_rate": r[2],
            "avg_oxygen_saturation": r[3]
        })
    return result

def get_risk_matrix_data():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, age, gender, icu, heart_rate, oxygen_saturation, admission_date FROM patients")
    rows = cursor.fetchall()
    conn.close()
    
    classified = []
    for r in rows:
        p_id = r[0]
        name = r[1]
        age = r[2]
        gender = r[3]
        icu = r[4]
        hr = r[5]
        spo2 = r[6]
        date = r[7]
        
        if spo2 >= 95:
            spo2_cat = "high"
        elif spo2 >= 90:
            spo2_cat = "medium"
        else:
            spo2_cat = "low"
            
        if hr < 60:
            hr_cat = "bradycardia"
        elif hr <= 100:
            hr_cat = "normal"
        else:
            hr_cat = "tachycardia"
            
        classified.append({
            "id": p_id,
            "name": name,
            "age": age,
            "gender": gender,
            "icu": icu,
            "heart_rate": hr,
            "oxygen_saturation": spo2,
            "admission_date": date,
            "spo2_cat": spo2_cat,
            "hr_cat": hr_cat
        })
    return classified

def get_advanced_stats():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT age, oxygen_saturation, heart_rate, icu FROM patients")
    rows = cursor.fetchall()
    conn.close()
    
    if len(rows) == 0:
        return {
            "age_spo2_corr": 0,
            "age_hr_corr": 0,
            "elderly_icu_risk": 0,
            "younger_icu_risk": 0,
            "relative_risk": 0,
            "elderly_total": 0,
            "elderly_icu": 0,
            "younger_total": 0,
            "younger_icu": 0
        }
        
    ages = []
    spo2s = []
    hrs = []
    icus = []
    
    for r in rows:
        ages.append(r[0])
        spo2s.append(r[1])
        hrs.append(r[2])
        icus.append(r[3])
    
    n = len(rows)
    
    # Tính hệ số tương quan
    def correlation(x, y):
        sum_x = 0
        sum_y = 0
        for i in range(n):
            sum_x = sum_x + x[i]
            sum_y = sum_y + y[i]
            
        mean_x = sum_x / n
        mean_y = sum_y / n
        
        num = 0
        den_x = 0
        den_y = 0
        
        for i in range(n):
            dx = x[i] - mean_x
            dy = y[i] - mean_y
            num = num + (dx * dy)
            den_x = den_x + (dx * dx)
            den_y = den_y + (dy * dy)
            
        if den_x == 0 or den_y == 0:
            return 0
            
        return round(num / ((den_x * den_y) ** 0.5), 3)
        
    age_spo2_corr = correlation(ages, spo2s)
    age_hr_corr = correlation(ages, hrs)
    
    elderly_total = 0
    elderly_icu = 0
    younger_total = 0
    younger_icu = 0
    
    for i in range(n):
        age = ages[i]
        icu = icus[i]
        if age >= 60:
            elderly_total = elderly_total + 1
            if icu == 1:
                elderly_icu = elderly_icu + 1
        else:
            younger_total = younger_total + 1
            if icu == 1:
                younger_icu = younger_icu + 1
                
    if elderly_total > 0:
        elderly_risk = elderly_icu / elderly_total
    else:
        elderly_risk = 0
        
    if younger_total > 0:
        younger_risk = younger_icu / younger_total
    else:
        younger_risk = 0
        
    if younger_risk > 0:
        relative_risk = round(elderly_risk / younger_risk, 2)
    elif elderly_risk > 0:
        relative_risk = 99.9
    else:
        relative_risk = 1.0
        
    return {
        "age_spo2_corr": age_spo2_corr,
        "age_hr_corr": age_hr_corr,
        "elderly_icu_risk": round(elderly_risk * 100, 1),
        "younger_icu_risk": round(younger_risk * 100, 1),
        "relative_risk": relative_risk,
        "elderly_total": elderly_total,
        "elderly_icu": elderly_icu,
        "younger_total": younger_total,
        "younger_icu": younger_icu
    }

def get_forecast_data():
    time_series = get_time_series_data()
    if len(time_series) == 0:
        return []
        
    n = len(time_series)
    from datetime import datetime, timedelta
    
    if n < 2:
        if n == 1:
            last_val = time_series[0]["patient_count"]
            last_date_str = time_series[0]["admission_date"]
        else:
            last_val = 0
            last_date_str = datetime.now().strftime("%Y-%m-%d")
            
        last_date = datetime.strptime(last_date_str, "%Y-%m-%d")
        
        forecast = []
        for i in range(1, 8):
            next_date = last_date + timedelta(days=i)
            forecast.append({
                "admission_date": next_date.strftime("%Y-%m-%d"),
                "patient_count": last_val,
                "is_forecast": True
            })
        return forecast
        
    # Tính đường hồi quy tuyến tính (y = m * x + c)
    x = []
    y = []
    for i in range(n):
        x.append(i)
        y.append(time_series[i]["patient_count"])
    
    sum_x = 0
    sum_y = 0
    for i in range(n):
        sum_x = sum_x + x[i]
        sum_y = sum_y + y[i]
        
    mean_x = sum_x / n
    mean_y = sum_y / n
    
    num = 0
    den = 0
    for i in range(n):
        dx = x[i] - mean_x
        dy = y[i] - mean_y
        num = num + (dx * dy)
        den = den + (dx * dx)
        
    if den != 0:
        m = num / den
    else:
        m = 0
        
    c = mean_y - m * mean_x
    
    last_date_str = time_series[-1]["admission_date"]
    last_date = datetime.strptime(last_date_str, "%Y-%m-%d")
    
    forecast = []
    for i in range(1, 8):
        next_date = last_date + timedelta(days=i)
        projected_x = (n - 1) + i
        projected_y = m * projected_x + c
        if projected_y < 0:
            projected_y = 0
            
        forecast.append({
            "admission_date": next_date.strftime("%Y-%m-%d"),
            "patient_count": round(projected_y, 1),
            "is_forecast": True
        })
    return forecast
