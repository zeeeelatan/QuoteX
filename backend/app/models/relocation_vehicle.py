"""
机房搬迁车型数据模型
对应 Excel：机房搬迁车型数据大全.xlsx
"""

from sqlalchemy import Column, Integer, String, Numeric, Text
from app.database import Base


class RelocationVehicle(Base):
    """机房搬迁车型数据表"""
    __tablename__ = "relocation_vehicle"

    id = Column(Integer, primary_key=True, index=True)
    seq_no = Column(Integer, nullable=True, comment="序号")
    vehicle_category = Column(String(50), nullable=True, comment="车型分类")
    vehicle_name = Column(String(100), nullable=True, comment="车型名称")
    length_m = Column(Numeric(8, 2), nullable=True, comment="车厢长度(m)")
    width_m = Column(Numeric(8, 2), nullable=True, comment="车厢宽度(m)")
    height_m = Column(Numeric(8, 2), nullable=True, comment="车厢高度(m)")
    volume_m3 = Column(Numeric(10, 2), nullable=True, comment="容积(m³)")
    load_ton = Column(Numeric(8, 2), nullable=True, comment="载重量(吨)")
    server_1u = Column(String(50), nullable=True, comment="可装1U服务器(台)")
    server_2u = Column(String(50), nullable=True, comment="可装2U服务器(台)")
    rack_count = Column(String(50), nullable=True, comment="可装机柜(个)")
    scenario = Column(String(200), nullable=True, comment="适用场景")
    distance_advice = Column(String(100), nullable=True, comment="运输距离建议")
    license_required = Column(String(50), nullable=True, comment="是否需特殊驾照")
    city_restrict = Column(String(100), nullable=True, comment="市区限行情况")
    basement_limit = Column(String(100), nullable=True, comment="地库限高通过")
    start_price = Column(String(100), nullable=True, comment="参考起步价(元)")
    km_price = Column(String(100), nullable=True, comment="参考公里价(元/km)")
    remark = Column(Text, nullable=True, comment="备注")
