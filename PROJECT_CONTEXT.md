# 项目上下文 - SGA材料合成方案评分系统

## 📋 项目概览

**项目名称**: SGA-evaluation (材料合成方案李克特评分系统)  
**仓库**: https://github.com/YaoPan-NJU/SGA-evaluation.git  
**任务**: 对A-F六组共60个材料合成方案进行深度化学推理评分

---

## 🎯 核心任务

使用小米mimo-v2.5-pro API，对60个材料合成方案进行v1李克特量表评分（6维度加权）：
- **D1 (25%)**: 设计到合成的转化准确性
- **D2 (25%)**: 反应和工艺参数可行性
- **D3 (20%)**: 结构控制和质量控制完整性
- **D4 (10%)**: 批次稳定性和实验可重复性
- **D5 (10%)**: 路线简洁性和方法适当性
- **D6 (10%)**: 安全性、试剂可获得性和风险缓解

**加权公式**: `25×(D1/10) + 25×(D2/10) + 20×(D3/10) + 10×(D4/10) + 10×(D5/10) + 10×(D6/10)`  
**等级**: A≥85, B+=75-84, B=65-74, C=55-64, D<55

---

## 📁 项目结构

```
scoring_project/
├── .env.example              # API配置模板
├── 01_task_queue.json        # 任务队列（60个任务状态）
├── 02_scoring_framework.md   # 详细评分框架和推理指南
├── 03_schemes_data/          # ✅ 已解析的60个方案JSON数据
│   ├── A_schemes.json (10个方案)
│   ├── B_schemes.json (10个方案)
│   ├── C_schemes.json (10个方案)
│   ├── D_schemes.json (10个方案)
│   ├── E_schemes.json (10个方案)
│   └── F_schemes.json (10个方案)
├── 04_scoring_results/       # 评分结果（待生成）
├── 05_final_output/          # 最终输出（待生成）
└── scripts/
    ├── parse_schemes.py      # MD文件解析（已完成）
    ├── test_api.py           # API连接测试
    ├── api_scoring.py        # ⭐ 核心：批量评分脚本
    └── generate_output.py    # 生成Excel和Markdown
```

---

## ✅ 已完成工作

1. **项目搭建** ✅
   - 完整的项目结构和文档
   - Git仓库已推送到GitHub
   - .env配置支持

2. **数据解析** ✅
   - 60个方案已从MD文件解析为JSON
   - 保存在`03_schemes_data/`目录
   - 已修复JSON括号不平衡问题

3. **脚本开发** ✅
   - `api_scoring.py`: 核心评分脚本（带详细化学推理prompt）
   - 自动容错、重试机制（3次）
   - API限流保护（2秒间隔）
   - 任务队列自动保存

4. **代码优化** ✅
   - API返回数据验证
   - weighted_total计算校验
   - 详细异常追踪
   - .gitignore配置

---

## 🔄 待执行任务

### 立即执行：批量评分（58个方案）

**状态**: D-01、D-02已完成（示范），剩余58个待评分

**执行步骤**:
```bash
# 1. 配置API密钥
cp .env.example .env
nano .env  # 填入MIMO_API_KEY

# 2. 安装依赖
pip install -r requirements.txt

# 3. 测试API连接
python scripts/test_api.py

# 4. 开始批量评分（约30-40分钟）
python scripts/api_scoring.py

# 5. 生成最终输出
python scripts/generate_output.py
```

**输出**:
- `04_scoring_results/{A-F}_group/XX-XX.json` - 每个方案的详细评分
- `05_final_output/detailed_scores.xlsx` - Excel评分表（7个sheet）
- `05_final_output/scoring_reasons.md` - Markdown评分理由

---

## 🔧 关键配置

### API配置
- **API地址**: `https://token-plan-ams.xiaomimimo.com/v1`
- **模型**: `mimo-v2.5-pro`
- **环境变量**: `MIMO_API_KEY`
- **Temperature**: 0.3
- **Max tokens**: 2000

