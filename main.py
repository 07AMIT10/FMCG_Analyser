import streamlit as st
import pandas as pd
from PIL import Image

# Import functions from modules
from image_analysis import analyze_image, parse_product_details
from data_utils import update_product_data
from report_generation import generate_pdf_report

# Initialize Streamlit page configuration
st.set_page_config(page_title="FMCG Product Analyzer", layout="wide")

# Initialize session state for product tracking
if 'product_data' not in st.session_state:
    st.session_state.product_data = []

def main():
    st.title("FMCG Product Analyzer and Tracker")

    uploaded_file = st.file_uploader("Choose an image of FMCG products", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        image = Image.open(uploaded_file)

        # Resize image for display
        max_width = 300
        ratio = max_width / image.width
        new_size = (max_width, int(image.height * ratio))
        resized_image = image.resize(new_size)

        # Display resized image
        col1, col2 = st.columns([1, 2])
        with col1:
            st.image(resized_image, caption="Uploaded Image", use_container_width=True)

        with col2:
            if st.button("Analyze Image"):
                with st.spinner("Analyzing image..."):
                    analysis = analyze_image(image)
                    if analysis:
                        # st.subheader("Raw Model Output:")
                        # st.code(analysis, language="json")

                        products = parse_product_details(analysis)
                        if products:  # Valid products list
                            update_product_data(products)
                            st.subheader("Product Details:")
                            for product in products:
                                # Display product details
                                st.markdown(f"**Product Details for {product['Brand']} (Expiry: {product['Expiry Date']}):**")
                                display_fields = {k:v for k,v in product.items() if k not in ['Sl No', 'Timestamp']}
                                for key, value in display_fields.items():
                                    st.write(f"**{key}:** {value}")
                                st.write("---")
                        else:
                            st.error("Failed to parse product details. Please try again.")
                    else:
                        st.error("Unable to analyze the image. Please try again with a different image.")

    st.subheader("Product Inventory")
    if st.session_state.product_data:
        df = pd.DataFrame(st.session_state.product_data)

        # Reorder columns
        columns_order = [
            'Sl No', 'Timestamp', 'Brand', 'Expiry Date',
            'Count', 'Expired', 'Expected Lifespan (Days)'
        ]
        df = df[columns_order]

        # Style the dataframe
        styled_df = df.style.set_properties(**{
            'text-align': 'left',
            'white-space': 'nowrap'
        })
        styled_df = styled_df.set_table_styles([
            {'selector': 'th', 'props': [
                ('font-weight', 'bold'),
                ('text-align', 'left'),
                ('padding', '8px')
            ]},
            {'selector': 'td', 'props': [
                ('padding', '8px'),
                ('border', '1px solid #ddd')
            ]}
        ])

        st.write(styled_df.to_html(escape=False, index=False), unsafe_allow_html=True)

        # Add option to generate report
        if st.button("Generate PDF Report"):
            # Generate report
            report_generated = generate_pdf_report(st.session_state.product_data, "product_report.pdf")
            if report_generated:
                st.success("Report generated successfully!")
                with open("product_report.pdf", "rb") as file:
                    btn = st.download_button(
                        label="Download PDF",
                        data=file,
                        file_name="product_report.pdf",
                        mime="application/octet-stream"
                    )
            else:
                st.error("Failed to generate report.")
    else:
        st.write("No products scanned yet.")

if __name__ == "__main__":
    main()