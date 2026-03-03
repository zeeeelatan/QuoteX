from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.schemas.product_parameter import (
    BaseRateCreate, BaseRateUpdate, BaseRateOut,
    SLAConfigCreate, SLAConfigUpdate, SLAConfigOut,
    HardwareDepreciationCreate, HardwareDepreciationUpdate, HardwareDepreciationOut,
    RegionalAdjustmentCreate, RegionalAdjustmentUpdate, RegionalAdjustmentOut,
    ProductParametersOut
)
from app.models.product_parameter import (
    BaseRate, SLAConfig, HardwareDepreciation, RegionalAdjustment
)
from app.database import get_db

router = APIRouter(prefix="/product_parameters", tags=["产品参数管理"])


# ============ 基础费率 API ============
@router.get("/base_rates", response_model=List[BaseRateOut])
def list_base_rates(db: Session = Depends(get_db)):
    """获取所有基础费率"""
    return db.query(BaseRate).all()


@router.post("/base_rates", response_model=BaseRateOut)
def create_base_rate(rate: BaseRateCreate, db: Session = Depends(get_db)):
    """创建基础费率"""
    # 检查代码是否已存在
    existing = db.query(BaseRate).filter(BaseRate.level_code == rate.level_code).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"级别代码 {rate.level_code} 已存在")
    db_rate = BaseRate(
        level_code=rate.level_code,
        level_name=rate.level_name,
        level_desc=rate.level_desc,
        rate_value=rate.rate_value / 100,  # 百分比转小数
        trend_value=rate.trend_value / 100 if rate.trend_value else None
    )
    db.add(db_rate)
    db.commit()
    db.refresh(db_rate)
    return db_rate


@router.put("/base_rates/{rate_id}", response_model=BaseRateOut)
def update_base_rate(rate_id: int, rate: BaseRateUpdate, db: Session = Depends(get_db)):
    """更新基础费率"""
    db_rate = db.query(BaseRate).filter(BaseRate.id == rate_id).first()
    if not db_rate:
        raise HTTPException(status_code=404, detail="费率不存在")
    for k, v in rate.dict(exclude_unset=True).items():
        if k == 'rate_value' and v is not None:
            setattr(db_rate, k, v / 100)
        elif k == 'trend_value' and v is not None:
            setattr(db_rate, k, v / 100)
        else:
            setattr(db_rate, k, v)
    db.commit()
    db.refresh(db_rate)
    return db_rate


@router.delete("/base_rates/{rate_id}")
def delete_base_rate(rate_id: int, db: Session = Depends(get_db)):
    """删除基础费率"""
    db_rate = db.query(BaseRate).filter(BaseRate.id == rate_id).first()
    if not db_rate:
        raise HTTPException(status_code=404, detail="费率不存在")
    db.delete(db_rate)
    db.commit()
    return {"ok": True}


# ============ SLA配置 API ============
@router.get("/sla_configs", response_model=List[SLAConfigOut])
def list_sla_configs(db: Session = Depends(get_db)):
    """获取所有SLA配置"""
    return db.query(SLAConfig).all()


@router.post("/sla_configs", response_model=SLAConfigOut)
def create_sla_config(config: SLAConfigCreate, db: Session = Depends(get_db)):
    """创建调节系数配置"""
    db_config = SLAConfig(
        coefficient_name=config.coefficient_name,
        description=config.description,
        coefficient=config.coefficient
    )
    db.add(db_config)
    db.commit()
    db.refresh(db_config)
    return db_config


@router.put("/sla_configs/{config_id}", response_model=SLAConfigOut)
def update_sla_config(config_id: int, config: SLAConfigUpdate, db: Session = Depends(get_db)):
    """更新调节系数配置"""
    db_config = db.query(SLAConfig).filter(SLAConfig.id == config_id).first()
    if not db_config:
        raise HTTPException(status_code=404, detail="调节系数配置不存在")

    update_data = config.dict(exclude_unset=True)
    if 'coefficient_name' in update_data:
        db_config.coefficient_name = update_data['coefficient_name']
    if 'description' in update_data:
        db_config.description = update_data['description']
    if 'coefficient' in update_data:
        db_config.coefficient = update_data['coefficient']

    db.commit()
    db.refresh(db_config)
    return db_config


@router.delete("/sla_configs/{config_id}")
def delete_sla_config(config_id: int, db: Session = Depends(get_db)):
    """删除调节系数配置"""
    db_config = db.query(SLAConfig).filter(SLAConfig.id == config_id).first()
    if not db_config:
        raise HTTPException(status_code=404, detail="调节系数配置不存在")
    db.delete(db_config)
    db.commit()
    return {"ok": True}


# ============ 硬件折旧 API ============
@router.get("/hardware_depreciations", response_model=List[HardwareDepreciationOut])
def list_hardware_depreciations(db: Session = Depends(get_db)):
    """获取所有硬件折旧系数"""
    return db.query(HardwareDepreciation).all()


@router.post("/hardware_depreciations", response_model=HardwareDepreciationOut)
def create_hardware_depreciation(dep: HardwareDepreciationCreate, db: Session = Depends(get_db)):
    """创建硬件折旧系数"""
    # 检查设备类型是否已存在
    existing = db.query(HardwareDepreciation).filter(
        HardwareDepreciation.device_type == dep.device_type
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"设备类型 {dep.device_type} 已存在")
    db_dep = HardwareDepreciation(
        device_type=dep.device_type,
        rate_value=dep.rate_value / 100  # 百分比转小数
    )
    db.add(db_dep)
    db.commit()
    db.refresh(db_dep)
    return db_dep


