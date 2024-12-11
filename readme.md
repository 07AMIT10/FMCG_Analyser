# FMCG Product Analyzer

## Overview

The FMCG Product Analyzer is a Streamlit-based application designed to analyze images of Fast Moving Consumer Goods (FMCG) products. It extracts detailed information about each product, including brand, expiry date, and count, and generates a structured report in PDF format.

## Features

- Upload and analyze images of FMCG products.
- Extract product details such as brand, expiry date, and count.
- Display product details and inventory in a structured format.
- Generate and download a PDF report of the analyzed products.

## Requirements

- Python 3.7+
- Streamlit
- Google Cloud AI Platform
- Pandas
- Pillow
- ReportLab

## Installation

1. Clone the repository:

   ```sh
   git clone <repository-url>
   cd <repository-directory>
   ```

2. Install the required Python packages:

   ```sh
   pip install -r requirements.txt
   ```

3. Set up Google Cloud credentials:

   - Create a service account in Google Cloud and download the JSON key file.
   - Add the JSON key file content to Streamlit secrets (`.streamlit/secrets.toml`):
     ```toml
     [GOOGLE_APPLICATION_CREDENTIALS]
     // ...existing code...
     ```

## Usage

1. Run the Streamlit application:

   ```sh
   streamlit run main.py
   ```

2. Upload an image of FMCG products using the file uploader.

3. Click the "Analyze Image" button to extract product details.

4. View the extracted product details and inventory.

5. Click the "Generate PDF Report" button to create a PDF report of the analyzed products.

6. Download the generated PDF report.

## File Structure

- `main.py`: Main Streamlit application file.
- `image_analysis.py`: Functions for analyzing images and extracting product details.
- `data_utils.py`: Utility functions for updating product data.
- `report_generation.py`: Functions for generating PDF reports.
- `requirements.txt`: List of required Python packages.
- `readme.md`: Project documentation.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgements

- [Streamlit](https://streamlit.io/)
- [Google Cloud AI Platform](https://cloud.google.com/ai-platform)
- [Pandas](https://pandas.pydata.org/)
- [Pillow](https://python-pillow.org/)
- [ReportLab](https://www.reportlab.com/)


