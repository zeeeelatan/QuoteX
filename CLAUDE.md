# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

智能报价系统 (AI Quotation System) - A B2B device quotation generation system that matches device models from uploaded Excel files, applies maintenance rates and service level pricing, and generates quotations.

**Core Capabilities:**
- Multi-source device matching (datacenter/office/hybrid) with fuzzy matching algorithms
- Dynamic pricing with maintenance rate lookups and service level coefficient adjustments
- Excel import/export for device data, rates, service levels, GPU pricing, and spare parts
- Admin dashboard for configuration management

## Technology Stack

**Backend:**
- FastAPI (Python) with Uvicorn ASGI server
- PostgreSQL database with SQLAlchemy ORM
- Pydantic for data validation
- Pandas/OpenPyXL for Excel processing

**Frontend:**
- Vue 3 (Composition API) with TypeScript
- Vite build tool
- Element Plus UI library
- XLSX library for Excel I/O

## Development Commands

### Backend

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn app.main:app --reload --port 5002 --host 0.0.0.0

# Alternative: Use project script
python run.py
```

**Database Setup:**
- Configure via environment variables: `DATABASE_URL` or individual vars (`DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`)
- Default: PostgreSQL on localhost, database `device_inventory_ai_quote_test`
- No migration system - models auto-create tables via SQLAlchemy

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Run development server (port 3008)
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

**Environment Configuration:**
- Set `VITE_API_BASE_URL` to override backend URL (default: http://localhost:5002)
- Frontend auto-detects API endpoint based on access method (IP vs localhost)

### Full System Startup

Use convenience scripts from project root:
```bash
./start.sh              # Start both frontend and backend
./start_backend.sh      # Backend only
./start_frontend.sh     # Frontend only
./stop.sh               # Stop all services
```

**Service Ports:**
- Backend API: 5002
- Frontend Dev: 3008
- Frontend Access: http://localhost:3008

## Architecture & System Flow

### Database Schema

**Core Tables:**

1. **device_inventory** / **office_device_inventory**
   - Separate tables for datacenter vs office equipment
   - Fields: manufacturer, model_number, device_price, primary/secondary/tertiary_category, device_grade, device_series
   - Source selection enables targeted or merged searches

2. **maintenance_rate**
   - Hierarchical rate lookup by primary_category → secondary_category → tertiary_category
   - Rate stored as decimal (0.08 = 8%)
   - Used to calculate maintenance prices: `device_price * rate * 1.06`

3. **service_level**
   - level_code: Service tier name (e.g., "7*24*3")
   - response_time: SLA description (e.g., "2小时工程师和备件到达")
   - coefficient: Price multiplier (e.g., 1.2)

4. **gpu_price**
   - GPU-specific pricing with auto-calculated repair costs
   - Fields: manufacturer, series, model, gpu_memory, gpu_price, gpu_rate, spare_repair_cost, labor_repair_cost

5. **spare_part**
   - Spare parts inventory: manufacturer, part_pn, part_desc, unit_price, repair_method, repair_period

### Device Matching Algorithm

**Location:** `/backend/app/matching.py`

**Three-Tier Strategy:**

1. **Exact Match (100% confidence)** - Normalized model string equality
2. **Prefix Match (90% confidence)** - Substring matching
3. **Fuzzy Match (70%+ confidence)** - SequenceMatcher with dynamic weighting
   - High similarity (>90%): 80% model + 20% manufacturer
   - Medium similarity (>80%): 70% model + 30% manufacturer
   - Lower similarity: 60% model + 40% manufacturer

**Key Functions:**
- `normalize_manufacturer()`: Maps brand aliases to canonical names (e.g., 'hp' → '惠普&慧与/HP&HPE')
- `normalize_model()`: Strips whitespace, uppercases, removes special chars
- `match_device()`: Executes three-tier matching and calculates maintenance price

**Data Source Selection:**
- 'datacenter': Uses device_inventory table only
- 'office': Uses office_device_inventory table only
- 'hybrid': Merges both sources, orders by match score

### Quotation Pipeline

```
Excel Upload → Parse Devices → Bulk Match API
    ↓
Match Device Models (3-tier algorithm)
    ↓
Lookup Maintenance Rate (by category hierarchy)
    ↓
Calculate Base Price = device_price * rate * 1.06
    ↓
Parse Service Level Requirement (e.g., "7*24*3")
    ↓
Match Available Service Levels → Get Coefficient
    ↓
Calculate Adjusted Price = base_price * coefficient
    ↓