@router.put("/hardware_depreciations/{dep_id}", response_model=HardwareDepreciationOut)
def update_hardware_depreciation(dep_id: int, dep: HardwareDepreciationUpdate, db: Session = Depends(get_db)):
    """更新硬件折旧系数"""
    db_dep = db.query(HardwareDepreciation).filter(HardwareDepreciation.id == dep_id).first()
    if not db_dep:
        raise HTTPException(status_code=404, detail="硬件折旧配置不存在")
    for k, v in dep.dict(exclude_unset=True).items():
        if k == 'rate_value' and v is not None:
            setattr(db_dep, k, v / 100)
        else:
            setattr(db_dep, k, v)
    db.commit()
    db.refresh(db_dep)
    return db_dep


@router.delete("/hardware_depreciations/{dep_id}")
def delete_hardware_depreciation(dep_id: int, db: Session = Depends(get_db)):
    """删除硬件折旧系数"""
    db_dep = db.query(HardwareDepreciation).filter(HardwareDepreciation.id == dep_id).first()
    if not db_dep:
        raise HTTPException(status_code=404, detail="硬件折旧配置不存在")
    db.delete(db_dep)
    db.commit()
    return {"ok": True}


# ============ 区域调节 API ============
@router.get("/regional_adjustments", response_model=List[RegionalAdjustmentOut])
def list_regional_adjustments(db: Session = Depends(get_db)):
    """获取所有区域调节系数"""
    return db.query(RegionalAdjustment).all()


@router.post("/regional_adjustments", response_model=RegionalAdjustmentOut)
def create_regional_adjustment(adj: RegionalAdjustmentCreate, db: Session = Depends(get_db)):
    """创建区域调节系数"""
    # 检查区域代码是否已存在
    existing = db.query(RegionalAdjustment).filter(
        RegionalAdjustment.region_code == adj.region_code
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"区域代码 {adj.region_code} 已存在")
    db_adj = RegionalAdjustment(**adj.dict())
    db.add(db_adj)
    db.commit()
    db.refresh(db_adj)
    return db_adj


@router.put("/regional_adjustments/{adj_id}", response_model=RegionalAdjustmentOut)
def update_regional_adjustment(adj_id: int, adj: RegionalAdjustmentUpdate, db: Session = Depends(get_db)):
    """更新区域调节系数"""
    db_adj = db.query(RegionalAdjustment).filter(RegionalAdjustment.id == adj_id).first()
    if not db_adj:
        raise HTTPException(status_code=404, detail="区域调节配置不存在")
    for k, v in adj.dict(exclude_unset=True).items():
        setattr(db_adj, k, v)
    db.commit()
    db.refresh(db_adj)
    return db_adj


@router.delete("/regional_adjustments/{adj_id}")
def delete_regional_adjustment(adj_id: int, db: Session = Depends(get_db)):
    """删除区域调节系数"""
    db_adj = db.query(RegionalAdjustment).filter(RegionalAdjustment.id == adj_id).first()
    if not db_adj:
        raise HTTPException(status_code=404, detail="区域调节配置不存在")
    db.delete(db_adj)
    db.commit()
    return {"ok": True}


# ============ 批量获取所有配置 ============
@router.get("/all", response_model=ProductParametersOut)
def get_all_parameters(db: Session = Depends(get_db)):
    """获取所有产品参数配置"""
    return ProductParametersOut(
        base_rates=db.query(BaseRate).all(),
        sla_configs=db.query(SLAConfig).all(),
        hardware_depreciations=db.query(HardwareDepreciation).all(),
        regional_adjustments=db.query(RegionalAdjustment).all()
    )


# ============ 初始化默认数据 ============
@router.post("/init_defaults")
def init_default_data(db: Session = Depends(get_db)):
    """初始化默认的产品参数数据"""
    # 检查是否已有数据
    if db.query(BaseRate).count() > 0:
        raise HTTPException(status_code=400, detail="数据已存在，无需初始化")

    # 初始化基础费率
    base_rates = [
        BaseRate(level_code='gold', level_name='金牌服务 (Gold)', level_desc='7x24小时 + 4小时到场',
                 rate_value=0.185, trend_value=0.012),
        BaseRate(level_code='silver', level_name='银牌服务 (Silver)', level_desc='5x8小时 + 下一工作日',
                 rate_value=0.12, trend_value=0),
        BaseRate(level_code='bronze', level_name='铜牌服务 (Bronze)', level_desc='远程支持 / 仅备件',
                 rate_value=0.085, trend_value=-0.005),
    ]
    db.add_all(base_rates)

    # 初始化SLA配置 (调节系数配置)
    sla_configs = [
        SLAConfig(coefficient_name='高风险', description='高风险环境作业的加价系数', coefficient=1.5),
        SLAConfig(coefficient_name='特殊时段', description='非工作时间、节假日等特殊时段的加价系数', coefficient=1.3),
        SLAConfig(coefficient_name='紧急程度', description='紧急需求的加价系数', coefficient=1.8),
    ]
    db.add_all(sla_configs)

    # 初始化硬件折旧
    hardware_deps = [
        HardwareDepreciation(device_type='服务器', rate_value=0.025),
        HardwareDepreciation(device_type='存储设备', rate_value=0.04),
        HardwareDepreciation(device_type='网络设备', rate_value=0.018),
    ]
    db.add_all(hardware_deps)

    # 初始化区域调节
    regional_adjustments = [
        RegionalAdjustment(region_code='CN', region_name='华东区 (East China)', coefficient=1.0),
        RegionalAdjustment(region_code='HK', region_name='港澳台 (HK/MO/TW)', coefficient=1.5),
        RegionalAdjustment(region_code='SG', region_name='亚太其他 (APAC Other)', coefficient=1.8),
    ]
    db.add_all(regional_adjustments)

    db.commit()
    return {"message": "默认数据初始化成功"}
