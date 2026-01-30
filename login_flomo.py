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

    steps = [
        ("svg.filter-icon", "筛选图标"),
        ("input[placeholder='结束日期']", "结束日期输入框"),
        ("button:has-text('最近一个月')", "最近一个月按钮"),
        ("span:has-text('搜索')", "搜索按钮"),
        ("button:has-text('导出')", "导出按钮"),
    ]

    for i, (selector, desc) in enumerate(steps, 1):
        try:
            page.wait_for_timeout(2000)
            element = page.locator(selector).first
            element.wait_for(state="visible", timeout=10000)
            element.click()
            print(f"步骤 {i}: 已点击 {desc}")
        except Exception as e:
            print(f"步骤 {i}: 点击 {desc} 失败 - {e}")

    # 步骤6: 点击确定按钮并处理下载
    try:
        page.wait_for_timeout(2000)
        confirm_btn = page.locator("button:has-text('确定')").first
        confirm_btn.wait_for(state="visible", timeout=10000)

        # 等待下载
        with page.expect_download() as download_info:
            confirm_btn.click()
            print("步骤 6: 已点击 确定按钮")

        download = download_info.value
        # 保存到指定路径，使用原文件名（同一天会覆盖）
        save_path = os.path.join(download_path, download.suggested_filename)
        download.save_as(save_path)
        print(f"文件已保存到: {save_path}")
    except Exception as e:
        print(f"步骤 6: 下载失败 - {e}")

    print("\n数据导出流程完成！")

    # 保持浏览器打开一段时间以便查看结果
    page.wait_for_timeout(10000)
    browser.close()
