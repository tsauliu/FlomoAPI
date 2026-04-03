# FlomoAPI

## Project Overview
Weekly automated Flomo note export via Playwright + cron (`30 1 * * 5`).

## Tech Stack
- Python + Playwright + playwright-stealth
- uv for dependency management
- Runs headless in WSL, downloads to `/mnt/c/Users/leo/Dropbox/MyServerFiles/Flomo`

## Debugging Flomo Selector Breakage

Flomo frequently changes its frontend UI, causing export selectors to break. When the cron job fails (check `export.log`), use `agent-browser` to inspect the current page structure:

1. Set Chrome User-Agent header first (Flomo returns 403 to default Playwright UA):
   ```
   agent-browser set headers '{"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ..."}'
   ```
2. Login, navigate to `/mine`, then use `agent-browser snapshot -i` and `agent-browser eval` to inspect elements.
3. Flomo uses Element UI (`el-popover`, `el-message-box`, etc.) — some elements live inside popovers with `display:none` and need the trigger clicked first.
4. Elements inside popovers may not respond to Playwright `.click()` — use `page.evaluate()` with `dispatchEvent(new MouseEvent('click', {bubbles: true}))` instead.

## Current Export Flow (as of 2026-04)
1. Click search input (`.search-input .el-input__inner`) to open filter popover
2. JS-dispatch click on date chip (e.g. "近 30 天") inside `.search-popover`
3. JS-dispatch click on "搜索" span inside popover
4. Click "导出" button (only visible after search results load)
5. Click confirm button (`.el-message-box__btns .el-button--primary`) and `expect_download`
