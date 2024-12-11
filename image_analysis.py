import io
import json
import re
from datetime import datetime
import streamlit as st
from PIL import Image
from google.oauth2 import service_account
import vertexai
from vertexai.generative_models import GenerativeModel, Part

# Initialize Google Cloud credentials and Vertex AI
try:
    credentials_info = json.loads(st.secrets["GOOGLE_APPLICATION_CREDENTIALS"])
    credentials = service_account.Credentials.from_service_account_info(credentials_info)
    project_id = st.secrets["GOOGLE_CLOUD_PROJECT"]
    # Initialize Vertex AI
    vertexai.init(project=project_id, location="us-central1", credentials=credentials)
    # Initialize the model from Vertex AI
    model = GenerativeModel(st.secrets["GCP_MODEL_CRED"])
    st.success("Model loaded successfully")
except Exception as e:
    st.error(f"Error loading Google Cloud credentials or Vertex AI")
    st.stop()

def analyze_image(image):
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()

    image_part = Part.from_data(img_byte_arr, mime_type="image/png")

    prompt = """
      Below is a comprehensive prompt you can provide to a Large Language Model (LLM) that explains the task, input/output requirements, and the reasoning steps it should follow. Adapt the prompt as needed for your specific LLM environment.

---

**PROMPT START**

You are an AI assistant that is provided with a single image containing one or more FMCG (Fast Moving Consumer Goods) products. Your task is to analyze the image and produce a structured JSON output containing detailed information about each product identified in the image. Follow the instructions carefully and produce the response strictly in the required format.

### Input Description
- You will be given a single image of some common FMCG product(s).
- There can be multiple distinct products in the same image.
- A product may appear multiple times in the same image.

### What You Need To Identify
1. **Brand:**  
   - Identify the brand name of each distinct product visible in the image.  
   - There might be text or logo cues on the packaging that you can use to determine the brand name.  
   - If the brand is not recognizable or no brand is visible, output a best guess or "Unknown".

2. **Expiry Date:**  
   - Find and extract any expiry date information on the product packaging. The label might be indicated by phrases like "Expiry Date," "Best Before," "Use By," "BB," or similar.  
   - The expiry date might be given in various formats, such as:  
     - DD/MM/YYYY  
     - MM/YY  
     - DD-MM-YYYY  
     - Only a month and year (MM/YYYY)  
     - Only a year (YYYY)  
     - Relative information like "Best before 6 months from manufacture date" (if a manufacture date is also visible).  
   - **IMPORTANT** Convert all identified expiry date information into the format `DD/MM/YYYY` only.  
     - If the day (DD) is missing, use `01` as the default day.  
     - If the month (MM) is missing, use `01` (January) as the default month.  
     - If only a year (YYYY) is given, assume `01/01/YYYY`.  
     - If you need to compute a date from a given duration (e.g., "Best Before 6 months from a given manufacturing date"), add the specified duration to the manufacturing date and then format the resulting date as `DD/MM/YYYY`. If the computed day is unclear, choose the first day of the computed month. If no manufacturing day is given but a month/year is, assume the 1st of that month. If only a year is given, assume 01/01 of that year, then add the months.  
   
   Your goal is to present a single, best-guess expiry date in `DD/MM/YYYY` format.

3. **Item Count:**  
   - Count the number of identical units of each product visible in the image.  
   - Handle scenarios such as overlapping items, partially occluded items, or products placed side-by-side.  
   - Provide a best possible count based on the visible evidence in the image.

### Handling Multiple Products
- If the image contains multiple distinct products (e.g., Product A and Product B), you must output a JSON array containing one object per product.  
- Each object in the array will contain:  
  - `"brand"`: The detected brand name of the product.  
  - `"expiry_date"`: The expiry date of the product in `DD/MM/YYYY` format following the rules above. If no expiry date is visible or cannot be inferred, return a sensible default such as `"01/01/2099"` (or another clearly invalid date placeholder if instructed).  
  - `"count"`: The integer count of how many units of that product are visible in the image.

### Output Format
- Your final answer **must** be a JSON array of objects, where each object has the keys `brand`, `expiry_date`, and `count`.  
- Example structure (pseudocode):
  ```json
  [
    {
      "brand": "Product brand name",
      "expiry_date": "DD/MM/YYYY",
      "count": 2
    },
    {
      "brand": "Second product brand name",
      "expiry_date": "DD/MM/YYYY",
      "count": 1
    }
    // ... and so on for other products if they exist
  ]
  ```

### Sample Output (For Illustration)
```json
[
  {
    "brand": "Nestle",
    "expiry_date": "01/12/2024",
    "count": 2
  },
  {
    "brand": "Cadbury",
    "expiry_date": "01/06/2025",
    "count": 1
  }
]
```

### Important Notes
- The date format is strict: Always `DD/MM/YYYY`. For missing components, make sensible assumptions as described.
- If the product’s expiry date references a "Best Before" period from a manufacturing date, COMPUTE THE expected date as best as possible.
- If no expiry date is found at all, provide a fallback date like `"NA"` to indicate no available data.
- Ensure the count accurately reflects the number of identical items of that product in the image.
- If there are multiple products, output one JSON object per product, all contained in a JSON array.

Now, using these instructions, analyze the given image and produce the final JSON output.

**PROMPT END**

    Return only the JSON array of product objects without any additional text or formatting.
    """

    try:
        response = model.generate_content(
            [image_part, prompt],
            generation_config={
                "max_output_tokens": 2048,
                "temperature": 0.1,
                "top_p": 1,
                "top_k": 32
            }
        )
        # Clean the response text
        response_text = response.text.strip()
        # Remove any potential markdown code block markers
        response_text = re.sub(r'^```json\s*|\s*```$', '', response_text, flags=re.MULTILINE)
        return response_text
    except Exception as e:
        st.error(f"Error in image analysis")
        return None

