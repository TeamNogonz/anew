from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time
from datetime import datetime
from config import settings

mediaIdList = {
    "009": "매일경제",
    "015": "한국경제",
    "011": "서울경제",
    "008": "머니투데이",
    "018": "이데일리",
    "648": "비즈워치"
}

# 언론사별 최대 뉴스 개수는 config.py에서 설정

def getNewsUrlByMediaId(driver, mediaId):
    urls = []
    today_str = datetime.today().strftime("%Y%m%d")

    for i in range(settings.max_news_by_media):
        page = (i // 20) + 1
        page_offset = i % 20

        if page_offset == 0:
            # URL 생성 (2페이지 이상이면 date와 page 필요)
            if page == 1:
                url = f"https://news.naver.com/main/list.naver?mode=LPOD&mid=sec&oid={mediaId}"
            else:
                url = f"https://news.naver.com/main/list.naver?mode=LPOD&mid=sec&oid={mediaId}&date={today_str}&page={page}"

            driver.get(url)
            time.sleep(1)

            headline_items = driver.find_elements(By.CSS_SELECTOR, "ul.type06_headline li")
            type06_items = driver.find_elements(By.CSS_SELECTOR, "ul.type06 li")
            all_items = headline_items + type06_items  # 총 20개 기사

        try:
            item = all_items[page_offset]
            a_tag = item.find_element(By.CSS_SELECTOR, "a")
            news_url = a_tag.get_attribute("href")
            urls.append(news_url)

            if len(urls) >= settings.max_news_by_media:
                break
        except:
            continue

        if len(urls) >= settings.max_news_by_media:
            break

    return urls

def getNews(driver, news_url):
    driver.get(news_url)
    time.sleep(1)
    title = None  # 제목
    content = None  # 본문

    try:
        for sel in [".media_end_head_headline", "h2#title", ".end_tit", ".ArticleHead_article_title__qh8GV"]:
            try:
                elem = driver.find_element(By.CSS_SELECTOR, sel)
                title = elem.text.strip()
                if title:
                    break
            except:
                continue

        for sel in ["#newsct_article", ".article_body", "#articleBody", "._article_content", ".newsct_article _article_body"]:
            try:
                elem = driver.find_element(By.CSS_SELECTOR, sel)
                content = elem.text.strip()
                if content:
                    break
            except:
                continue

        return {
            "title": title,
            "content": content
        }
    except:
        return None