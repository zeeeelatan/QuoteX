#!/usr/bin/env python3
"""
备件价格管理数据导入脚本
将 Excel 文件中的备件数据导入到数据库中
"""
import os
import sys
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# 添加父目录到 path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 数据库配置
DB_NAME = os.getenv('DB_NAME', 'device_inventory_ai_quote_test')
DB_USER = os.getenv('DB_USER', 'device_inventory_user')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'dev_password_123')
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Excel 文件路径
EXCEL_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '备件价格管理.xlsx')


def import_spare_parts():
    """导入备件数据"""
    print(f"=== 备件价格管理数据导入 ===")
    print(f"数据库: {DB_NAME}@{DB_HOST}:{DB_PORT}")
    print(f"Excel文件: {EXCEL_FILE}")
    print()

    # 检查文件是否存在
    if not os.path.exists(EXCEL_FILE):
        print(f"错误: 文件不存在 - {EXCEL_FILE}")
        return False

    # 读取 Excel
    print("正在读取 Excel 文件...")
    df = pd.read_excel(EXCEL_FILE)
    print(f"读取到 {len(df)} 行数据")
    print(f"表头: {list(df.columns)}")
    print()

    # 列名映射：Excel -> 数据库
    column_mapping = {
        '序号': 'seq_no',  # 不导入，数据库自增
        '厂商': 'manufacturer',
        '备件PN': 'part_pn',
        '备件描述': 'part_desc',
        '备件分类': 'part_category',
        '备件成色': 'part_condition',
        '报修方式': 'repair_method',
        '报修期限': 'repair_period',
        '单价': 'unit_price'
    }

    # 重命名列
    df_renamed = df.rename(columns=column_mapping)

    # 删除序号列（数据库自增）
    if 'seq_no' in df_renamed.columns:
        df_renamed = df_renamed.drop(columns=['seq_no'])

    # 处理空值
    df_renamed = df_renamed.fillna({
        'manufacturer': '',
        'part_pn': '',
        'part_desc': '',
        'part_category': '',
        'part_condition': '',
        'repair_method': '',
        'repair_period': '',
        'unit_price': 0
    })

    # 确保单价是数值类型
    df_renamed['unit_price'] = pd.to_numeric(df_renamed['unit_price'], errors='coerce').fillna(0)

    # 创建数据库连接
    print("正在连接数据库...")
    engine = create_engine(DATABASE_URL)

    try:
        with engine.connect() as conn:
            # 清空现有数据
            print("正在清空现有备件数据...")
            conn.execute(text("DELETE FROM spare_part"))
            conn.execute(text("ALTER SEQUENCE spare_part_id_seq RESTART WITH 1"))
            conn.commit()
            print("现有数据已清空")

            # 导入新数据
            print(f"正在导入 {len(df_renamed)} 条备件数据...")
            df_renamed.to_sql('spare_part', engine, if_exists='append', index=False)
            
            # 验证导入结果
            result = conn.execute(text("SELECT COUNT(*) FROM spare_part"))
            count = result.scalar()
            print(f"导入完成！数据库中共有 {count} 条备件记录")

        print()
        print("=== 导入成功 ===")
        return True

    except Exception as e:
        print(f"导入失败: {e}")
        return False


if __name__ == '__main__':
    success = import_spare_parts()
    sys.exit(0 if success else 1)





