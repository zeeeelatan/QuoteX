from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel
import json
from pathlib import Path

router = APIRouter()

# 数据文件路径
DATA_FILE = Path("data/service_levels.json")
DATA_FILE.parent.mkdir(parents=True, exist_ok=True)

# 数据模型
class ServiceLevel(BaseModel):
    id: Optional[int] = None
    service_level: str
    response_time: str
    coefficient: float

class ServiceLevelImport(BaseModel):
    data: List[ServiceLevel]

# 初始化数据文件
if not DATA_FILE.exists():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump([], f, ensure_ascii=False, indent=2)

def load_data() -> List[dict]:
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data: List[dict]):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, ensure_ascii=False, indent=2, default=str)

@router.get("/")
async def get_service_levels():
    return load_data()

@router.post("/")
async def create_service_level(service_level: ServiceLevel):
    data = load_data()
    new_id = max([item["id"] for item in data], default=0) + 1
    service_level_dict = service_level.dict()
    service_level_dict["id"] = new_id
    data.append(service_level_dict)
    save_data(data)
    return service_level_dict

@router.put("/{service_level_id}")
async def update_service_level(service_level_id: int, service_level: ServiceLevel):
    data = load_data()
    for i, item in enumerate(data):
        if item["id"] == service_level_id:
            service_level_dict = service_level.dict()
            service_level_dict["id"] = service_level_id
            data[i] = service_level_dict
            save_data(data)
            return service_level_dict
    raise HTTPException(status_code=404, detail="Service level not found")

@router.delete("/{service_level_id}")
async def delete_service_level(service_level_id: int):
    data = load_data()
    for i, item in enumerate(data):
        if item["id"] == service_level_id:
            del data[i]
            save_data(data)
            return {"message": "Service level deleted"}
    raise HTTPException(status_code=404, detail="Service level not found")

@router.post("/import")
async def import_service_levels(import_data: ServiceLevelImport):
    data = []
    for idx, item in enumerate(import_data.data):
        service_level_dict = item.dict()
        service_level_dict["id"] = idx + 1
        data.append(service_level_dict)
    save_data(data)
    return {"message": f"Successfully imported {len(data)} service levels"}

@router.delete("/clear")
async def clear_service_levels():
    save_data([])
    return {"message": "All service levels cleared"} 