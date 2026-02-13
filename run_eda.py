
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import koreanize_matplotlib
from wordcloud import WordCloud
from loguru import logger
import os

# Create data directory if it doesn't exist
if not os.path.exists('yes24/data'):
    os.makedirs('yes24/data')

# 데이터 로드
file_path = 'yes24/data/yes24_ai.csv'
try:
    df = pd.read_csv(file_path)
    logger.info("Data loaded successfully")
except FileNotFoundError:
    logger.error(f"File not found: {file_path}")
    exit()

# 데이터 기본 정보 확인
logger.info("DataFrame shape: {}", df.shape)
logger.info("DataFrame columns: {}", df.columns.tolist())

# 결측치 확인
logger.info("Missing values per column:
{}", df.isnull().sum())

# 데이터 미리보기
print("### Data Preview (Top 5)")
print(df.head())

# 데이터프레임 정보
print("
### DataFrame Info")
df.info()

# 기본 통계 정보
print("
### Basic Statistics")
print(df.describe())

# 3.1. 출판사별 도서 수
plt.figure(figsize=(12, 8))
publisher_counts = df['publisher'].value_counts().sort_values(ascending=False)
sns.barplot(x=publisher_counts.values, y=publisher_counts.index, palette='viridis')
plt.title('Number of Books per Publisher')
plt.xlabel('Number of Books')
plt.ylabel('Publisher')
plt.tight_layout()
plt.savefig('yes24/data/publisher_counts.png')
logger.info("Saved publisher_counts.png")

# 3.2. 가격 분포
plt.figure(figsize=(12, 6))
plt.subplot(1, 2, 1)
sns.histplot(df['original_price'], bins=20, kde=True)
plt.title('Original Price Distribution')
plt.xlabel('Original Price')
plt.ylabel('Frequency')
plt.subplot(1, 2, 2)
sns.histplot(df['sale_price'], bins=20, kde=True, color='orange')
plt.title('Sale Price Distribution')
plt.xlabel('Sale Price')
plt.ylabel('Frequency')
plt.tight_layout()
plt.savefig('yes24/data/price_distribution.png')
logger.info("Saved price_distribution.png")

# 3.3. 평점과 리뷰 수의 관계
plt.figure(figsize=(10, 6))
sns.scatterplot(data=df, x='rating', y='review_count', hue='publisher', size='sale_index', sizes=(20, 200))
plt.title('Rating vs. Review Count')
plt.xlabel('Rating')
plt.ylabel('Review Count')
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.savefig('yes24/data/rating_review_relation.png')
logger.info("Saved rating_review_relation.png")

# 3.4. 도서 제목 워드클라우드
text = ' '.join(df['title'].dropna())
wordcloud = WordCloud(
    font_path='malgun',
    width=800,
    height=400,
    background_color='white'
).generate(text)
plt.figure(figsize=(15, 7))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')
plt.title('Book Title Word Cloud')
plt.savefig('yes24/data/title_wordcloud.png')
logger.info("Saved title_wordcloud.png")


# 3.5. 상관관계 히트맵
numeric_df = df[['original_price', 'sale_price', 'sale_index', 'review_count', 'rating']]
correlation_matrix = numeric_df.corr()
plt.figure(figsize=(10, 8))
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt='.2f', linewidths=.5)
plt.title('Correlation Heatmap')
plt.savefig('yes24/data/correlation_heatmap.png')
logger.info("Saved correlation_heatmap.png")
