# Smart Course Search Engine

Smart Course Search Engine is a web application that enables users to search for courses using advanced vector-based similarity search. It leverages OpenAI’s GPT-3.5-turbo for query refinement and recommendations, FAISS for efficient vector storage and retrieval, and includes a scraper (`scrapebest.py`) to update the course database dynamically.

---

## Features

- **Advanced Search**: Find courses using natural language queries with refined results powered by OpenAI.
- **Dynamic Filtering**: Filter results based on level, length, rating, price, and other attributes.
- **Interactive Suggestions**: Receive personalized course suggestions based on search results.
- **Live Database Updates**: Dynamically update the course database using the integrated scraper tool.
- **Responsive Design**: Aesthetic and mobile-friendly interface built with Tailwind CSS.
- **Deployment-Ready**: Compatible with hosting platforms like Render, Railway, or local deployment.

---

## Technologies Used

### Backend
- **Flask**: Web framework to handle routing, API, and server logic.
- **FAISS (Facebook AI Similarity Search)**: Efficient vector-based similarity search to store and retrieve course embeddings.
- **OpenAI GPT-3.5-turbo**: Used for query refinement and generating personalized suggestions.
- **Hugging Face Embeddings**: To convert course descriptions into vector representations for similarity search.

### Frontend
- **HTML**: Structure of the web application.
- **Tailwind CSS**: Ensures a responsive and visually appealing user interface.
- **JavaScript**: Handles interactions such as search requests and results rendering dynamically.

### Scraper
- **`scrapebest.py`**: Python script to scrape course data and generate a fresh `all_courses.json` file.
- **Libraries Used in Scraper**:
  - `BeautifulSoup`: For HTML parsing and extracting course details.
  - `Requests`: To handle HTTP requests during web scraping.

---

## Why These Tools?

- **FAISS**: Chosen for its performance in large-scale similarity searches, which makes it ideal for vector retrieval.
- **OpenAI GPT-3.5-turbo**: Its language understanding capabilities provide excellent results in query refinement and suggestion generation.
- **Hugging Face Embeddings**: Lightweight and efficient embedding generation for transforming textual data into vectors.
- **Flask**: Simple yet powerful enough to handle both API and frontend rendering needs.
- **Tailwind CSS**: Enables rapid development of a clean, responsive interface.

---

## Block Diagram

<p align="center">
    <img src="https://i.imgur.com/dRDD8N0.jpeg" alt="Block Diagram">
</p>

---

## Updating the Course Database

- **Dynamic Updates via Web Interface**:
    A button on the web interface allows you to update the course database dynamically.
    When clicked, it triggers the scrapebest.py script to scrape and refresh all_courses.json.
- **Logging Updates**:
    While the scraper is running, updates are printed in real-time on the CLI and the webpage for transparency.
