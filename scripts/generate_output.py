"""
生成最终输出 - Excel评分表和Markdown评分理由
"""
import json
import os
import pandas as pd
from datetime import datetime

def load_all_results(results_dir: str) -> dict:
    """加载所有评分结果"""
    all_results = {}
    groups = ['A', 'B', 'C', 'D', 'E', 'F']
    
    for group in groups:
        group_dir = os.path.join(results_dir, f'{group}_group')
        if not os.path.exists(group_dir):
            continue
        
        group_results = []
        for filename in sorted(os.listdir(group_dir)):
            if filename.endswith('.json'):
                filepath = os.path.join(group_dir, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    result = json.load(f)
                    group_results.append(result)
        
        if group_results:
            all_results[group] = group_results
    
    return all_results


def generate_excel(all_results: dict, output_file: str):
    """生成Excel评分表"""
    print("\n📊 生成Excel评分表...")
    
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        # 为每个组创建sheet
        for group in ['A', 'B', 'C', 'D', 'E', 'F']:
            if group not in all_results:
                continue
            
            results = all_results[group]
            
            # 构建数据表
            data = []
            for r in results:
                data.append({
                    '方案ID': r['scheme_id'],
                    'Run ID': r['run_id'],
                    'D1 (25%)': r['scores']['D1'],
                    'D2 (25%)': r['scores']['D2'],
                    'D3 (20%)': r['scores']['D3'],
                    'D4 (10%)': r['scores']['D4'],
                    'D5 (10%)': r['scores']['D5'],
                    'D6 (10%)': r['scores']['D6'],
                    '加权总分': r['weighted_total'],
                    '等级': r['grade']
                })
            
            df = pd.DataFrame(data)
            df.to_excel(writer, sheet_name=f'{group}组', index=False)
        
        # 生成汇总表
        summary_data = []
        for group in ['A', 'B', 'C', 'D', 'E', 'F']:
            if group not in all_results:
                continue
            
            results = all_results[group]
            scores = [r['weighted_total'] for r in results]
            
            summary_data.append({
                '组别': f'{group}组',
                '方案数量': len(results),
                '平均分': round(sum(scores) / len(scores), 2),
                '最高分': max(scores),
                '最低分': min(scores),
                '标准差': round(pd.Series(scores).std(), 2),
                'A级数量': len([r for r in results if r['grade'] == 'A']),
                'B+级数量': len([r for r in results if r['grade'] == 'B+']),
                'B级数量': len([r for r in results if r['grade'] == 'B']),
                'C级数量': len([r for r in results if r['grade'] == 'C']),
                'D级数量': len([r for r in results if r['grade'] == 'D'])
            })
        
        df_summary = pd.DataFrame(summary_data)
        df_summary.to_excel(writer, sheet_name='Summary', index=False)
    
    print(f"✅ Excel已生成: {output_file}")


def generate_markdown(all_results: dict, output_file: str):
    """生成Markdown评分理由"""
    print("\n📝 生成Markdown评分理由...")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# 材料合成方案深度化学推理评分报告\n\n")
        f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**评分模型**: 小米mimo-v2.5-pro API\n")
        f.write(f"**评分标准**: v1李克特量表（6维度加权）\n\n")
        
        # 按组输出
        for group in ['A', 'B', 'C', 'D', 'E', 'F']:
            if group not in all_results:
                continue
            
            results = all_results[group]
            
            f.write(f"\n## {group}组评分详情\n\n")
            
            for r in results:
                f.write(f"### {r['scheme_id']}\n\n")
                f.write(f"**Run ID**: {r['run_id']}\n")
                f.write(f"**加权总分**: {r['weighted_total']} | **等级**: {r['grade']}\n\n")
                f.write(f"**计算公式**: {r.get('calculation', 'N/A')}\n\n")
                
                # 各维度详细理由
                for dim in ['D1', 'D2', 'D3', 'D4', 'D5', 'D6']:
                    dim_names = {
                        'D1': '设计到合成的转化准确性',
                        'D2': '反应和工艺参数可行性',
                        'D3': '结构控制和质量控制完整性',
                        'D4': '批次稳定性和实验可重复性',
                        'D5': '路线简洁性和方法适当性',
                        'D6': '安全性、试剂可获得性和风险缓解'
                    }
                    f.write(f"**{dim} ({r['scores'][dim]}分)** - {dim_names[dim]}: {r['reasons'][dim]}\n\n")
                
                f.write("---\n\n")
    
    print(f"✅ Markdown已生成: {output_file}")


def main():
    """主函数"""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    results_dir = os.path.join(base_dir, '04_scoring_results')
    output_dir = os.path.join(base_dir, '05_final_output')
    
    os.makedirs(output_dir, exist_ok=True)
    
    # 加载所有结果
    print("📂 加载评分结果...")
    all_results = load_all_results(results_dir)
    
    total_schemes = sum(len(results) for results in all_results.values())
    print(f"✅ 已加载 {total_schemes} 个方案的评分结果")
    
    if total_schemes == 0:
        print("❌ 没有找到评分结果，请先运行api_scoring.py")
        return
    
    # 生成Excel
    excel_file = os.path.join(output_dir, 'detailed_scores.xlsx')
    generate_excel(all_results, excel_file)
    
    # 生成Markdown
    markdown_file = os.path.join(output_dir, 'scoring_reasons.md')
    generate_markdown(all_results, markdown_file)
    
    print(f"\n✅ 所有输出已生成到: {output_dir}")
    print(f"   - detailed_scores.xlsx")
    print(f"   - scoring_reasons.md")


if __name__ == '__main__':
    main()
