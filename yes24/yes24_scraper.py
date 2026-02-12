
import requests
from bs4 import BeautifulSoup
import pandas as pd
from loguru import logger
import koreanize_matplotlib
import os
import re

# 로거 설정
logger.add("yes24_scraper.log", rotation="500 MB")

def get_book_info(disp_no, page=1, size=24):
    """
    Yes24에서 특정 카테고리의 도서 정보를 가져옵니다.
    """
    url = "https://www.yes24.com/product/category/CategoryProductContents"
    headers = {
        'host': 'www.yes24.com',
        'referer': f'https://www.yes24.com/product/category/display/{disp_no}',
        'sec-ch-ua': '"Not(A:Brand";v="8", "Chromium";v="144", "Google Chrome";v="144"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest'
    }
    params = {
        'dispNo': disp_no,
        'order': 'SINDEX_ONLY',
        'addOptionTp': '0',
        'page': page,
        'size': size,
        'statGbYn': 'N',
        'viewMode': '',
        '_options': '',
        'directDelvYn': '',
        'usedTp': '0',
        'elemNo': '0',
        'elemSeq': '0',
        'seriesNumber': '0'
    }

    try:
        logger.info(f"페이지 {page}에서 데이터 수집 시작...")
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()  # HTTP 오류 발생 시 예외 발생
        logger.info(f"페이지 {page}에서 데이터 수집 완료 (상태 코드: {response.status_code})")
        return response.text
    except requests.exceptions.RequestException as e:
        logger.error(f"페이지 {page}에서 데이터를 가져오는 중 오류 발생: {e}")
        return None

def parse_book_data(html):
    """
    HTML 응답을 파싱하여 도서 데이터를 추출합니다.
    """
    soup = BeautifulSoup(html, 'html.parser')
    book_items = soup.find_all('div', class_='itemUnit')
    
    books_data = []
    if not book_items:
        logger.warning("파싱할 도서 아이템이 없습니다.")
        return books_data

    for item in book_items:
        # 가격 정보 추출 및 숫자로 변환
        original_price_tag = item.select_one('.info_price .txt_num.dash em')
        original_price = int(original_price_tag.text.replace(',', '')) if original_price_tag else 0

        sale_price_tag = item.select_one('.info_price .yes_b')
        sale_price = int(sale_price_tag.text.replace(',', '')) if sale_price_tag else 0

        # 판매지수 추출 및 숫자로 변환
        sale_num_tag = item.select_one('.saleNum')
        sale_index = 0
        if sale_num_tag:
            match = re.search(r'[\d,]+', sale_num_tag.text)
            if match:
                sale_index = int(match.group().replace(',', ''))

        # 리뷰 수 추출
        review_count_tag = item.select_one('.rating_rvCount .txC_blue')
        review_count = int(re.search(r'\d+', review_count_tag.text).group()) if review_count_tag else 0
        
        # 저자 정보 클리닝
        author_tag = item.select_one('.info_auth')
        author = author_tag.text.strip().replace(' 저', '') if author_tag else 'N/A'


        book_info = {
            'title': item.select_one('.gd_name').text.strip() if item.select_one('.gd_name') else 'N/A',
            'author': author,
            'publisher': item.select_one('.info_pub').text.strip() if item.select_one('.info_pub') else 'N/A',
            'publication_date': item.select_one('.info_date').text.strip() if item.select_one('.info_date') else 'N/A',
            'original_price': original_price,
            'sale_price': sale_price,
            'sale_index': sale_index,
            'review_count': review_count,
            'rating': float(item.select_one('.rating_grade .yes_b').text) if item.select_one('.rating_grade .yes_b') else 0.0,
            'image_url': item.select_one('.lazy')['data-original'] if item.select_one('.lazy') else 'N/A',
            'book_url': 'https://www.yes24.com' + item.select_one('.gd_name')['href'] if item.select_one('.gd_name') else 'N/A'
        }
        books_data.append(book_info)
    
    logger.info(f"{len(books_data)}개의 도서 정보를 파싱했습니다.")
    return books_data

def main():
    """
    메인 실행 함수
    """
    disp_no = '001001003032'  # IT 모바일
    total_pages = 5  # 수집할 총 페이지 수 (필요에 따라 조절)
    all_books = []

    for page in range(1, total_pages + 1):
        html_content = get_book_info(disp_no, page=page)
        if html_content:
            books_on_page = parse_book_data(html_content)
            if not books_on_page:
                logger.warning(f"{page} 페이지에서 더 이상 수집할 도서가 없습니다. 수집을 중단합니다.")
                break
            all_books.extend(books_on_page)
        else:
            logger.error(f"{page} 페이지의 콘텐츠를 가져오지 못했습니다.")

    if not all_books:
        logger.error("수집된 도서 정보가 없습니다. 스크립트를 종료합니다.")
        return

    # 데이터프레임 생성 및 CSV 파일로 저장
    df = pd.DataFrame(all_books)
    
    # 데이터 저장 경로 설정
    output_dir = 'yes24/data'
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'yes24_ai.csv')

    df.to_csv(output_path, index=False, encoding='utf-8-sig')
    logger.info(f"총 {len(all_books)}개의 도서 정보를 '{output_path}' 파일에 저장했습니다.")
    print(f"데이터 수집 완료! 총 {len(all_books)}개의 도서 정보를 '{output_path}'에 저장했습니다.")
    print(df.head())


if __name__ == '__main__':
    main()
