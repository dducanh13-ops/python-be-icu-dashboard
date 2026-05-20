from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
import os
import openpyxl
from io import BytesIO
from datetime import datetime

# Import database module từ cùng thư mục
import db

app = FastAPI(title="ICU Patient Dashboard API", version="1.0.0")

# Cấu hình CORS để cho phép gọi API từ frontend trong lúc phát triển
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Khởi tạo database khi ứng dụng bắt đầu
@app.on_event("startup")
def startup_event():
    db.init_db()

# Khai báo cấu trúc dữ liệu cho Bệnh nhân mới (Sử dụng Pydantic)
class PatientCreate(BaseModel):
    name: str = Field(..., example="Nguyễn Văn A")
    age: int = Field(..., ge=0, le=120, example=45)
    gender: str = Field(..., example="Nam")
    icu: int = Field(..., ge=0, le=1, example=0)  # 0 hoặc 1
    heart_rate: int = Field(..., ge=30, le=250, example=75)
    oxygen_saturation: int = Field(..., ge=50, le=100, example=98)
    admission_date: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))

# ----------------- CÁC ENDPOINT API -----------------

@app.get("/api/patients")
def read_patients():
    """Lấy danh sách tất cả bệnh nhân"""
    try:
        return db.get_all_patients()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi truy vấn database: {str(e)}")

