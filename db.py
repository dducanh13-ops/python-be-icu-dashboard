import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "patients.db")

def get_db_connection():
    """Tạo kết nối tới cơ sở dữ liệu SQLite và trả về đối tượng dict cho mỗi dòng"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Giúp truy cập dữ liệu theo tên cột (ví dụ: row['name'])
    return conn

def init_db():
    """Khởi tạo cơ sở dữ liệu và thêm dữ liệu mẫu nếu bảng trống"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Tạo bảng bệnh nhân
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            gender TEXT NOT NULL,
            icu INTEGER NOT NULL, -- 0: Không ICU, 1: Có ICU
            heart_rate INTEGER NOT NULL,
            oxygen_saturation INTEGER NOT NULL,
            admission_date TEXT NOT NULL
        )
    """)
    conn.commit()
    
    # Kiểm tra xem đã có dữ liệu chưa
    cursor.execute("SELECT COUNT(*) FROM patients")
    count = cursor.fetchone()[0]
    
    if count == 0:
        # Nếu chưa có dữ liệu, thêm dữ liệu mẫu (30 bệnh nhân)
        # Thiết kế dữ liệu sao cho người lớn tuổi có tỉ lệ vào ICU cao hơn
        sample_patients = [
            # Nhóm 0-19 tuổi (Thấp)
            ("Nguyễn An", 12, "Nam", 0, 78, 99, "2026-05-10"),
            ("Lê Minh", 8, "Nam", 0, 85, 98, "2026-05-11"),
            ("Trần Vy", 17, "Nữ", 0, 72, 99, "2026-05-12"),
            ("Phạm Hoàng", 15, "Nam", 0, 80, 97, "2026-05-12"),
            
            # Nhóm 20-39 tuổi (Thấp-Trung bình)
            ("Nguyễn Văn Bình", 28, "Nam", 0, 75, 98, "2026-05-13"),
            ("Đỗ Thị Chi", 32, "Nữ", 0, 70, 98, "2026-05-13"),
            ("Hoàng Đức Duy", 24, "Nam", 1, 105, 94, "2026-05-14"),  # ICU do nhịp tim cao, SpO2 thấp
            ("Phan Thanh Hải", 39, "Nam", 0, 82, 97, "2026-05-14"),
            ("Vũ Thu Hà", 35, "Nữ", 0, 76, 99, "2026-05-15"),
            
            # Nhóm 40-59 tuổi (Trung bình)
            ("Lê Văn Hùng", 45, "Nam", 0, 80, 96, "2026-05-15"),
            ("Nguyễn Thị Hương", 52, "Nữ", 0, 78, 97, "2026-05-16"),
            ("Trần Tuấn Kiệt", 58, "Nam", 1, 95, 92, "2026-05-16"),  # ICU
            ("Bùi Minh Long", 48, "Nam", 0, 84, 98, "2026-05-17"),
            ("Phạm Thanh Nga", 50, "Nữ", 1, 90, 93, "2026-05-17"),   # ICU
            ("Ngô Tiến Phát", 55, "Nam", 0, 72, 97, "2026-05-18"),
            
            # Nhóm 60-79 tuổi (Cao)
            ("Trịnh Văn Quyết", 67, "Nam", 1, 110, 89, "2026-05-18"), # ICU
            ("Lâm Thị Mai", 72, "Nữ", 1, 95, 91, "2026-05-18"),      # ICU
            ("Đặng Hữu Phước", 63, "Nam", 0, 78, 96, "2026-05-19"),
            ("Võ Hoài Nam", 78, "Nam", 1, 102, 90, "2026-05-19"),     # ICU
            ("Nguyễn Thị Thảo", 65, "Nữ", 0, 80, 97, "2026-05-19"),
            ("Lý Hoàng Thông", 70, "Nam", 1, 88, 92, "2026-05-20"),    # ICU
            ("Hồ Bảo Trâm", 74, "Nữ", 0, 74, 95, "2026-05-20"),
            
            # Nhóm 80+ tuổi (Rất cao)
            ("Phan Văn Sơn", 82, "Nam", 1, 92, 88, "2026-05-10"),     # ICU
            ("Trần Thị Tuyết", 89, "Nữ", 1, 98, 87, "2026-05-11"),    # ICU
            ("Nguyễn Văn Tuyên", 85, "Nam", 1, 105, 89, "2026-05-12"),  # ICU
            ("Lê Thị Út", 81, "Nữ", 0, 76, 95, "2026-05-13"),
            ("Đỗ Văn Vương", 93, "Nam", 1, 112, 85, "2026-05-14"),    # ICU
            ("Mai Thị Xuân", 87, "Nữ", 1, 85, 90, "2026-05-15"),     # ICU
            ("Quách Văn Yến", 80, "Nam", 0, 72, 96, "2026-05-16"),
            ("Hoàng Thị Yên", 84, "Nữ", 1, 90, 89, "2026-05-17")      # ICU
        ]
        
        cursor.executemany("""
            INSERT INTO patients (name, age, gender, icu, heart_rate, oxygen_saturation, admission_date)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, sample_patients)
        conn.commit()
        print(f"Successfully added {len(sample_patients)} sample patients to database.")
        
    conn.close()

