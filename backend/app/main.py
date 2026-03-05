import os
from pathlib import Path
from dotenv import load_dotenv

# 加载项目根目录 .env（本地开发时读取，Docker 环境由 compose 注入）
_env_file = Path(__file__).resolve().parent.parent.parent / ".env"
if _env_file.exists():
    load_dotenv(_env_file, override=False)

from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from . import models, schemas, matching
from .database import engine, get_db, Base
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from app.routers import maintenance_rate, service_level
from app.routers import gpu_price
from app.routers import spare_part
from app.routers import manual_matching_override
from app.routers import quote_history
from app.routers import product_parameter
from app.routers import service_terms
from app.routers import service_personnel
from app.routers import pricing_parameter
from app.routers import single_service
from app.routers import outsourced_personnel
from app.routers import dispatch_service
from app.routers import superimposed_price
from app.routers import city_social_insurance
from app.routers import china_city_tier
from app.routers import relocation_vehicle
from app.routers import device_inventory, office_device_inventory
from app.routers import user_profile, auth
from app.routers import ai_quote
from app.routers import document_parser
from app.seed_default_user import ensure_default_user

app = FastAPI(title="智能报价系统API")


@app.get("/health")
def health():
    """供 Docker / 负载均衡 / CI 健康检查"""
    return {"status": "ok"}


def _wait_for_db(max_attempts: int = 30, interval: float = 1.0):
    """等待数据库可用后再执行 create_all / 默认用户，避免容器启动时 postgres 未就绪"""
    from sqlalchemy import text
    for attempt in range(1, max_attempts + 1):
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return
        except Exception as e:
            if attempt == max_attempts:
                raise
            import time
            time.sleep(interval)


@app.on_event("startup")
def on_startup():
    """确保数据库就绪、表存在、默认账户存在"""
    _wait_for_db()
    # 优先尝试 Alembic 迁移；若 Alembic 未初始化则退回 create_all
    try:
        from alembic.config import Config
        from alembic import command
        import os
        alembic_ini = os.path.join(os.path.dirname(os.path.dirname(__file__)), "alembic.ini")
        if os.path.exists(alembic_ini):
            alembic_cfg = Config(alembic_ini)
            command.upgrade(alembic_cfg, "head")
        else:
            Base.metadata.create_all(bind=engine)
    except Exception:
        # Alembic 迁移失败时退回 create_all，确保首次部署仍能启动
        Base.metadata.create_all(bind=engine)
    ensure_default_user()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi import Query

@app.get("/search/")
def search_devices(
    model_number: str = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(models.DeviceInventory)
    if model_number:
        query = query.filter(models.DeviceInventory.model_number.ilike(f"%{model_number}%"))
    devices = query.all()
    return [
        {col.name: getattr(device, col.name) for col in device.__table__.columns}
        for device in devices
    ]

@app.get("/devices/search/")
def devices_search(
    model: str = Query(None),
    model_number: str = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    source: str = Query('datacenter'),  # datacenter | office | hybrid
    db: Session = Depends(get_db)
):
    from app.models.office_device_inventory import OfficeDeviceInventory

    def base_query(table_cls):
        from sqlalchemy import case, or_
        import re
        q = db.query(table_cls)
        if model or model_number:
            keyword = model or model_number
            
            # 智能搜索：生成多个搜索变体
            # 1. 原始关键词
            # 2. 去掉常见后缀（-S, -A, -B, -X, -E 等）
            # 3. 去掉所有横杠后的部分
            search_variants = [keyword]
            
            # 去掉常见后缀
            suffix_pattern = r'[-_]?[A-Za-z]$'
            base_keyword = re.sub(suffix_pattern, '', keyword)
            if base_keyword and base_keyword != keyword:
                search_variants.append(base_keyword)
            
            # 去掉最后一个横杠后的所有内容
            if '-' in keyword:
                base_part = keyword.rsplit('-', 1)[0]
                if base_part and base_part not in search_variants:
                    search_variants.append(base_part)
            
            # 构建 OR 条件：任一变体匹配即可
            filter_conditions = []
            for variant in search_variants:
                filter_conditions.append(table_cls.model_number.ilike(f"%{variant}%"))
            
            q = q.filter(or_(*filter_conditions))
            
            # 精确匹配的排在前面，然后是包含关键词的
            q = q.order_by(
                case(
                    (table_cls.model_number == keyword, 1),
                    (table_cls.model_number.ilike(f"{keyword}%"), 2),
                    else_=3
                ),
                table_cls.model_number
            )
        return q

    if source == 'datacenter':
        q = base_query(models.DeviceInventory)
        total = q.count()
        devices = q.offset(offset).limit(limit).all()
    elif source == 'office':
        q = base_query(OfficeDeviceInventory)
        total = q.count()
        devices = q.offset(offset).limit(limit).all()
    else:  # hybrid
        # 对于混合模式，我们需要分别查询然后合并并排序
        q1 = base_query(models.DeviceInventory)
        q2 = base_query(OfficeDeviceInventory)
        total1 = q1.count()
        total2 = q2.count()
        total = total1 + total2
        
        devices1 = q1.all()
        devices2 = q2.all()
        
        # 合并结果并按匹配度排序
        all_devices = []
        if model or model_number:
            keyword = model or model_number
            # 为每个设备添加匹配度
            for device in devices1 + devices2:
                match_score = 1 if device.model_number == keyword else 2
                all_devices.append((match_score, device.model_number, device))
            
            # 按匹配度和型号排序
            all_devices.sort(key=lambda x: (x[0], x[1]))
            devices = [x[2] for x in all_devices[offset:offset+limit]]
        else:
            devices = (devices1 + devices2)[offset:offset+limit]

    return {
        "data": [
            {col.name: getattr(device, col.name) for col in device.__table__.columns}
            for device in devices
        ],
        "total": total
    }

@app.get("/")
def read_root():
    return {"message": "智能报价系统API"}

@app.post("/match/", response_model=schemas.MatchResponse)
def match_device(request: schemas.MatchRequest, db: Session = Depends(get_db)):
    result = matching.match_device(
        db=db,
        manufacturer=request.manufacturer,
        model=request.model,
        category=request.category,
        source=request.source or 'datacenter'
    )
    return result

@app.post("/bulk-match/", response_model=List[schemas.MatchResponse])
def bulk_match_devices(request: schemas.BulkMatchRequest, db: Session = Depends(get_db)):
    results = []
    for item in request.items:
        result = matching.match_device(
            db=db,
            manufacturer=item.manufacturer,
            model=item.model,
            category=item.category,
            source=item.source or 'datacenter'
        )
        results.append(result)
    return results

app.include_router(maintenance_rate.router)
app.include_router(service_level.router)
app.include_router(product_parameter.router)
app.include_router(gpu_price.router)
app.include_router(spare_part.router)
app.include_router(manual_matching_override.router)
app.include_router(quote_history.router)
app.include_router(service_terms.router)
app.include_router(service_personnel.router)
app.include_router(pricing_parameter.router)
app.include_router(single_service.router)
app.include_router(outsourced_personnel.router)
app.include_router(dispatch_service.router)
app.include_router(superimposed_price.router)
app.include_router(city_social_insurance.router)
app.include_router(china_city_tier.router)
app.include_router(relocation_vehicle.router)
app.include_router(device_inventory.router)
app.include_router(office_device_inventory.router)
app.include_router(user_profile.router)
app.include_router(auth.router)
app.include_router(ai_quote.router)
app.include_router(document_parser.router)