Display Results Table → Export Quotation Excel
```

### API Endpoints

**Device Matching:**
- `GET /devices/search/?model={model}&source={datacenter|office|hybrid}&limit={N}&offset={N}` - Search devices
- `POST /match/` - Single device matching
- `POST /bulk-match/` - Batch matching (accepts array of {manufacturer, model, category, source})

**Admin Management:**
- `GET|POST|PUT|DELETE /maintenance_rates/` - CRUD operations
- `POST /maintenance_rates/import` - Bulk import from JSON
- `GET|POST|PUT|DELETE /service-level/` - Service level management
- `GET /service-level/template` - Download Excel template
- `POST /service-level/import` - Upload Excel with validation
- `GET|POST|DELETE /gpu_prices/` - GPU pricing management
- `GET|POST|DELETE /spare_parts/` - Spare parts management

### Frontend Architecture

**Main Entry:** `/frontend/src/main.ts` - Routes to legacy App.vue or new router-based system

**Legacy App.vue (2700+ lines):**
- State-based navigation via `activeFunction` property
- Main sections:
  1. **智能识别** - Document recognition and Excel parsing
  2. **智能匹配** - Device matching with manual override capability
  3. **生成报价单** - Quotation generation and export
  4. **手动搜索** - Manual device search
  5. **后台管理** - Admin dashboard (rates, service levels, GPU prices, spare parts)

**API Integration:** `/frontend/src/api.js`
- Auto-detects backend URL based on access method (IP vs localhost)
- Exports: `matchDevices()`, `searchDevice()`

**Service Level Logic:** `/frontend/src/serviceLevelUtils.js`
- `parseServiceLevel()`: Extracts hours/type from formats like "7*24*3"
- `matchServiceLevel()`: Finds best available level meeting requirements
- `calculateServiceLevelPrice()`: Applies coefficient multiplier

## UI Standards

**Button Consistency (from .cursorrules):**
- Always use Element Plus `el-button`
- Color mapping:
  - Primary actions: `type="primary"`
  - Downloads/success: `type="success"`
  - Imports/warnings: `type="warning"`
  - Clear/delete: `type="danger"`
- Button spacing: Use flexbox containers with `gap: 12px`, avoid manual margins
- File uploads: Hidden `<input type="file">` triggered by `el-button`
- Download actions: Use `window.open()` to call API endpoints

## Common Patterns

### Adding a New Device Source

1. Create new table in `/backend/app/models/` (inherit from Base)
2. Update `/backend/app/matching.py` to add source to `match_device()`
3. Add source option to frontend dropdown in App.vue
4. Update `/devices/search/` endpoint to handle new source parameter

### Adding a New Admin Table

1. Define SQLAlchemy model in `/backend/app/models/`
2. Create Pydantic schemas in `/backend/app/schemas/`
3. Create router in `/backend/app/routers/` with CRUD endpoints
4. Include router in `/backend/app/main.py`
5. Add frontend section to App.vue admin dropdown
6. Implement table display and import/export UI using Element Plus components

### Excel Import/Export Pattern

**Backend:**
```python
# Import
import pandas as pd
df = pd.read_excel(file)
for _, row in df.iterrows():
    # Validate and insert records

# Export
from openpyxl import Workbook
wb = Workbook()
ws = wb.active
# Populate workbook, return StreamingResponse
```

**Frontend:**
```javascript
// Import
import * as XLSX from 'xlsx'
const workbook = XLSX.read(data, { type: 'array' })
const sheet = workbook.Sheets[workbook.SheetNames[0]]
const jsonData = XLSX.utils.sheet_to_json(sheet)

// Export
import { saveAs } from 'file-saver'
const ws = XLSX.utils.json_to_sheet(data)
const wb = XLSX.utils.book_new()
XLSX.utils.book_append_sheet(wb, ws, 'Sheet1')
const wbout = XLSX.write(wb, { bookType: 'xlsx', type: 'array' })
saveAs(new Blob([wbout]), 'filename.xlsx')
```

## Key Business Rules

1. **Maintenance Rate Lookup:** Falls back through tertiary → secondary → primary category, defaults to 0.02 (2%) if no match
2. **Price Calculation:** `maintenance_price = device_price * rate * 1.06` (includes 6% markup)
3. **Service Level Matching:** Prioritizes exact type match, then lower response time, then higher coefficient
4. **Match Rate Color Coding:** High (>85% green), Medium (70-85% yellow), Low (<70% red), None (gray)
5. **GPU Price Auto-Calculation:** `spare_repair_cost = gpu_price * gpu_rate`, `service_fee = spare_repair_cost + labor_repair_cost`

## Database Connection Notes

The backend supports flexible database configuration:
- Full URL: Set `DATABASE_URL` environment variable
- Component-based: Set `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`
- Default: Uses `device_inventory_ai_quote_test` database on localhost PostgreSQL

No explicit migration system - tables are created on first run via SQLAlchemy's `create_all()`.
