# AI-Powered Text Summarizer

This project is an AI-powered text summarization tool featuring a Python backend running on Google Colab and a React frontend. It leverages Hugging Face Transformers for abstractive summarization and custom implementations for extractive methods, offering various summarization styles for text, URLs, and PDF documents. The backend is exposed publicly using ngrok for seamless communication with the React frontend.

## ✨ Features

* **Versatile Summarization:** Summarize plain text, content from URLs, and text extracted from PDF documents. 
* **Multiple Techniques:**
    * **Abstractive Summarization:** Utilizes the `facebook/bart-large-cnn` model from Hugging Face Transformers for generating human-like summaries. 
    * **Extractive Summarization:** Implements TF-IDF, TextRank, and Centroid-based algorithms to select key sentences. 
* **Diverse Styles:** Offers various summarization styles such as default, concise, detailed, aggressive, creative, bullet points, ELI5 (Explain Like I'm 5), and academic. 
* **User-Friendly Frontend:** Interactive React application for easy input and visualization of summaries.
* **FastAPI Backend:** Robust and efficient backend API built with Python and FastAPI. 
* **Colab Deployment with Ngrok:** Backend runs in a Google Colab environment, made publicly accessible via ngrok tunneling. 
* **PDF & URL Processing:** Capable of extracting text directly from web links and uploaded PDF files. 
* **(Dummy) Translation Endpoint:** Includes a basic endpoint for text translation (can be expanded). 

## 🛠️ Tech Stack

* **Frontend:** React
* **Backend:** Python, FastAPI, Uvicorn 
* **AI/ML:**
    * PyTorch 
    * Hugging Face Transformers (`facebook/bart-large-cnn`) 
    * NLTK (for stopwords and text processing) 
    * Scikit-learn (for TF-IDF and cosine similarity) 
* **Text Extraction:**
    * BeautifulSoup4 (for URL content) 
    * PyMuPDF (fitz) (for PDF text extraction) 
* **Tunneling:** Ngrok 
* **Environment:** Google Colab (with GPU acceleration) 

## 🏗️ Architecture Overview

The application follows a simple client-server architecture:

1.  **React Frontend:** Users interact with the React application to input text, URLs, or upload PDFs, and select summarization options.
2.  **Ngrok Tunnel:** The React frontend sends requests to the public URL provided by ngrok.
3.  **FastAPI Backend (on Google Colab):** Ngrok tunnels these requests to the FastAPI application running within the Google Colab notebook.
4.  **Summarization Engine:** The FastAPI backend processes the request using the appropriate summarization model (abstractive or extractive) and returns the summary.
5.  **Response Flow:** The summary is sent back through ngrok to the React frontend for display to the user.
   
[User via React App] ----> [Ngrok Public URL] ----> [FastAPI on Google Colab] ----> [AI Summarization Logic]
^                                                                                |
|__**[Summary]**|

## 🚀 Setup and Running

### 1. Backend (Google Colab - `AISummarizer.ipynb`)

1.  **Open in Colab:** Upload and open the `AISummarizer.ipynb` notebook in Google Colab.
2.  **Enable GPU:**
    * Go to `Runtime` -> `Change runtime type`.
    * Select `GPU` from the `Hardware accelerator` dropdown menu and click `Save`. 
3.  **Ngrok Authentication:**
    * Sign up for a free account at [ngrok.com](https://ngrok.com) and get your authtoken.
    * In the first code cell of the notebook, replace `"Replace with your authtoken"` (or the existing token in the file for `NGROK_AUTH_TOKEN`) with your actual ngrok authtoken. 
    ```python
    ngrok_authtoken = "YOUR_ACTUAL_NGROK_AUTHTOKEN" # For the first cell
    # Or find and replace:
    NGROK_AUTH_TOKEN = "YOUR_ACTUAL_NGROK_AUTHTOKEN" # Near the end of the imports
    ```
4.  **Run Notebook:**
    * Click on `Runtime` -> `Run all`.
    * The notebook will install dependencies, download models, and start the FastAPI server.
    * Once running, an ngrok public URL will be printed in the output of the last cell (e.g., `https://<unique_id>.ngrok-free.app`). Copy this URL.

### 2. Frontend (React App)

*(Assuming your React app is in a `/frontend` directory within this project)*

1.  **Clone Repository (if you haven't already):**
    ```bash
    git clone <your-repository-url>
    cd <your-repository-url>/frontend
    ```
2.  **Install Dependencies:**
    ```bash
    npm install
    # or
    yarn install
    ```
3.  **Configure Backend URL:**
    * In your React application's configuration (e.g., a `.env` file, a `config.js`, or directly in your API service files), update the API base URL to the ngrok URL you copied from the Colab notebook.
    * Example (if using a `.env` file):
        ```env
        REACT_APP_API_BASE_URL=https://<unique_id>.ngrok-free.app
        ```
4.  **Start React App:**
    ```bash
    npm start
    # or
    yarn start
    ```
    Your React application should now be running locally (usually at `http://localhost:3000`) and communicating with the backend via the ngrok tunnel.

## ⚙️ API Endpoints

The backend exposes the following API endpoints: 

* `GET /`: Welcome message and basic API information.
* `GET /health`: Health check for the API and model status.
* `GET /summarization_types`: Lists available summarization types (e.g., "abstractive", "extractive").
* `GET /styles/{summarization_type}`: Get available summarization styles for a specific type (e.g., `/styles/abstractive`).
* `POST /summarize/text`: Summarize plain text.
    * **Body (JSON):** `{ "text": "...", "max_length": 150, "min_length": 30, "style": "abstractive:default" }`
* `POST /summarize/url`: Summarize content from a URL.
    * **Body (JSON):** `{ "url": "http://...", "max_length": 150, "min_length": 30, "style": "abstractive:default" }`
* `POST /summarize/pdf`: Summarize content from an uploaded PDF file.
    * **Body (FormData):** `file` (PDF file), `max_length` (int), `min_length` (int), `style` (str)
* `POST /translate`: (Dummy) Translate text.
    * **Body (JSON):** `{ "text": "...", "target_language": "es" }`

### Example `curl` Request (for text summarization): 

Replace `<your_ngrok_url>` with the actual public URL from your Colab notebook.

```bash
curl -X POST "<your_ngrok_url>/summarize/text" \
-H "Content-Type: application/json" \
-d '{
      "text": "Your extensive text to summarize here...",
      "max_length": 150,
      "min_length": 30,
      "style": "abstractive:default"
    }'