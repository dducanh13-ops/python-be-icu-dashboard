# Python Dashboard (FastAPI)

Dashboard đơn giản dùng **FastAPI + Jinja2 + SQLite**.

## Yêu cầu

- Windows + Python 3.10+ (khuyến nghị 3.11)
- PowerShell

## Cách chạy (khuyến nghị: tạo virtual env mới)

Tại thư mục dự án:

```powershell
cd d:\dashboard\python-dashboard

py -m venv .venv
.\.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
pip install -r requirements.txt

python -m uvicorn main:app --reload
```

Mở trình duyệt:

- UI: http://127.0.0.1:8000/
- Healthcheck: http://127.0.0.1:8000/ping
- Swagger (API docs): http://127.0.0.1:8000/docs

## Nếu bạn muốn dùng virtual env có sẵn trong repo

Repo hiện có thư mục `venv/`. Bạn có thể thử:

```powershell
cd d:\dashboard\python-dashboard
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m uvicorn main:app --reload
```

## Ghi chú

- Database SQLite nằm ở file `patients.db` (tự tạo/khởi tạo khi server start).
- Static files được mount tại `/static` và template nằm trong `templates/`.

## Troubleshooting nhanh

- Nếu PowerShell chặn activate venv:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

- Nếu lỗi thiếu module: chạy lại `pip install -r requirements.txt` trong đúng venv.
