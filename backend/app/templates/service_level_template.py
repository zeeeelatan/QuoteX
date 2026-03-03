import pandas as pd
import os

def create_service_level_template():
    """创建服务级别导入模板"""
    # 根据用户提供的Excel模板创建示例数据
    sample_data = [
        {
            '服务级别': '基础服务',
            '响应时效': '24小时',
            '服务级别系数值': 1.0
        },
        {
            '服务级别': '标准服务',
            '响应时效': '4小时',
            '服务级别系数值': 1.2
        },
        {
            '服务级别': '快速服务',
            '响应时效': '2小时',
            '服务级别系数值': 1.5
        },
        {
            '服务级别': '紧急服务',
            '响应时效': '1小时',
            '服务级别系数值': 2.0
        }
    ]
    
    # 创建DataFrame
    df = pd.DataFrame(sample_data)
    
    # 保存为Excel文件
    template_path = "service_level_template.xlsx"
    try:
        df.to_excel(template_path, index=False, engine='openpyxl')
        print(f"服务级别模板已创建: {template_path}")
        return template_path
    except Exception as e:
        print(f"创建模板失败: {e}")
        raise e
    
if __name__ == '__main__':
    create_service_level_template() 