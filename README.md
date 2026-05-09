# 材料合成方案李克特评分系统

基于小米mimo-v2.5-pro API的材料合成方案深度化学推理评分工具。

## 📋 项目简介

对A-F六组共60个材料合成方案进行严格的李克特量表评分（v1版本，6维度加权），使用大语言模型进行深度化学推理分析。

### 评分维度
- **D1 (25%)**: 设计到合成的转化准确性
- **D2 (25%)**: 反应和工艺参数可行性  
- **D3 (20%)**: 结构控制和质量控制完整性
- **D4 (10%)**: 批次稳定性和实验可重复性
- **D5 (10%)**: 路线简洁性和方法适当性
- **D6 (10%)**: 安全性、试剂可获得性和风险缓解

## 🚀 快速开始

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 配置API密钥
```bash
# Windows PowerShell
$env:MIMO_API_KEY="your-api-key-here"

# Linux/Mac
export MIMO_API_KEY="your-api-key-here"
```

### 3. 测试连接
```bash
python scripts/test_api.py
```

### 4. 解析原始MD文件（如未执行）
```bash
python scripts/parse_schemes.py
```

### 5. 开始批量评分
```bash
python scripts/api_scoring.py
```

### 6. 生成最终输出
```bash
python scripts/generate_output.py
```

## 📁 项目结构

```
scoring_project/
├── README.md                      # 本文件
├── requirements.txt               # Python依赖
├── .gitignore                     # Git忽略规则
│
├── 01_task_queue.json            # 任务队列（60个任务）
├── 02_scoring_framework.md       # 评分框架和推理指南
│
├── 03_schemes_data/              # 解析后的方案数据 [git忽略]
│   └── {A-F}_schemes.json
│
├── 04_scoring_results/           # 评分结果 [git忽略]
│   └── {A-F}_group/
│       └── XX-XX.json
│
├── 05_final_output/              # 最终输出 [git忽略]
│   ├── detailed_scores.xlsx
│   └── scoring_reasons.md
│
└── scripts/
    ├── parse_schemes.py          # MD文件解析
    ├── test_api.py               # API连接测试
    ├── api_scoring.py            # 批量评分主脚本
    └── generate_output.py        # 生成Excel和Markdown
```

## 🔧 配置说明

### API配置
- **API地址**: `https://token-plan-ams.xiaomimimo.com/v1`
- **模型**: `mimo-v2.5-pro`
- **环境变量**: `MIMO_API_KEY`

### 评分参数
- **Temperature**: 0.3（确保输出稳定）
- **Max tokens**: 2000
- **重试次数**: 3次
- **调用间隔**: 2秒（避免限流）

## 📊 数据流

```
原始MD文件 → parse_schemes.py → 03_schemes_data/
                                    ↓
                    api_scoring.py + mimo API → 04_scoring_results/
                                                    ↓
                                generate_output.py → 05_final_output/
```

## ⚙️ 脚本说明

### parse_schemes.py
从原始MD文件（A-F.md）中提取JSON方案数据。
- 自动修复JSON括号不平衡问题
- 输出到 `03_schemes_data/`

### test_api.py
测试mimo API连接和认证。

### api_scoring.py
核心评分脚本：
- 读取任务队列和方案数据
- 构建详细的化学推理prompt
- 调用API进行深度分析
- 保存评分结果并更新任务队列
- 自动容错和重试

### generate_output.py
汇总所有评分结果，生成：
- `detailed_scores.xlsx`: Excel评分表（7个sheet）
- `scoring_reasons.md`: Markdown详细理由

## 🔍 监控进度

查看已完成任务数量：
```bash
# PowerShell
$json = Get-Content 01_task_queue.json | ConvertFrom-Json
($json.task_queue | Where-Object { $_.status -eq 'completed' }).Count

# Linux/Mac
python -c "import json; data=json.load(open('01_task_queue.json')); print(len([t for t in data['task_queue'] if t['status']=='completed']))"
```

## ⚠️ 注意事项

1. **API密钥安全**: 不要提交到版本控制
2. **限流保护**: 脚本已内置2秒间隔
3. **中断恢复**: 任务队列自动保存，可中断后继续
4. **数据文件**: `03_schemes_data/` 和 `04_scoring_results/` 已加入 `.gitignore`，可从原始文件重新生成

## 📝 评分数据格式

### 方案数据 (03_schemes_data/*.json)
```json
[
  {
    "run_id": "RUN_20260428_210444_b49955",
    "proposal": {
      "steps": [...],
      "raw_materials": [...],
      "key_parameters": {...},
      "rationale": "..."
    }
  }
]
```

### 评分结果 (04_scoring_results/{group}/XX-XX.json)
```json
{
  "scheme_id": "D-01",
  "scores": {"D1": 9, "D2": 9, "D3": 8, "D4": 9, "D5": 8, "D6": 9},
  "weighted_total": 87.0,
  "grade": "A",
  "reasons": {
    "D1": "具体化学推理理由...",
    ...
  },
  "calculation": "25×0.9 + 25×0.9 + ... = 87.0"
}
```

## 🛠️ 故障排除

### API调用失败
- 检查API密钥是否正确
- 检查网络连接
- 查看API配额

### JSON解析错误
- 脚本会自动重试3次
- 检查原始MD文件格式

### 评分结果异常
- 查看 `reasons` 字段确保是具体化学推理
- 检查 `calculation` 字段验证计算正确性

## 📄 License

MIT License

## 👤 Author

YaoPan-NJU
