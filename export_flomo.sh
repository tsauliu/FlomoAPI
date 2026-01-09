#!/bin/bash

# Flomo 数据导出脚本
# 每周五早上8点通过 crontab 运行

SCRIPT_DIR="/home/leo/FlomoAPI"
LOG_FILE="$SCRIPT_DIR/export.log"
VENV_PATH="/home/leo/pyenv"

# 记录日志
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

log "开始 Flomo 导出任务"

# 切换到脚本目录
cd "$SCRIPT_DIR" || {
    log "错误: 无法切换到 $SCRIPT_DIR"
    exit 1
}

# 激活虚拟环境并运行脚本
source "$VENV_PATH/bin/activate"

# 使用 headless 模式运行
HEADLESS=1 python3 login_flomo.py >> "$LOG_FILE" 2>&1

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    log "导出成功完成"
else
    log "导出失败，退出码: $EXIT_CODE"
fi

deactivate

log "任务结束"
echo "" >> "$LOG_FILE"
