# 小说信息提取
python -m src.services.extraction.main  data/raw --processes 2 --output data/output

# 角色卡提取
## 指定输出目录
python -m src.services.character_card.main "第一章" --output custom_output

## 批量处理目录(处理目录需要加上--batch参数)
python -m src.services.character_card.main data/raw --batch