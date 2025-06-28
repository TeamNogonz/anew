from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time
from datetime import datetime

mediaIdList = {
    "009": "매일경제",
    "015": "한국경제",
    "011": "서울경제",
    "008": "머니투데이",
    "018": "이데일리",
    "648": "비즈워치"
}

MAX_NEWS_BY_MEDIA = 2  # 언론사 별, 가져올 최대 뉴스 개수

def getNewsUrlByMediaId(driver, mediaId):
    urls = []
    today_str = datetime.today().strftime("%Y%m%d")

    for i in range(MAX_NEWS_BY_MEDIA):
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

            if len(urls) >= MAX_NEWS_BY_MEDIA:
                break
        except:
            continue

        if len(urls) >= MAX_NEWS_BY_MEDIA:
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

if __name__ == "__main__":
    start_time = time.time()
    print("Start time:", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start_time)))

    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    mediaIds = list(mediaIdList.keys())
    newsData = {mediaIdList[mediaId]: [] for mediaId in mediaIds}

    # 언론사별 실패 카운트 초기화
    fail_counts = {mediaIdList[mediaId]: 0 for mediaId in mediaIds}

    for mediaId in mediaIds:
        mediaName = mediaIdList[mediaId]
        collected = newsData[mediaName]

        need = MAX_NEWS_BY_MEDIA - len(collected)
        urls = getNewsUrlByMediaId(driver, mediaId)

        for url in urls:
            if len(collected) >= MAX_NEWS_BY_MEDIA:
                break
            if any(d['url'] == url for d in collected):
                continue

            details = getNews(driver, url)
            if details:
                collected.append({
                    "press": mediaName,
                    "url": url,
                    **details
                })
            else:
                fail_counts[mediaName] += 1
                print(f"[경고] '{mediaName}' 상세페이지 추출 실패: {url} (실패 횟수: {fail_counts[mediaName]})")
    print(newsData.items())
    # for press, news_list in newsData.items():
    #     print("f@@@@@@ ", newsData.items())
        #print(f"\n=== {press} 기사 {len(news_list)}개 ===")
        #for idx, news in enumerate(news_list, 1):
        #    print(f"[{idx}] 제목: {news['title']}")
        #    print(f"링크: {news['url']}")
        #    print(f"본문:\n{news['content']}\n{'-'*60}")

    end_time = time.time()
    print("End time:", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(end_time)))
    elapsed = end_time - start_time
    print(f"Elapsed time: {elapsed:.4f} seconds")

    driver.quit()