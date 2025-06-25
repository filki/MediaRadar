# News Radar

![Version](https://img.shields.io/badge/version-0.1.3-blue)

A web application that analyzes news articles and visualizes relationships between entities (people, organizations, locations) using Natural Language Processing.

## Features

- Fetches latest news articles
- Extracts named entities using BERT NER model
- Visualizes relationships between entities in an interactive graph
- Performs sentiment analysis on news articles
- Displays sentiment summary and distribution
- Clean, responsive web interface

## Prerequisites

- Python 3.8+
- pip
- Git
- GNews API key (free tier available)

## 🚀 Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/news-radar.git
   cd news-radar
   ```

2. Create and activate a virtual environment:
   ```bash
   # On Windows
   python -m venv venv
   .\venv\Scripts\activate
   
   # On macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   - Create a `.env` file in the project root
   - Add your GNews API key:
     ```
     GNEWS_API_KEY=your_api_key_here
     ```

## Usage

1. Run the application:
   ```bash
   python app.py
   ```

2. Open your browser and navigate to `http://localhost:5000`

3. Click the "Generuj Graf" button to fetch and analyze news articles

## Project Structure

- `app.py` - Main Flask application
- `fetcher.py` - Handles news fetching and NLP processing
- `templates/` - HTML templates
  - `index.html` - Main application interface
- `requirements.txt` - Python dependencies
- `.gitignore` - Specifies intentionally untracked files to ignore
## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
