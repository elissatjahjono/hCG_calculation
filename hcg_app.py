import streamlit as st
import scipy.optimize as optimize
import numpy as np
import pandas as pd

# Standards
hcgvals = np.array([0, 5, 25, 50, 100, 200])

# Define the model curve
def model4param(x, b, c, d, e):
    y = c + (d - c) * x**b / (e**b + x**b)
    return y

def getHCGFromReading(evalat, hcg_predict, read_val):
    diffs = np.abs(hcg_predict - read_val)
    min_ind = np.argmin(diffs)
    return evalat[min_ind]

# Streamlit App
st.title("hCG Concentration Calculator")

st.markdown("""
This app calculates hCG concentrations from ELISA readings. 
1. Enter your hCG standards readings for 0, 5, 25, 50, 100, & 200 mIU/mL hCG.
2. Upload an Excel file with your samples absorbance readings.  
3. Download the results.
""")

# Input: HCG readings
hcgreadings = st.text_input("Enter six hCG readings (comma-separated):", "0.012, 0.032, 0.207, 0.376, 0.801, 1.73")
try:
    hcgreadings = np.array([float(x.strip()) for x in hcgreadings.split(",")])
    if len(hcgreadings) != 6:
        st.error("Please enter exactly six values.")
except ValueError:
    st.error("Ensure the readings are valid numbers.")

# File upload
uploaded_file = st.file_uploader("Upload an Excel file with an 'Abs' column:", type=["xlsx"])

if uploaded_file and len(hcgreadings) == 6:
    # Read Excel file
    df = pd.read_excel(uploaded_file)

    if "Abs" not in df.columns:
        st.error("The uploaded file must contain an 'Abs' column.")
    else:
        # Curve fitting
        try:
            pfit, _ = optimize.curve_fit(model4param, hcgvals, hcgreadings, maxfev=5000)
            evalat = np.arange(0, 205, 0.1)
            hcg_predict = model4param(evalat, *pfit)

            # Calculate HCG concentrations
            toFindHCG = df['Abs'].values
            results = []
            for read_val in toFindHCG:
                hcg_concentration = getHCGFromReading(evalat, hcg_predict, read_val)
                results.append({'Reading': read_val, 'hCG Concentration': hcg_concentration})

            res = pd.DataFrame(results)

            # Show results
            st.write("### Results")
            st.dataframe(res)
            
            # Download results
            from io import BytesIO

            @st.cache_data
            def convert_df_to_excel(df):
                output = BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False, sheet_name="Results")
                processed_data = output.getvalue()
                return processed_data
            
            excel_data = convert_df_to_excel(res)
            st.download_button(
                label="Download Results as Excel",
                data=excel_data,
                file_name="hcg_results.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

        except RuntimeError as e:
            st.error(f"Error during curve fitting: {e}")

else:
    st.info("Upload a valid Excel file and ensure the readings are entered correctly.")

st.caption("Created with ❤️ using Streamlit.")
