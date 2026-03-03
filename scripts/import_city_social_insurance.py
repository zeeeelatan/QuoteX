#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
导入城市社保公积金数据到数据库
从 Excel 文件读取城市社保公积金数据（通过环境变量 IMPORT_EXCEL_FILE 指定路径）
"""
import sys
import os

# 添加后端目录到路径
backend_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'backend')
sys.path.insert(0, backend_path)

import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import engine, SessionLocal
from app.models.city_social_insurance import CitySocialInsurance

def import_data():
    """导入城市社保基准数据"""
    excel_path = os.getenv("IMPORT_EXCEL_FILE", "./data/社保公积金测算.xlsx")
    
    print(f"正在读取Excel文件: {excel_path}")
    
    # 读取Excel，跳过表头行
    df = pd.read_excel(excel_path, header=None)
    
    # 数据从第4行开始（索引3）
    data_rows = []
    
    # Excel列映射（基于分析结果）
    # 列0: 城市
    # 列4: 社保基数上限
    # 列5: 社保基数下限
    # 列6: 计算基数
    # 列7: 工伤扣款基数
    # 列8: 公司养老比例
    # 列10: 公司医疗比例
    # 列12: 公司工伤比例
    # 列14: 公司生育比例
    # 列16: 公司失业比例
    # 列18: 公司残保金比例
    # 列22: 公司公积金比例
    # 列25: 个人养老比例
    # 列27: 个人医疗比例
    # 列29: 个人工伤比例
    # 列31: 个人生育比例
    # 列33: 个人失业比例
    # 列37: 个人公积金比例
    
    for idx in range(3, len(df)):
        row = df.iloc[idx]
        city = row[0]
        
        # 跳过空行或非城市行
        if pd.isna(city) or city == '':
            continue
            
        # 跳过合计行
        if '合计' in str(city) or '总计' in str(city):
            continue
        
        def safe_float(val):
            """安全转换为浮点数"""
            if pd.isna(val):
                return None
            try:
                return float(val)
            except:
                return None
        
        def safe_int(val):
            """安全转换为整数"""
            if pd.isna(val):
                return None
            try:
                return int(float(val))
            except:
                return None
        
        record = {
            'province': '默认',  # 暂时设为默认，Excel中无省份信息
            'city': str(city),
            'city_alias': str(city) if '（' in str(city) or '(' in str(city) else None,
            'upper_limit': safe_int(row[4]),
            'lower_limit': safe_int(row[5]),
            'calc_base': safe_int(row[6]),
            'injury_base': safe_int(row[7]),
            'corp_pension_rate': safe_float(row[8]),
            'corp_medical_rate': safe_float(row[10]),
            'corp_injury_rate': safe_float(row[12]),
            'corp_maternity_rate': safe_float(row[14]),
            'corp_unemployment_rate': safe_float(row[16]),
            'corp_disability_rate': safe_float(row[18]),  # 残保金
            'corp_fund_rate': safe_float(row[22]),
            'indiv_pension_rate': safe_float(row[25]),
            'indiv_medical_rate': safe_float(row[27]),
            'indiv_injury_rate': safe_float(row[29]),
            'indiv_maternity_rate': safe_float(row[31]),
            'indiv_unemployment_rate': safe_float(row[33]),
            'indiv_fund_rate': safe_float(row[37]),
            'is_active': True
        }
        
        # 验证必要字段
        if record['upper_limit'] is None or record['lower_limit'] is None:
            print(f"  跳过无效数据: {city}")
            continue
            
        data_rows.append(record)
        print(f"  解析: {city} - 上限:{record['upper_limit']}, 下限:{record['lower_limit']}, 残保金:{record['corp_disability_rate']}")
    
    print(f"\n共解析 {len(data_rows)} 条有效数据")
    
    # 写入数据库
    db = SessionLocal()
    try:
        updated_count = 0
        created_count = 0
        
        for record in data_rows:
            # 查找是否已存在相同城市的记录
            existing = db.query(CitySocialInsurance).filter(
                CitySocialInsurance.city == record['city']
            ).first()
            
            if existing:
                # 更新现有记录
                for key, value in record.items():
                    if key != 'id' and value is not None:
                        setattr(existing, key, value)
                updated_count += 1
                print(f"  更新: {record['city']}")
            else:
                # 创建新记录
                new_record = CitySocialInsurance(**record)
                db.add(new_record)
                created_count += 1
                print(f"  新增: {record['city']}")
        
        db.commit()
        print(f"\n导入完成: 新增 {created_count} 条, 更新 {updated_count} 条")
        
    except Exception as e:
        db.rollback()
        print(f"导入失败: {e}")
        raise
    finally:
        db.close()

if __name__ == '__main__':
    import_data()
