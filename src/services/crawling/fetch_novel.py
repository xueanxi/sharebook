from playwright.sync_api import sync_playwright
import time
import os

save_novel_dir = 'data_crawl_novel'

def get_clipboard_after_click(url=None, max_chapters=50):
    """
    爬取小说内容
    
    Args:
        url: 小说页面URL，如果为None则使用默认URL
        max_chapters: 最大爬取章节数
    """
    # 确保输出目录存在
    os.makedirs(save_novel_dir, exist_ok=True)
    
    # 如果没有提供URL，使用默认URL
    if url is None:
        url = "https://promoter.fanqieopen.com/page/share/content/book-detail?token=ae36ee8729e25d4d92a7ddf0bd75d71d&tab_type=2&key=6&top_tab_genre=-1&book_id=7270734352873425961&genre=0&item_id=7272809347439135744"
    
    with sync_playwright() as p:
        # 启动浏览器（调试时用 headless=False 可见操作过程）
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        # 1. 访问目标页面
        page.goto(url)
        page.wait_for_load_state("networkidle")  # 等待页面加载稳定
        
        # 2. 定位并点击复制按钮（替换成你的按钮选择器）
        catalogue_panel = page.locator(".catalogue__list-sbGYR4")
        if catalogue_panel and catalogue_panel.is_visible():
            print('找到了目录')
            # 遍历catalogue_panel的子元素
            catalogue_panel.hover()
            page.wait_for_timeout(500)
            page.mouse.wheel(0, 1)
            page.wait_for_timeout(500)
            test_time = 0
            for item in catalogue_panel.locator("div.catalogue__item-ImEeJx").all()[:max_chapters]:
                if item.is_visible():
                    chapter_title = item.inner_text().strip()
                    if not item.is_visible():
                            print(f"章节《{chapter_title}》向下滚动10个像素")
                            page.mouse.wheel(0, 3)
                            page.wait_for_timeout(500)  # 等待滚动完成
                    item.hover()  # 鼠标移动到按钮上
                    page.wait_for_timeout(500)  # 等待滚动完成
                    item.click()  # 然后点击
                    page.wait_for_timeout(2000)
                    page.mouse.wheel(0, 3)
                    page.wait_for_timeout(500)  # 等待滚动完成
                    
                    content = get_content_and_save(page,chapter_title)
                    while not content and test_time < 3:
                        test_time += 1
                        print(f"尝试获取内容第{test_time}次")
                        page.mouse.wheel(0, 3)
                        page.wait_for_timeout(500)  # 等待滚动完成
                        content = get_content_and_save(page,chapter_title)
                        

            time.sleep(1)  # 关键：等待 1 秒，确保内容写入剪贴板（根据页面速度调整）
        else:
            print("未找到复制按钮")
            browser.close()
            return
        browser.close()

def get_content_and_save(page,title):
    contet = page.locator("div[class^='sider-right-wrap']")
    if contet.is_visible():
        content = contet.inner_text()
        print(f"获取到内容：\n{content[:20]}...")  # 打印前100字
        # 去除title中的空格
        clean_title = title.replace(" ", "")
        # 保存内容到本地
        with open(f"{save_novel_dir}/{clean_title}.txt", "w", encoding="utf-8") as f:
            f.write(content)
        print(f"内容已保存到 {save_novel_dir}/{clean_title}.txt")
        return content
    else:
        print("未找到内容")
        return None

if __name__ == "__main__":
    get_clipboard_after_click()