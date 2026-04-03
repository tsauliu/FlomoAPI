from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth
from dotenv import load_dotenv
import os
import sys

load_dotenv()

user = os.getenv("user")
passwd = os.getenv("passwd")
url = os.getenv("url")

# 检查是否 headless 模式
headless = "--headless" in sys.argv or os.getenv("HEADLESS") == "1"

# 下载路径 (WSL 转换 Windows 路径)
download_path = "/mnt/c/Users/leo/Dropbox/MyServerFiles/Flomo"
os.makedirs(download_path, exist_ok=True)

print(f"登录网址: {url}")
print(f"用户名: {user}")
print(f"下载路径: {download_path}")
print(f"Headless 模式: {headless}")

with Stealth().use_sync(sync_playwright()) as p:
    browser = p.chromium.launch(headless=headless)
    context = browser.new_context(accept_downloads=True)
    page = context.new_page()

    # 访问登录页面
    page.goto(url, timeout=60000)
    page.wait_for_timeout(3000)

    # 等待页面加载并查找输入框
    print("页面已加载，正在查找登录表单...")

    # 输入手机号
    phone_input = page.locator('input[placeholder="手机号 / 邮箱"], input[type="tel"], input[placeholder*="手机"]').first
    phone_input.fill(user)
    print("已输入手机号")

    # 输入密码
    password_input = page.locator('input[type="password"]').first
    password_input.fill(passwd)
    print("已输入密码")

    # 点击登录按钮
    login_button = page.locator('button:has-text("登录"), button[type="submit"]').first
    login_button.click()
    print("已点击登录按钮")

    # 等待登录结果
    page.wait_for_timeout(5000)

    # 检查是否登录成功
    current_url = page.url
    print(f"当前URL: {current_url}")

    if "login" not in current_url:
        print("登录成功！")
    else:
        print("登录可能失败，请检查页面")
        browser.close()
        exit(1)

    # 导航到主页
    print("\n导航到主页...")
    page.goto("https://v.flomoapp.com/", timeout=60000)
    page.wait_for_timeout(3000)
    print(f"当前URL: {page.url}")

    # 数据导出流程
    print("\n开始数据导出流程...")

    # 步骤1: 点击搜索框打开筛选 popover
    try:
        search_input = page.locator(".search-input .el-input__inner").first
        search_input.click()
        page.wait_for_timeout(1000)
        print("步骤 1: 已打开搜索筛选面板")
    except Exception as e:
        print(f"步骤 1: 打开筛选面板失败 - {e}")

    # 步骤2: 点击 "近 30 天" chip (通过 JS dispatch，因为在 popover 内)
    try:
        page.evaluate("""
            const chip = Array.from(document.querySelectorAll('.search-popover .chip'))
                .find(c => c.textContent.trim() === '近 30 天');
            if (chip) chip.dispatchEvent(new MouseEvent('click', {bubbles: true, cancelable: true}));
        """)
        page.wait_for_timeout(1000)
        print("步骤 2: 已选择 近 30 天")
    except Exception as e:
        print(f"步骤 2: 选择日期范围失败 - {e}")

    # 步骤3: 点击搜索按钮
    try:
        page.evaluate("""
            const btn = Array.from(document.querySelectorAll('.search-popover span'))
                .find(s => s.textContent.trim() === '搜索' && s.children.length === 0);
            if (btn) btn.dispatchEvent(new MouseEvent('click', {bubbles: true, cancelable: true}));
        """)
        page.wait_for_timeout(3000)
        print("步骤 3: 已点击搜索")
    except Exception as e:
        print(f"步骤 3: 点击搜索失败 - {e}")

    # 步骤4: 点击导出按钮
    try:
        export_btn = page.locator("button:has-text('导出')").first
        export_btn.wait_for(state="visible", timeout=10000)
        export_btn.click()
        page.wait_for_timeout(2000)
        print("步骤 4: 已点击导出")
    except Exception as e:
        print(f"步骤 4: 点击导出失败 - {e}")

    # 步骤5: 点击确定按钮并处理下载
    try:
        confirm_btn = page.locator(".el-message-box__btns .el-button--primary").first
        confirm_btn.wait_for(state="visible", timeout=10000)

        # 等待下载
        with page.expect_download(timeout=60000) as download_info:
            confirm_btn.click()
            print("步骤 5: 已点击确定，等待下载...")

        download = download_info.value
        save_path = os.path.join(download_path, download.suggested_filename)
        download.save_as(save_path)
        print(f"文件已保存到: {save_path}")
    except Exception as e:
        print(f"步骤 5: 下载失败 - {e}")

    print("\n数据导出流程完成！")

    # 保持浏览器打开一段时间以便查看结果
    page.wait_for_timeout(10000)
    browser.close()