@app.post("/api/patients")
def create_patient(patient: PatientCreate):
    """Thêm một bệnh nhân mới thủ công qua Form"""
    try:
        # Kiểm tra định dạng ngày
        try:
            datetime.strptime(patient.admission_date, "%Y-%m-%d")
        except ValueError:
            # Nếu định dạng ngày sai, sử dụng ngày hôm nay
            patient.admission_date = datetime.now().strftime("%Y-%m-%d")

        patient_id = db.add_patient(
            name=patient.name,
            age=patient.age,
            gender=patient.gender,
            icu=patient.icu,
            heart_rate=patient.heart_rate,
            oxygen_saturation=patient.oxygen_saturation,
            admission_date=patient.admission_date
        )
        return {"status": "success", "id": patient_id, "message": "Đã thêm bệnh nhân thành công."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi thêm bệnh nhân: {str(e)}")

@app.delete("/api/patients/{patient_id}")
def delete_patient(patient_id: int):
    """Xóa một bệnh nhân theo ID"""
    try:
        success = db.delete_patient(patient_id)
        if not success:
            raise HTTPException(status_code=404, detail="Không tìm thấy bệnh nhân để xóa.")
        return {"status": "success", "message": "Đã xóa bệnh nhân thành công."}
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi xóa bệnh nhân: {str(e)}")

@app.delete("/api/patients")
def delete_all_patients():
    """Xóa toàn bộ bệnh nhân khỏi database"""
    try:
        db.delete_all_patients()
        return {"status": "success", "message": "Đã xóa toàn bộ bệnh nhân thành công."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi xóa toàn bộ bệnh nhân: {str(e)}")

@app.get("/api/patients/stats")
def read_stats():
    """Lấy dữ liệu thống kê cho các biểu đồ trên Dashboard"""
    try:
        return db.get_dashboard_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi tính toán thống kê: {str(e)}")

@app.get("/api/patients/time-series")
def read_time_series():
    """Lấy chuỗi thời gian số lượng bệnh nhân và chỉ số trung bình theo ngày"""
    try:
        return db.get_time_series_data()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi lấy dữ liệu chuỗi thời gian: {str(e)}")

@app.get("/api/patients/risk-matrix")
def read_risk_matrix():
    """Lấy danh sách bệnh nhân đã được phân loại theo nhịp tim và SpO2"""
    try:
        return db.get_risk_matrix_data()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi phân loại ma trận rủi ro: {str(e)}")

@app.get("/api/patients/advanced-stats")
def read_advanced_stats():
    """Lấy các chỉ số phân tích tương quan nâng cao và tỷ lệ Rủi ro tương đối"""
    try:
        return db.get_advanced_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi tính toán chỉ số nâng cao: {str(e)}")

@app.get("/api/patients/forecast")
def read_forecast():
    """Lấy dự báo số lượng bệnh nhân nhập viện trong 7 ngày tới"""
    try:
        return db.get_forecast_data()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi dự báo hồi quy: {str(e)}")

@app.get("/api/patients/sample-excel")
def download_sample_excel():
    """Tạo và tải về file Excel mẫu cho bệnh nhân"""
    try:
        # Khởi tạo Workbook mới
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Danh sách bệnh nhân"
        
        # Thêm tiêu đề cột (Headers)
        headers = ["Họ và Tên", "Tuổi", "Giới tính", "ICU (1=Có, 0=Không)", "Nhịp tim", "SpO2 (%)", "Ngày nhập viện (YYYY-MM-DD)"]
        ws.append(headers)
        
        # Thêm dữ liệu mẫu vào file Excel
        sample_rows = [
            ["Nguyễn Văn Anh", 45, "Nam", 0, 75, 98, "2026-05-20"],
            ["Trần Thị Mai", 72, "Nữ", 1, 95, 91, "2026-05-20"],
            ["Lê Hoàng Nam", 19, "Nam", 0, 80, 99, "2026-05-20"]
        ]
        for row in sample_rows:
            ws.append(row)
            
        # Điều chỉnh độ rộng cột tự động cho dễ đọc
        for col in ws.columns:
            max_len = max(len(str(cell.value or '')) for cell in col)
            col_letter = openpyxl.utils.get_column_letter(col[0].column)
            ws.column_dimensions[col_letter].width = max(max_len + 3, 12)
            
        # Lưu file vào bộ nhớ đệm (BytesIO) để stream trực tiếp
        file_stream = BytesIO()
        wb.save(file_stream)
        file_stream.seek(0)
        
        return StreamingResponse(
            file_stream,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment; filename=mau_du_lieu_benh_nhan.xlsx"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi tạo file mẫu Excel: {str(e)}")

@app.get("/api/patients/kaggle-excel")
def download_kaggle_excel():
    """Tải trực tiếp file dữ liệu Kaggle Sirio Libanes làm mẫu"""
    file_path = r"d:\dashboard\Kaggle_Sirio_Libanes_ICU_Prediction.xlsx"
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Không tìm thấy tệp Kaggle Sirio Libanes trên hệ thống.")
        
    def iterfile():
        with open(file_path, mode="rb") as f:
            yield from f
            
    return StreamingResponse(
        iterfile(),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={os.path.basename(file_path)}"}
    )

@app.post("/api/patients/import")
async def import_patients_excel(file: UploadFile = File(...)):
    """Đọc file Excel tải lên (Chuẩn hoặc Kaggle Sirio Libanes) và import vào SQLite"""
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="Chỉ hỗ trợ file Excel (.xlsx, .xls)")
        
    try:
        contents = await file.read()
        wb = openpyxl.load_workbook(filename=BytesIO(contents), data_only=True)
        ws = wb.active
        
        # Lấy tiêu đề cột dòng đầu tiên để phân biệt cấu trúc
        first_row = next(ws.iter_rows(max_row=1, values_only=True))
        if not first_row:
            raise HTTPException(status_code=400, detail="File Excel rỗng.")
            
        headers = [str(h).strip().upper() if h is not None else "" for h in first_row]
        
        imported_count = 0
        skipped_count = 0
        
        # 1. PHÂN TÍCH THEO PHƯƠNG THỨC KAGGLE SIRIO LIBANES (nếu có cột PATIENT_VISIT_IDENTIFIER)
        if "PATIENT_VISIT_IDENTIFIER" in headers:
            try:
                idx_id = headers.index("PATIENT_VISIT_IDENTIFIER")
                idx_age_above65 = headers.index("AGE_ABOVE65") if "AGE_ABOVE65" in headers else -1
                idx_age_percentil = headers.index("AGE_PERCENTIL") if "AGE_PERCENTIL" in headers else -1
                idx_gender = headers.index("GENDER") if "GENDER" in headers else -1
                idx_hr = headers.index("HEART_RATE_MEAN") if "HEART_RATE_MEAN" in headers else -1
                idx_spo2 = headers.index("OXYGEN_SATURATION_MEAN") if "OXYGEN_SATURATION_MEAN" in headers else -1
                idx_icu = headers.index("ICU") if "ICU" in headers else -1
                
                patients_dict = {}
                
                # Gom dữ liệu theo từng bệnh nhân (do mỗi bệnh nhân có nhiều dòng/cửa sổ quan sát)
                for row in ws.iter_rows(min_row=2, values_only=True):
                    if not row or len(row) <= idx_id or row[idx_id] is None:
                        continue
                        
                    p_id = int(row[idx_id])
                    if p_id not in patients_dict:
                        patients_dict[p_id] = {
                            "age_above65": row[idx_age_above65] if idx_age_above65 != -1 and len(row) > idx_age_above65 else 0,
                            "age_percentil": str(row[idx_age_percentil]) if idx_age_percentil != -1 and len(row) > idx_age_percentil and row[idx_age_percentil] is not None else "",
                            "gender": row[idx_gender] if idx_gender != -1 and len(row) > idx_gender else 0,
                            "hr_list": [],
                            "spo2_list": [],
                            "icu_list": []
                        }
                    
                    if idx_hr != -1 and len(row) > idx_hr and row[idx_hr] is not None:
                        patients_dict[p_id]["hr_list"].append(float(row[idx_hr]))
                    if idx_spo2 != -1 and len(row) > idx_spo2 and row[idx_spo2] is not None:
                        patients_dict[p_id]["spo2_list"].append(float(row[idx_spo2]))
                    if idx_icu != -1 and len(row) > idx_icu and row[idx_icu] is not None:
                        patients_dict[p_id]["icu_list"].append(int(row[idx_icu]))
                
                # Import từng bệnh nhân vào cơ sở dữ liệu
                for p_id, data in patients_dict.items():
                    try:
                        # Map Age Percentil -> Tuổi số thực tế
                        age = 35
                        ap = data["age_percentil"]
                        if ap:
                            if "10TH" in ap.upper(): age = 15
                            elif "20TH" in ap.upper(): age = 25
                            elif "30TH" in ap.upper(): age = 35
                            elif "40TH" in ap.upper(): age = 45
                            elif "50TH" in ap.upper(): age = 55
                            elif "60TH" in ap.upper(): age = 65
                            elif "70TH" in ap.upper(): age = 75
                            elif "80TH" in ap.upper(): age = 85
                            elif "90TH" in ap.upper(): age = 90
                            elif "ABOVE 90" in ap.upper(): age = 95
                        else:
                            if data["age_above65"] == 1:
                                age = 70
                        
                        # Map Gender (0 = Nam, 1 = Nữ)
                        gender = "Nam" if data["gender"] == 0 else "Nữ"
                        
                        # ICU (nếu có bất kỳ cửa sổ nào cần ICU, ta tính là có ICU)
                        icu = 1 if (1 in data["icu_list"]) else 0
                        
                        # Map nhịp tim từ min-max scale [-1, 1] về thực tế [50, 120]
                        if data["hr_list"]:
                            avg_hr_norm = sum(data["hr_list"]) / len(data["hr_list"])
                            heart_rate = int((avg_hr_norm + 1) / 2 * (120 - 50) + 50)
                            heart_rate = max(30, min(250, heart_rate))
                        else:
                            heart_rate = 80
                            
                        # Map SpO2 từ min-max scale [-1, 1] về thực tế [80, 100]
                        if data["spo2_list"]:
                            # Lấy giá trị SpO2 thấp nhất ghi nhận được (tình trạng tệ nhất)
                            min_spo2_norm = min(data["spo2_list"])
                            oxygen_saturation = int((min_spo2_norm + 1) / 2 * (100 - 80) + 80)
                            oxygen_saturation = max(50, min(100, oxygen_saturation))
                        else:
                            oxygen_saturation = 98
                            
                        # Tạo ngày nhập viện giả lập phân bố đều trong 15 ngày qua
                        day_diff = p_id % 15
                        from datetime import timedelta
                        admission_date = (datetime.now() - timedelta(days=day_diff)).strftime("%Y-%m-%d")
                        
                        name = f"Bệnh nhân Sirio #{p_id}"
                        
                        db.add_patient(name, age, gender, icu, heart_rate, oxygen_saturation, admission_date)
                        imported_count += 1
                    except Exception:
                        skipped_count += 1
                        continue
                        
            except Exception as kaggle_err:
                raise HTTPException(status_code=400, detail=f"Lỗi cấu trúc dữ liệu Kaggle: {str(kaggle_err)}")
                
        # 2. PHÂN TÍCH THEO PHƯƠNG THỨC EXCEL MẪU CHUẨN (7 cột)
        else:
            for r_idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
                if not row or not any(cell is not None for cell in row):
                    continue
                    
                try:
                    name = str(row[0]).strip() if row[0] is not None else "Bệnh nhân ẩn danh"
                    age = int(row[1]) if row[1] is not None else 0
                    gender = str(row[2]).strip() if row[2] is not None else "Không rõ"
                    icu = int(row[3]) if row[3] is not None else 0
                    icu = 1 if icu > 0 else 0
                    
                    heart_rate = int(row[4]) if row[4] is not None else 80
                    oxygen_saturation = int(row[5]) if row[5] is not None else 98
                    
                    raw_date = row[6]
                    if isinstance(raw_date, datetime):
                        admission_date = raw_date.strftime("%Y-%m-%d")
                    elif raw_date is not None:
                        raw_date_str = str(raw_date).strip()
                        try:
                            datetime.strptime(raw_date_str, "%Y-%m-%d")
                            admission_date = raw_date_str
                        except ValueError:
                            try:
                                parsed_date = datetime.strptime(raw_date_str, "%d/%m/%Y")
                                admission_date = parsed_date.strftime("%Y-%m-%d")
                            except ValueError:
                                admission_date = datetime.now().strftime("%Y-%m-%d")
                    else:
                        admission_date = datetime.now().strftime("%Y-%m-%d")
                    
                    db.add_patient(name, age, gender, icu, heart_rate, oxygen_saturation, admission_date)
                    imported_count += 1
                except Exception:
                    skipped_count += 1
                    continue
                    
        return {
            "status": "success", 
            "message": f"Nhập thành công {imported_count} bệnh nhân. Bỏ qua {skipped_count} dòng lỗi.",
            "imported": imported_count,
            "skipped": skipped_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi xử lý file Excel: {str(e)}")

# ----------------- HOSTING FRONTEND STATIC FILES -----------------

# Mount thư mục chứa frontend tĩnh tại đường dẫn gốc '/'
# Lưu ý: backend và frontend cùng thư mục gốc d:\dashboard.
# Đường dẫn tương đối từ d:\dashboard\python-dashboard-be đến python-dashboard-fe là ../python-dashboard-fe
frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "python-dashboard-fe"))

if os.path.exists(frontend_dir):
    # Mount frontend static files
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="static")
else:
    # Nếu thư mục frontend chưa tồn tại, tạm thời không mount để tránh crash server
    print(f"Warning: Frontend directory not found at {frontend_dir}")
