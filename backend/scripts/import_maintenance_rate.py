import pandas as pd
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from backend.models.maintenance_rate import MaintenanceRate
from database import Base

# 配置数据库连接
engine = create_engine('postgresql://youruser:yourpwd@localhost:5432/yourdb')
Session = sessionmaker(bind=engine)
session = Session()

def parse_rate(val):
    if pd.isnull(val):
        raise ValueError('维保费率(%)不能为空')
    if isinstance(val, str):
        val = val.strip()
        if '%' in val or not val.replace('.', '', 1).isdigit():
            raise ValueError(f'维保费率(%)只能填写数字，不能包含%号，错误值：{val}')
    try:
        rate = float(val)
        return rate / 100
    except Exception:
        raise ValueError(f'维保费率(%)格式错误，错误值：{val}')

# 读取Excel
file_path = 'backend/费率.xlsx'
df = pd.read_excel(file_path)
# 兼容不同表头
if '设备类型' in df.columns:
    df[['primary_category', 'secondary_category', 'tertiary_category']] = df['设备类型'].str.split('-', expand=True)
if '一级分类' in df.columns:
    df['primary_category'] = df['一级分类']
if '二级分类' in df.columns:
    df['secondary_category'] = df['二级分类']
if '三级分类' in df.columns:
    df['tertiary_category'] = df['三级分类']
rate_col = '维保费率(%)'
df['rate'] = df[rate_col].apply(parse_rate)

for _, row in df.iterrows():
    # 查找是否已存在
    obj = session.query(MaintenanceRate).filter_by(
        primary_category=row['primary_category'],
        secondary_category=row['secondary_category'],
        tertiary_category=row['tertiary_category']
    ).first()
    if obj:
        obj.rate = row['rate']
        obj.remark = row.get('备注', '')
    else:
        obj = MaintenanceRate(
            primary_category=row['primary_category'],
            secondary_category=row['secondary_category'],
            tertiary_category=row['tertiary_category'],
            rate=row['rate'],
            remark=row.get('备注', '')
        )
        session.add(obj)
session.commit()
session.close()
print('导入完成') 