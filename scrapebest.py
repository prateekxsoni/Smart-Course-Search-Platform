import requests
from bs4 import BeautifulSoup
import json

BASE_URL = "https://courses.analyticsvidhya.com"
START_URL = f"{BASE_URL}/collections/courses?page="

def scrape_page(page_url, current_id):
    """Scrape data from a single page."""
    response = requests.get(page_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    courses = []
    course_cards = soup.select('li.products__list-item')

    for card in course_cards:
        try:
            # Extract basic course details
            title = card.select_one('h3').text.strip() if card.select_one('h3') else "N/A"
            lessons_or_courses = (
                card.select_one('span.course-card__lesson-count strong').text.strip()
                if card.select_one('span.course-card__lesson-count strong')
                else card.select_one('span.course-card__bundle-size').text.strip()
                if card.select_one('span.course-card__bundle-size')
                else "N/A"
            )
            price = card.select_one('span.course-card__price strong').text.strip() if card.select_one('span.course-card__price strong') else "Free"
            link = BASE_URL + card.select_one('a')['href']
            image_url = card.select_one('img.course-card__img')['src'] if card.select_one('img.course-card__img') else "N/A"
            
            print(f"Scraping course: {title}")

            # Visit course detail page for additional info
            course_response = requests.get(link)
            course_soup = BeautifulSoup(course_response.text, 'html.parser')

            description = course_soup.select_one('h2.section__subheading').text.strip() if course_soup.select_one('h2.section__subheading') else "No description available"
            details = course_soup.select('ul.text-icon__list li.text-icon__list-item')

            # Extract time, rating, and level
            time_to_complete = "N/A"
            rating = "N/A"
            level = "N/A"

            for detail in details:
                icon = detail.select_one('i')['class'] if detail.select_one('i') else []
                text = detail.select_one('h4').text.strip() if detail.select_one('h4') else ""

                if "fa-clock-o" in icon:
                    time_to_complete = text
                elif "fa-star" in icon:
                    rating = text
                elif "fa-signal" in icon:
                    level = text

            # Append the course data with an incremented id
            courses.append({
                'id': current_id,
                'title': title,
                'lessons_or_courses': lessons_or_courses,
                'price': price,
                'link': link,
                'image_url': image_url,
                'description': description,
                'time_to_complete': time_to_complete,
                'rating': rating,
                'level': level
            })
            current_id += 1
        except Exception as e:
            print(f"Error processing course: {e}")

    return courses, current_id

def scrape_all_pages():
    """Scrape all 9 pages."""
    all_courses = []
    current_id = 1

    for page_number in range(1, 10):
        page_url = f"{START_URL}{page_number}"
        print(f"Scraping page: {page_url}")
        courses, current_id = scrape_page(page_url, current_id)
        all_courses.extend(courses)

    return all_courses

if __name__ == "__main__":
    all_courses_data = scrape_all_pages()

    # Save the scraped data to a JSON file
    with open('all_courses.json', 'w', encoding='utf-8') as f:
        json.dump(all_courses_data, f, ensure_ascii=False, indent=4)

    print(f"Scraped {len(all_courses_data)} courses. Data saved to 'all_courses.json'")
