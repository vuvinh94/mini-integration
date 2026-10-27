# Tiki Books End-to-End ETL Pipeline with Python & PostgreSQL

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue?logo=postgresql)
![Docker](https://img.shields.io/badge/Docker-✓-blue?logo=docker)
![Pandas](https://img.shields.io/badge/Pandas-2.2-blue?logo=pandas)
![Pandera](https://img.shields.io/badge/Pandera-0.19-blue?logo=pandera)
![Tests](https://img.shields.io/badge/tests-passing-brightgreen)

Pipeline ETL end-to-end trích xuất, làm sạch, xác thực và nạp dữ liệu sách và đánh giá Tiki (**Tiki Books Dataset**) vào PostgreSQL sử dụng giao thức `COPY` tốc độ cao.

---

## Kiến trúc Pipeline

```
┌───────────────────────────┐
│     data/raw/*.csv        │  ← book_data.csv, comments.csv (~140k dòng)
└─────────────┬─────────────┘
              │
              ▼
┌───────────────────────────┐
│          EXTRACT          │  Pandas read_csv (UTF-8)            
└─────────────┬─────────────┘
              │
              ▼
┌───────────────────────────┐
│         TRANSFORM         │  Làm sạch, khử trùng lặp, tính % discount
│       + VALIDATION        │  Pandera schema validation
└─────────────┬─────────────┘
              │
              ▼
┌───────────────────────────┐
│           LOAD            │  psycopg2 COPY protocol
└─────────────┬─────────────┘
              │
              ▼
┌───────────────────────────┐
│       PostgreSQL 15       │  Bảng books & comments kèm index
└─────────────┬─────────────┘
              │
              ▼
┌───────────────────────────┐
│       SQL Analytics       │  Top doanh thu, thể loại, NXB, phân bố rating
└───────────────────────────┘
```

---

## Cấu trúc thư mục

```
end-to-end-pipeline/
├── config/
│   └── config.yaml          # Cấu hình bảng và thứ tự load
├── data/raw/                # Dữ liệu nguồn: book_data.csv, comments.csv
├── logs/                    # File log tự động xoay vòng (rotating logs)
├── sql/
│   ├── 01_init_schema.sql   # DDL: tạo bảng books, comments, indexes
│   └── 02_analytics.sql     # Truy vấn phân tích kinh doanh
├── src/
│   ├── cli.py               # Giao diện dòng lệnh CLI
│   ├── config_loader.py     # Nạp cấu hình YAML + biến môi trường (.env)
│   ├── extract.py           # Trích xuất dữ liệu từ CSV (hỗ trợ UTF-8)
│   ├── transform.py         # Làm sạch và tính toán cột phái sinh
│   ├── validation.py        # Kiểm tra chất lượng dữ liệu bằng Pandera
│   ├── load.py              # Nạp dữ liệu vào PostgreSQL bằng COPY
│   ├── pipeline.py          # Điều phối luồng ETL
│   └── logging_config.py    # Cấu hình logging
├── tests/
│   └── test_transform.py    # Unit tests
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md
```

---

## Cách chạy

### 1. Khởi động PostgreSQL qua Docker

```powershell
docker compose up -d postgres
```

### 2. Khởi tạo Schema Database

> [!NOTE]
> Database được cấu hình với tài khoản: User = `tikibook`, Database = `tikibook_db`.

```powershell
Get-Content sql\01_init_schema.sql -Raw | docker exec -i olist_postgres psql -U tikibook -d tikibook_db
```

### 3. Kích hoạt môi trường ảo & Cài đặt thư viện

```powershell
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 4. Chạy toàn bộ Pipeline ETL

```powershell
python -m src.cli --stage all
```

### 5. Xem kết quả phân tích SQL Analytics

```powershell
Get-Content sql\02_analytics.sql -Raw | docker exec -i olist_postgres psql -U tikibook -d tikibook_db
```

### 6. Kết nối qua DBeaver / GUI Tools

* **Host:** `localhost`
* **Port:** `5433`
* **Database:** `tikibook_db`
* **Username:** `tikibook`
* **Password:** `tikibook`

### 7. Chạy Unit Test

```powershell
pytest
```