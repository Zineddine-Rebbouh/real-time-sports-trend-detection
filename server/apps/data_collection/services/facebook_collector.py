from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
import time
import pandas as pd
import logging
from datetime import datetime
import random

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Target hashtags and sport type mapping
TARGET_HASHTAGS = ['#كرة_القدم', '#كرة_السلة', '#تنس', '#ملاكمة', '#كرة_الطائرة']
HASHTAG_TO_SPORT = {
    '#كرة_القدم': 'football',
    '#كرة_السلة': 'basketball',
    '#تنس': 'tennis',
    '#ملاكمة': 'boxing',
    '#كرة_الطائرة': 'volleyball'
}

def init_driver():
    """Initialize Chrome WebDriver with enhanced options."""
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Run in headless mode
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-webgl')  # Disable WebGL to avoid warnings
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36')
    try:
        driver = webdriver.Chrome(service=Service(), options=options)
        return driver
    except WebDriverException as e:
        logger.error(f"Failed to initialize WebDriver: {str(e)}")
        raise

def login_facebook(driver, email, password):
    """Log into Facebook."""
    driver.get('https://www.facebook.com')
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'email')))
        driver.find_element(By.ID, 'email').send_keys(email)
        driver.find_element(By.ID, 'pass').send_keys(password)
        driver.find_element(By.NAME, 'login').click()
        WebDriverWait(driver, 15).until(EC.url_contains('facebook.com'))
        logger.info("Logged into Facebook successfully")
    except TimeoutException:
        logger.error("Facebook login failed - timeout or incorrect credentials")
        raise
    except Exception as e:
        logger.error(f"Facebook login failed: {str(e)}")
        raise

def scrape_bein_sports_comments(email, password, max_posts=10, output_csv='bein_sports_comments.csv'):
    """Scrape comments from beIN Sports Facebook page and save to CSV."""
    driver = init_driver()
    comments_data = []

    try:
        # Log in
        login_facebook(driver, email, password)

        # Navigate to beIN Sports page
        driver.get('https://www.facebook.com/beINSPORTS')
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[role="main"]')))
        logger.info("Loaded beIN Sports page")

        # Scroll to load posts
        posts_scraped = 0
        last_height = driver.execute_script("return document.body.scrollHeight")
        max_scroll_attempts = 5
        scroll_attempts = 0

        while posts_scraped < max_posts and scroll_attempts < max_scroll_attempts:
            # Find posts
            posts = driver.find_elements(By.CSS_SELECTOR, 'div[role="article"]')
            logger.info(f"Found {len(posts)} posts on current page")
            for post in posts:
                try:
                    # Get post text
                    post_text_elem = post.find_element(By.CSS_SELECTOR, 'div[dir="auto"]')
                    post_text = post_text_elem.text.lower()
                    logger.debug(f"Post text: {post_text[:100]}...")

                    # Check if post contains target hashtags
                    matched_hashtags = [h for h in TARGET_HASHTAGS if h.lower() in post_text]
                    if matched_hashtags:
                        logger.info(f"Found post with hashtags: {matched_hashtags}")
                        # Click to expand comments
                        try:
                            comment_link = post.find_element(By.XPATH, './/span[contains(text(), "تعليق") or contains(text(), "Comment")]')
                            driver.execute_script("arguments[0].click();", comment_link)
                            WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[aria-label="Comment"]')))
                        except (NoSuchElementException, TimeoutException):
                            logger.warning("Could not expand comments for post")
                            continue

                        # Load all comments with retries
                        retries = 3
                        while retries > 0:
                            try:
                                more_comments = driver.find_elements(By.XPATH, '//span[contains(text(), "View more comments") or contains(text(), "عرض المزيد من التعليقات")]')
                                if more_comments:
                                    driver.execute_script("arguments[0].click();", more_comments[0])
                                    time.sleep(random.uniform(2, 4))  # Random delay
                                else:
                                    break
                            except (NoSuchElementException, TimeoutException):
                                break
                            retries -= 1

                        # Extract comments
                        comments = driver.find_elements(By.CSS_SELECTOR, 'div[aria-label="Comment"]')
                        logger.info(f"Found {len(comments)} comments in post")
                        for comment in comments:
                            try:
                                comment_text = comment.text.strip()
                                matched_comment_hashtags = [h for h in TARGET_HASHTAGS if h.lower() in comment_text.lower()]
                                if matched_comment_hashtags:
                                    sport_type = HASHTAG_TO_SPORT.get(matched_comment_hashtags[0], 'unknown')
                                    try:
                                        date_elem = comment.find_element(By.CSS_SELECTOR, 'span[dir="auto"] a[href*="/comment"]')
                                        comment_date = date_elem.text  # May need parsing
                                    except:
                                        comment_date = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
                                    comments_data.append({
                                        'content': comment_text,
                                        'sport_type': sport_type,
                                        'created_at': comment_date,
                                        'source': 'facebook',
                                        'page': 'beINSPORTS'
                                    })
                                    logger.info(f"Collected comment: {comment_text[:50]}... (Sport: {sport_type})")
                            except Exception as e:
                                logger.warning(f"Error processing comment: {str(e)}")

                        posts_scraped += 1
                        logger.info(f"Processed post {posts_scraped}/{max_posts}")
                        if posts_scraped >= max_posts:
                            break
                except Exception as e:
                    logger.warning(f"Error processing post: {str(e)}")

            # Scroll down
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(random.uniform(3, 5))  # Random delay
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                scroll_attempts += 1
                logger.warning(f"Scroll attempt {scroll_attempts}/{max_scroll_attempts} - no new content loaded")
            else:
                scroll_attempts = 0
            last_height = new_height

        # Save to CSV
        if comments_data:
            df = pd.DataFrame(comments_data)
            df.to_csv(output_csv, index=False, encoding='utf-8-sig')  # utf-8-sig for Arabic support
            logger.info(f"Saved {len(comments_data)} comments to {output_csv}")
        else:
            logger.warning("No comments collected - check hashtag matches or page access")

    except Exception as e:
        logger.error(f"Scraping failed: {str(e)}", exc_info=True)
        raise
    finally:
        driver.quit()

if __name__ == "__main__":
    # Replace with your Facebook credentials (store securely, e.g., in env variables)
    EMAIL = "toutoulamni@gmail.com"
    PASSWORD = "drack123"
    scrape_bein_sports_comments(EMAIL, PASSWORD, max_posts=10, output_csv='bein_sports_comments.csv')