def parse_product_details(analysis):
    try:
        if not analysis or not isinstance(analysis, str):
            st.error("Invalid analysis response")
            return None

        # Clean the input string
        analysis = analysis.strip()

        try:
            products = json.loads(analysis)
            if not isinstance(products, list):
                st.error("Expected a list of products in the analysis")
                return None
        except json.JSONDecodeError as e:
            st.error(f"JSON parsing error: {str(e)}\nReceived text: {analysis}")
            return None

        parsed_products = []

        for data in products:
            # Validate required fields and their types
            required_fields = {
                'brand': str,
                'expiry_date': str,
                'count': (int, float, str)  # Allow multiple numeric types
            }

            for field, field_type in required_fields.items():
                if field not in data:
                    st.error(f"Missing required field '{field}' in one of the products")
                    return None
                if not isinstance(data[field], field_type):
                    if field == 'count':
                        try:
                            data[field] = int(float(data[field]))
                        except (ValueError, TypeError):
                            st.error(f"Invalid type for field '{field}': expected numeric, got {type(data[field])}")
                            return None
                    else:
                        st.error(f"Invalid type for field '{field}': expected {field_type}, got {type(data[field])}")
                        return None

            try:
                # Add current timestamp in ISO format with timezone
                current_timestamp = datetime.now().astimezone().isoformat()

                # Parse expiry date with various formats
                expiry_date_str = data['expiry_date'].strip()
                expiry_date = None

                # List of date formats to try
                date_formats = ["%d/%m/%Y", "%d/%m/%y", "%m/%Y", "%m/%y", "%Y", "%y"]

                for fmt in date_formats:
                    try:
                        parsed_date = datetime.strptime(expiry_date_str, fmt)

                        # If day is missing, default to 1
                        if '%d' not in fmt:
                            parsed_date = parsed_date.replace(day=1)

                        expiry_date = parsed_date
                        break  # Exit the loop if parsing is successful
                    except ValueError:
                        continue

                current_date = datetime.now()

                if expiry_date:
                    # Compare dates based on available components
                    if expiry_date.year < current_date.year:
                        is_expired = "Yes"
                    elif expiry_date.year == current_date.year:
                        if expiry_date.month < current_date.month:
                            is_expired = "Yes"
                        elif expiry_date.month == current_date.month:
                            if expiry_date.day < current_date.day:
                                is_expired = "Yes"
                            else:
                                is_expired = "No"
                        else:
                            is_expired = "No"
                    else:
                        is_expired = "No"

                    lifespan_days = (expiry_date - current_date).days
                    lifespan = lifespan_days if lifespan_days >= 0 else "NA"
                else:
                    is_expired = "NA"
                    lifespan = "NA"

                parsed_product = {
                    "Sl No": None,  # Will be assigned later
                    "Timestamp": current_timestamp,
                    "Brand": data['brand'].strip(),
                    "Expiry Date": data['expiry_date'],
                    "Count": int(data['count']),
                    "Expired": is_expired,
                    "Expected Lifespan (Days)": lifespan
                }

                parsed_products.append(parsed_product)

            except Exception as e:
                st.error(f"Error processing product details: {str(e)}")
                return None

        return parsed_products

    except Exception as e:
        st.error(f"Error parsing product details: {str(e)}")
        return None