def get_all_patients():
    """Lấy danh sách tất cả bệnh nhân"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM patients ORDER BY id DESC")
    rows = cursor.fetchall()
    
    # Chuyển đổi thành danh sách dict để FastAPI có thể trả về JSON dễ dàng
    patients = [dict(row) for row in rows]
    conn.close()
    return patients

def add_patient(name, age, gender, icu, heart_rate, oxygen_saturation, admission_date):
    """Thêm bệnh nhân mới"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO patients (name, age, gender, icu, heart_rate, oxygen_saturation, admission_date)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (name, age, gender, icu, heart_rate, oxygen_saturation, admission_date))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return new_id

def delete_patient(patient_id):
    """Xóa bệnh nhân theo ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM patients WHERE id = ?", (patient_id,))
    conn.commit()
    rows_affected = cursor.rowcount
    conn.close()
    return rows_affected > 0

def delete_all_patients():
    """Xóa toàn bộ bệnh nhân và reset ID tăng tự động"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM patients")
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='patients'")
    conn.commit()
    conn.close()
    return True

def get_age_group(age):
    """Phân nhóm tuổi cho bệnh nhân"""
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
    """Tính toán tất cả các chỉ số thống kê cần thiết cho Dashboard"""
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
            "age_groups": {},
            "pie_data": {"icu": 0, "non_icu": 0}
        }
    
    # 1. Các chỉ số KPI cơ bản
    icu_count = sum(1 for p in patients if p['icu'] == 1)
    non_icu_count = total_patients - icu_count
    icu_rate = round((icu_count / total_patients) * 100, 1)
    
    avg_heart_rate = round(sum(p['heart_rate'] for p in patients) / total_patients, 1)
    avg_oxygen = round(sum(p['oxygen_saturation'] for p in patients) / total_patients, 1)
    
    # 2. Dữ liệu cho Pie Chart (ICU và Không ICU)
    pie_data = {
        "icu": icu_count,
        "non_icu": non_icu_count,
        "icu_rate": icu_rate
    }
    
    # Khởi tạo các nhóm tuổi
    age_groups_list = ["0-19", "20-39", "40-59", "60-79", "80+"]
    age_stats = {
        group: {
            "total": 0,
            "icu": 0,
            "heart_rate_sum": 0,
            "oxygen_sum": 0
        } for group in age_groups_list
    }
    
    # Phân nhóm bệnh nhân
    for p in patients:
        group = get_age_group(p['age'])
        age_stats[group]["total"] += 1
        age_stats[group]["heart_rate_sum"] += p['heart_rate']
        age_stats[group]["oxygen_sum"] += p['oxygen_saturation']
        if p['icu'] == 1:
            age_stats[group]["icu"] += 1
            
    # Tính toán kết quả cho Bar Chart và Line Chart theo nhóm tuổi
    bar_data = []
    line_data = []
    
    for group in age_groups_list:
        stats = age_stats[group]
        total = stats["total"]
        
        # Tính tỉ lệ ICU của từng nhóm
        group_icu_rate = round((stats["icu"] / total) * 100, 1) if total > 0 else 0
        avg_hr = round(stats["heart_rate_sum"] / total, 1) if total > 0 else 0
        avg_o2 = round(stats["oxygen_sum"] / total, 1) if total > 0 else 0
        
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
    """Lấy dữ liệu chuỗi thời gian của bệnh nhân nhập viện theo ngày"""
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
    return [
        {
            "admission_date": r[0],
            "patient_count": r[1],
            "avg_heart_rate": r[2],
            "avg_oxygen_saturation": r[3]
        }
        for r in rows
    ]

