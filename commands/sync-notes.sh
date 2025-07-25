#!/bin/bash

# sync-notes.sh - 同步筆記到 Obsidian 和專案記憶
# 這個腳本由斜線指令自動調用

# 設定顏色輸出
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 設定路徑
OBSIDIAN_PATH="/Users/yuwenhao/Library/Mobile Documents/iCloud~md~obsidian/Documents/Root/WenHao/Inbox/Qiuck Note"
PROJECT_MEMORY=".serena/memories/development_logs"
TECH_DECISIONS=".serena/memories/technical_decisions"

# 確保目錄存在
mkdir -p "$PROJECT_MEMORY"
mkdir -p "$TECH_DECISIONS"
mkdir -p "$OBSIDIAN_PATH"

# 函數：同步筆記到 Obsidian
sync_to_obsidian() {
    local note_file="$1"
    local obsidian_file="$2"
    
    if [ -f "$note_file" ]; then
        echo -e "${BLUE}Syncing to Obsidian: ${obsidian_file}${NC}"
        cp "$note_file" "$OBSIDIAN_PATH/$obsidian_file"
        echo -e "${GREEN}✓ Synced to Obsidian${NC}"
    fi
}

# 函數：同步筆記到專案記憶
sync_to_project_memory() {
    local note_file="$1"
    local memory_file="$2"
    local memory_type="$3"
    
    if [ -f "$note_file" ]; then
        if [ "$memory_type" == "technical" ]; then
            target_dir="$TECH_DECISIONS"
        else
            target_dir="$PROJECT_MEMORY"
        fi
        
        echo -e "${BLUE}Syncing to project memory: ${memory_file}${NC}"
        cp "$note_file" "$target_dir/$memory_file"
        echo -e "${GREEN}✓ Synced to project memory${NC}"
    fi
}

# 函數：更新索引文件
update_index() {
    local index_file=".serena/memories/development_logs/index.md"
    local new_entry="$1"
    
    # 如果索引不存在，創建它
    if [ ! -f "$index_file" ]; then
        cat > "$index_file" << EOF
# Development Logs Index

## Recent Entries
EOF
    fi
    
    # 添加新條目到索引
    echo "- $new_entry" >> "$index_file"
    echo -e "${GREEN}✓ Updated index${NC}"
}

# 主要同步邏輯
main() {
    local action="$1"
    local note_file="$2"
    local note_type="$3"
    
    case "$action" in
        "take-note-api")
            # 生成檔名
            timestamp=$(date +"%Y-%m-%d_%H-%M")
            date_only=$(date +"%Y-%m-%d")
            
            # 同步到 Obsidian
            obsidian_name="API_Development_${timestamp}.md"
            sync_to_obsidian "$note_file" "$obsidian_name"
            
            # 同步到專案記憶
            if [ "$note_type" == "technical_decision" ]; then
                memory_name="${date_only}_technical_decision.md"
                sync_to_project_memory "$note_file" "$memory_name" "technical"
            else
                memory_name="${date_only}_development_notes.md"
                sync_to_project_memory "$note_file" "$memory_name" "development"
            fi
            
            # 更新索引
            update_index "[$date_only] $note_type - [View]($memory_name)"
            ;;
            
        "organize-api-notes")
            # 組織筆記的同步邏輯
            summary_file="$note_file"
            timestamp=$(date +"%Y%m%d")
            
            # 同步總結到 Obsidian
            obsidian_name="API_Summary_${timestamp}.md"
            sync_to_obsidian "$summary_file" "$obsidian_name"
            
            # 如果是週總結，也保存到 docs/published
            if [[ "$note_type" == "weekly" ]]; then
                cp "$summary_file" "docs/published/WEEKLY_SUMMARY_${timestamp}.md"
                echo -e "${GREEN}✓ Published weekly summary${NC}"
            fi
            ;;
            
        *)
            echo -e "${YELLOW}Unknown action: $action${NC}"
            exit 1
            ;;
    esac
}

# 執行主函數
main "$@"