### 任务队列
- 文件: `01_task_queue.json`
- 格式: `{"id": "D-03", "group": "D", "index": 3, "status": "pending", "run_id": "..."}`
- 状态: `pending` / `completed` / `failed`

---

## 📊 评分数据格式

### 输入（03_schemes_data/*.json）
```json
[
  {
    "run_id": "RUN_20260428_210444_b49955",
    "proposal": {
      "steps": [{"step": 1, "description": "...", "temperature": "...", "duration": "..."}],
      "raw_materials": ["材料1", "材料2"],
      "key_parameters": {"param1": "value1"},
      "rationale": "设计理由..."
    }
  }
]
```

### 输出（04_scoring_results/{group}/XX-XX.json）
```json
{
  "scheme_id": "D-01",
  "scores": {"D1": 9, "D2": 9, "D3": 8, "D4": 9, "D5": 8, "D6": 9},
  "weighted_total": 87.0,
  "grade": "A",
  "reasons": {
    "D1": "具体化学推理理由...",
    "D2": "具体化学推理理由..."
  },
  "calculation": "25×0.9 + 25×0.9 + ... = 87.0"
}
```

---

## 🎓 评分框架要点

### D1 - 设计到合成的转化准确性
- 追踪每个设计特征（载体、复合组分、官能团、形貌）的合成路径
- 评估步骤是否真正能生成目标结构

### D2 - 反应和工艺参数可行性
- 分析关键反应机理（共沉淀、酯化、季铵化等）
- 验证pH、温度、浓度合理性
- 评估副反应风险（如ECH水解）

### D3 - 结构控制和质量控制完整性
- 检查表征方法匹配度（FTIR、XRD、BET等）
- 评估验收标准定量性
- 检查中间QC检查点

### D4 - 批次稳定性和实验可重复性
- 检查试剂精确用量
- 验证关键参数明确度
- 识别关键控制点

### D5 - 路线简洁性和方法适当性
- 评估步骤数量合理性
- 检查过度复杂化
- 评估设备负担

### D6 - 安全性、试剂可获得性和风险缓解
- 识别所有风险（腐蚀、毒性、易燃等）
- 评估缓解措施充分性
- 检查废物处理方案

**详细指南**: 见 `02_scoring_framework.md`

---

## ⚠️ 重要注意事项

1. **质量要求**：
   - ✅ 每个理由必须引用具体步骤编号和参数
   - ✅ 每个理由必须说明化学原理
   - ❌ 禁止使用"反应化学成熟"等通用套话
   - ❌ 禁止基于简单规则匹配

2. **API限流**：
   - 脚本已内置2秒间隔
   - 不要修改此设置

3. **中断恢复**：
   - 任务队列自动保存
   - 重新运行会从上次中断处继续

4. **数据文件**：
   - `03_schemes_data/`已提交到Git（临时）
   - `04_scoring_results/`在.gitignore中
   - 后续可从Git移除`03_schemes_data/`

---

## 🚀 快速启动命令

```bash
# 克隆项目
git clone https://github.com/YaoPan-NJU/SGA-evaluation.git
cd SGA-evaluation

# 配置
cp .env.example .env
nano .env  # 填入API密钥

# 安装
pip install -r requirements.txt

# 测试
python scripts/test_api.py

# 执行评分
python scripts/api_scoring.py

# 生成输出
python scripts/generate_output.py
```

---

## 📈 进度监控

```bash
# 查看已完成数量
python -c "import json; data=json.load(open('01_task_queue.json')); print(f'已完成: {len([t for t in data[\"task_queue\"] if t[\"status\"]==\"completed\"])}/60')"
```

---

## 📞 后续任务

完成评分后：
1. 审核评分质量（抽查reasons字段）
2. 检查分数分布合理性
3. 生成最终报告
4. 可选：从Git移除`03_schemes_data/`
5. 可选：提交`04_scoring_results/`和`05_final_output/`

---

**最后更新**: 2026-05-09  
**Git Commit**: 3ea3ef5  
**状态**: 准备开始批量评分（58/60待评分）