def get_risk_matrix_data():
    """Lấy danh sách bệnh nhân phân loại theo SpO2 và Nhịp tim để làm Ma trận rủi ro"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, age, gender, icu, heart_rate, oxygen_saturation, admission_date FROM patients")
    rows = cursor.fetchall()
    conn.close()
    
    classified = []
    for r in rows:
        p_id, name, age, gender, icu, hr, spo2, date = r
        
        # Phân loại SpO2: low (<90), medium (90-94), high (>=95)
        if spo2 >= 95:
            spo2_cat = "high"
        elif spo2 >= 90:
            spo2_cat = "medium"
        else:
            spo2_cat = "low"
            
        # Phân loại Nhịp tim: bradycardia (<60), normal (60-100), tachycardia (>100)
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
    """Tính toán hệ số tương quan (Pearson) và tỷ số Rủi ro tương đối (Relative Risk)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT age, oxygen_saturation, heart_rate, icu FROM patients")
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
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
        
    ages = [r[0] for r in rows]
    spo2s = [r[1] for r in rows]
    hrs = [r[2] for r in rows]
    icus = [r[3] for r in rows]
    
    n = len(rows)
    
    def correlation(x, y):
        mean_x = sum(x) / n
        mean_y = sum(y) / n
        num = sum((xi - mean_x) * (yi - mean_y) for xi, yi in zip(x, y))
        den_x = sum((xi - mean_x) ** 2 for xi in x)
        den_y = sum((yi - mean_y) ** 2 for yi in y)
        if den_x == 0 or den_y == 0:
            return 0
        return round(num / ((den_x * den_y) ** 0.5), 3)
        
    age_spo2_corr = correlation(ages, spo2s)
    age_hr_corr = correlation(ages, hrs)
    
    # Tính Rủi ro tương đối (Relative Risk) cho người lớn tuổi (>= 60) so với người trẻ (< 60)
    elderly_total = sum(1 for a in ages if a >= 60)
    elderly_icu = sum(1 for a, icu in zip(ages, icus) if a >= 60 and icu == 1)
    
    younger_total = sum(1 for a in ages if a < 60)
    younger_icu = sum(1 for a, icu in zip(ages, icus) if a < 60 and icu == 1)
    
    elderly_risk = (elderly_icu / elderly_total) if elderly_total > 0 else 0
    younger_risk = (younger_icu / younger_total) if younger_total > 0 else 0
    
    relative_risk = round(elderly_risk / younger_risk, 2) if younger_risk > 0 else (99.9 if elderly_risk > 0 else 1.0)
    
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
    """Dự báo số lượng bệnh nhân nhập viện trong 7 ngày tới sử dụng Hồi quy tuyến tính"""
    time_series = get_time_series_data()
    if not time_series:
        return []
        
    n = len(time_series)
    from datetime import datetime, timedelta
    
    if n < 2:
        last_val = time_series[0]["patient_count"] if n == 1 else 0
        forecast = []
        last_date_str = time_series[0]["admission_date"] if n == 1 else datetime.now().strftime("%Y-%m-%d")
        last_date = datetime.strptime(last_date_str, "%Y-%m-%d")
        for i in range(1, 8):
            next_date = last_date + timedelta(days=i)
            forecast.append({
                "admission_date": next_date.strftime("%Y-%m-%d"),
                "patient_count": last_val,
                "is_forecast": True
            })
        return forecast
        
    # Tính đường hồi quy tuyến tính: y = m * x + c
    x = list(range(n))
    y = [d["patient_count"] for d in time_series]
    
    mean_x = sum(x) / n
    mean_y = sum(y) / n
    
    num = sum((xi - mean_x) * (yi - mean_y) for xi, yi in zip(x, y))
    den = sum((xi - mean_x) ** 2 for xi in x)
    
    m = num / den if den != 0 else 0
    c = mean_y - m * mean_x
    
    # Dự báo tiếp 7 ngày từ ngày cuối cùng trong chuỗi thời gian
    last_date_str = time_series[-1]["admission_date"]
    last_date = datetime.strptime(last_date_str, "%Y-%m-%d")
    
    forecast = []
    for i in range(1, 8):
        next_date = last_date + timedelta(days=i)
        projected_x = n - 1 + i
        projected_y = max(0, m * projected_x + c) # Không cho phép số lượng âm
        forecast.append({
            "admission_date": next_date.strftime("%Y-%m-%d"),
            "patient_count": round(projected_y, 1),
            "is_forecast": True
        })
    return forecast

