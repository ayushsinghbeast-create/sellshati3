import streamlit as st
import pandas as pd
from datetime import datetime, date
from fpdf import FPDF
import base64

# Page configuration
st.set_page_config(page_title="SellSathi", layout="wide", initial_sidebar_state="expanded")

# --- FUNCTIONS ---

# Function to create a downloadable PDF link
def create_download_link(val, filename):
    b64 = base64.b64encode(val)
    return f'<a href="data:application/octet-stream;base64,{b64.decode()}" download="{filename}.pdf">Download Bill PDF</a>'

# Function to generate PDF
def generate_bill_pdf(bill_data):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    
    # Business Name
    pdf.cell(0, 10, f"Bill for: {bill_data['business_name']}", 0, 1, 'C')
    pdf.ln(10)
    
    # Customer Details
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 10, f"Customer Name: {bill_data['customer_name']}", 0, 1)
    pdf.cell(0, 10, f"Customer Contact: {bill_data['customer_contact']}", 0, 1)
    pdf.cell(0, 10, f"Selling Date: {bill_data['selling_date']}", 0, 1)
    pdf.ln(10)
    
    # Products Table
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(100, 10, 'Product Name', 1)
    pdf.cell(40, 10, 'Quantity', 1)
    pdf.cell(40, 10, 'Price', 1, 1)
    
    pdf.set_font("Arial", '', 12)
    total_amount = 0
    for product in bill_data['products']:
        pdf.cell(100, 10, product['name'], 1)
        pdf.cell(40, 10, str(product['quantity']), 1)
        pdf.cell(40, 10, str(product['price']), 1, 1)
        total_amount += product['quantity'] * product['price']
    
    # Total Amount
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(140, 10, 'Total Amount', 1)
    pdf.cell(40, 10, str(total_amount), 1, 1)
    
    return pdf.output(dest='S').encode('latin-1')


# --- INITIALIZE SESSION STATE ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_data = {}
    st.session_state.stock = []
    st.session_state.sales = []
    st.session_state.bills = []
    st.session_state.page = "Dashboard"

# --- UI Customization (Polished UI) ---
st.markdown("""
<style>
    /* Main App Styling */
    .stApp {
        background-color: #f0f2f6; /* Lighter grey background */
    }
    /* Metric Card Styling for 3D effect */
    .metric-card {
        background-color: #ffffff;
        border: 1px solid #dee2e6;
        border-radius: 15px;
        padding: 25px 20px;
        text-align: center;
        box-shadow: 0 8px 16px rgba(0,0,0,0.1);
        transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
        margin-bottom: 20px;
        height: 100%;
    }
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 24px rgba(0,0,0,0.15);
    }
    .metric-card h3 {
        font-size: 1.1rem;
        color: #495057;
        margin-bottom: 10px;
        font-weight: 500;
    }
    .metric-card p {
        font-size: 2.2rem;
        font-weight: 700;
        color: #0d6efd;
    }
    /* Button Styling */
    .stButton>button {
        border-radius: 8px;
        background-color: #0d6efd;
        color: white;
        border: none;
        padding: 10px 20px;
        transition: background-color 0.2s;
    }
    .stButton>button:hover {
        background-color: #0a58ca;
        color: white;
    }
    /* Expander Styling */
    .st-emotion-cache-1h9usn1 { /* Expander header */
        background-color: #ffffff;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)


# --- PAGES LOGIC ---

# 1. Registration Page
def register_page():
    st.title("Sellsathi")
    st.header("Register Your Business")

    with st.form("registration_form"):
        name = st.text_input("Your Name")
        email = st.text_input("Your Email")
        business_name = st.text_input("Business Name")
        business_type = st.text_input("Business Type (e.g., Retail, Wholesale)")
        
        submitted = st.form_submit_button("Confirm Register")
        if submitted:
            if name and email and business_name and business_type:
                st.session_state.user_data = {
                    "name": name, "email": email,
                    "business_name": business_name, "business_type": business_type
                }
                st.session_state.logged_in = True
                st.success("Registration Successful!")
                st.rerun()
            else:
                st.error("Please fill all the details.")

# 2. Dashboard Page
def dashboard_page():
    st.title(st.session_state.user_data.get("business_name", "Dashboard"))
    
    # Calculate Metrics
    today = date.today()
    sales_df = pd.DataFrame(st.session_state.sales)
    
    # Initialize all metrics to 0
    today_sales_total, today_profit_total, today_exp_total = 0, 0, 0
    monthly_sales_total, monthly_profit_total, monthly_exp_total = 0, 0, 0

    if not sales_df.empty:
        sales_df['date'] = pd.to_datetime(sales_df['date']).dt.date
        
        # Today's metrics
        today_sales_df = sales_df[sales_df['date'] == today]
        today_sales_total = (today_sales_df['sell_price'] * today_sales_df['qty']).sum()
        today_profit_total = ((today_sales_df['sell_price'] - today_sales_df['buy_price']) * today_sales_df['qty']).sum()
        today_exp_total = (today_sales_df['buy_price'] * today_sales_df['qty']).sum() # Expenditure from buy price

        # Monthly metrics
        monthly_sales_df = sales_df[pd.to_datetime(sales_df['date']).dt.month == today.month]
        monthly_sales_total = (monthly_sales_df['sell_price'] * monthly_sales_df['qty']).sum()
        monthly_profit_total = ((monthly_sales_df['sell_price'] - monthly_sales_df['buy_price']) * monthly_sales_df['qty']).sum()
        monthly_exp_total = (monthly_sales_df['buy_price'] * monthly_sales_df['qty']).sum() # Expenditure from buy price

    # Display Metrics with new 3D UI
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""<div class="metric-card"><h3>Today's Sales</h3><p>₹{today_sales_total:,.2f}</p></div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""<div class="metric-card"><h3>Today's Profit</h3><p>₹{today_profit_total:,.2f}</p></div>""", unsafe_allow_html=True)
    with col3:
        st.markdown(f"""<div class="metric-card"><h3>Today's Expenditure</h3><p>₹{today_exp_total:,.2f}</p></div>""", unsafe_allow_html=True)

    col4, col5, col6 = st.columns(3)
    with col4:
        st.markdown(f"""<div class="metric-card"><h3>Monthly Sales</h3><p>₹{monthly_sales_total:,.2f}</p></div>""", unsafe_allow_html=True)
    with col5:
        st.markdown(f"""<div class="metric-card"><h3>Monthly Profit</h3><p>₹{monthly_profit_total:,.2f}</p></div>""", unsafe_allow_html=True)
    with col6:
        st.markdown(f"""<div class="metric-card"><h3>Monthly Expenditure</h3><p>₹{monthly_exp_total:,.2f}</p></div>""", unsafe_allow_html=True)

    st.markdown("---")

    # Add Sales Form (Expenditure form removed)
    with st.expander("Add Sale", expanded=False):
        with st.form("add_sale_form", clear_on_submit=True):
            product_names = [p['name'] for p in st.session_state.stock if p['qty'] > 0]
            if not product_names:
                st.warning("No products in stock. Please add products in the 'Stock' page first.")
            else:
                selected_product_name = st.selectbox("Search Product", options=product_names)
                selected_product = next((p for p in st.session_state.stock if p['name'] == selected_product_name), None)
                
                if selected_product:
                    sell_price = st.number_input("Sell Price", value=selected_product['sell_price'], min_value=0.0)
                    quantity = st.number_input("Quantity", min_value=1, max_value=selected_product['qty'], value=1, step=1)
                    
                    sale_submitted = st.form_submit_button("Confirm Sale")
                    if sale_submitted:
                        st.session_state.sales.append({
                            'name': selected_product_name, 'buy_price': selected_product['buy_price'],
                            'sell_price': sell_price, 'qty': quantity, 'date': datetime.now()
                        })
                        selected_product['qty'] -= quantity
                        st.success(f"Sale of {quantity} x {selected_product_name} recorded!")
                        st.rerun()

# 3. Stock Page
def stock_page():
    st.title("Stock Management")
    st.header(st.session_state.user_data.get("business_name"))

    with st.expander("Add Stock / Product", expanded=False):
        with st.form("add_product_form", clear_on_submit=True):
            product_name = st.text_input("Product Name")
            buy_price = st.number_input("Buy Price", min_value=0.0)
            sell_price = st.number_input("Sell Price", min_value=0.0)
            quantity = st.number_input("Stock Quantity", min_value=0, step=1)
            submitted = st.form_submit_button("Confirm Add Product")
            if submitted:
                if product_name and buy_price > 0 and sell_price > 0:
                    existing_product = next((p for p in st.session_state.stock if p['name'].lower() == product_name.lower()), None)
                    if existing_product:
                        existing_product['buy_price'] = (existing_product['buy_price'] * existing_product['qty'] + buy_price * quantity) / (existing_product['qty'] + quantity)
                        existing_product['sell_price'] = sell_price
                        existing_product['qty'] += quantity
                        st.success(f"Stock for '{product_name}' updated!")
                    else:
                        st.session_state.stock.append({
                            "name": product_name, "buy_price": buy_price,
                            "sell_price": sell_price, "qty": quantity
                        })
                        st.success(f"Product '{product_name}' added to stock!")
                    st.rerun()
                else:
                    st.error("Please provide valid product details.")

    st.markdown("---")
    st.subheader("Current Stock")
    if not st.session_state.stock:
        st.info("Your stock is empty.")
    else:
        stock_df = pd.DataFrame(st.session_state.stock)
        stock_df.columns = ["Product Name", "Buy Price", "Sell Price", "Quantity"]
        st.dataframe(stock_df, use_container_width=True)


# 4. Bill Page
def bill_page():
    st.title("Bill Generation")
    
    with st.expander("Generate New Bill"):
        with st.form("generate_bill_form"):
            customer_name = st.text_input("Customer Name")
            customer_contact = st.text_input("Customer Contact (Optional)")
            selling_date = st.date_input("Selling Date", value=datetime.now())

            st.subheader("Products")
            if 'bill_products' not in st.session_state: st.session_state.bill_products = []

            def add_product_to_bill():
                p_name = st.session_state['bill_product_name']
                p_qty = st.session_state['bill_product_qty']
                p_details = next((p for p in st.session_state.stock if p['name'] == p_name), None)
                if p_details:
                    st.session_state.bill_products.append({"name": p_name, "quantity": p_qty, "price": p_details['sell_price']})
            
            bill_col1, bill_col2, bill_col3 = st.columns([3,1,1.2])
            with bill_col1:
                st.selectbox("Select Product", options=[p['name'] for p in st.session_state.stock], key='bill_product_name')
            with bill_col2:
                st.number_input("Quantity", min_value=1, step=1, key='bill_product_qty')
            with bill_col3:
                st.write("") 
                st.form_submit_button("Add Product", on_click=add_product_to_bill)
            
            if st.session_state.bill_products:
                st.write("Products in current bill:")
                st.dataframe(pd.DataFrame(st.session_state.bill_products), use_container_width=True)

            submitted = st.form_submit_button("Confirm and Generate Bill")
            if submitted:
                if customer_name and st.session_state.bill_products:
                    bill_data = {
                        'business_name': st.session_state.user_data.get("business_name"),
                        'customer_name': customer_name, 'customer_contact': customer_contact,
                        'selling_date': str(selling_date), 'products': st.session_state.bill_products,
                        'bill_id': f"BILL-{len(st.session_state.bills)+1}-{datetime.now().strftime('%Y%m%d')}"
                    }
                    st.session_state.bills.append(bill_data)
                    st.session_state.bill_products = []
                    st.success("Bill generated successfully!")
                    pdf_data = generate_bill_pdf(bill_data)
                    st.markdown(create_download_link(pdf_data, bill_data['bill_id']), unsafe_allow_html=True)
                    st.rerun()
                else:
                    st.error("Please enter customer name and add at least one product.")
    
    st.markdown("---")
    st.subheader("Bill History")
    if not st.session_state.bills: st.info("No bills generated yet.")
    else:
        for bill in reversed(st.session_state.bills):
            with st.container(border=True):
                st.write(f"**Bill ID:** {bill['bill_id']} | **Customer:** {bill['customer_name']} | **Date:** {bill['selling_date']}")
                total = sum(p['quantity'] * p['price'] for p in bill['products'])
                st.write(f"**Total Amount:** ₹{total:,.2f}")
                pdf_data = generate_bill_pdf(bill)
                st.markdown(create_download_link(pdf_data, bill['bill_id']), unsafe_allow_html=True)


# 5. Business Analysis Page
def analysis_page():
    st.title("Business Analysis")
    if not st.session_state.sales:
        st.info("No sales data available for analysis.")
        return

    sales_df = pd.DataFrame(st.session_state.sales)
    sales_df['total_sale'] = sales_df['sell_price'] * sales_df['qty']
    sales_df['profit'] = (sales_df['sell_price'] - sales_df['buy_price']) * sales_df['qty']
    sales_df['date'] = pd.to_datetime(sales_df['date']).dt.date

    st.subheader("Key Performance Indicators")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""<div class="metric-card"><h3>Most Selling Product</h3><p style="font-size: 1.2rem; color: #333;">{sales_df.groupby('name')['qty'].sum().idxmax()}</p></div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""<div class="metric-card"><h3>Least Selling Product</h3><p style="font-size: 1.2rem; color: #333;">{sales_df.groupby('name')['qty'].sum().idxmin()}</p></div>""", unsafe_allow_html=True)
    with col3:
        st.markdown(f"""<div class="metric-card"><h3>Most Profitable Product</h3><p style="font-size: 1.2rem; color: #333;">{sales_df.groupby('name')['profit'].sum().idxmax()}</p></div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("Daily Sales Performance")
    daily_sales = sales_df.groupby('date')['total_sale'].sum()
    st.bar_chart(daily_sales)
    st.subheader("All Sales Data")
    st.dataframe(sales_df, use_container_width=True)


# 6. About Page
def about_page():
    st.title("About")
    st.header("About Sellsathi")
    st.info("""
    Sellsathi is a simple and intuitive application designed to help small business owners manage their sales, stock, and billing with ease. 
    It provides a clear dashboard with key metrics, a straightforward stock management system, and quick bill generation. 
    The business analysis section helps you understand your performance and make better decisions.
    """)

    st.header("About Your Business")
    user_data = st.session_state.user_data
    st.markdown(f"""
    - **Business Name:** {user_data.get('business_name')}
    - **Owner Name:** {user_data.get('name')}
    - **Contact Email:** {user_data.get('email')}
    - **Business Type:** {user_data.get('business_type')}
    """)


# --- MAIN APP ROUTING ---
if not st.session_state.logged_in:
    register_page()
else:
    with st.sidebar:
        st.header("Sellsathi")
        st.session_state.page = st.radio("Navigation",
            ["Dashboard", "Stock", "Bill", "Business Analysis", "About"],
            label_visibility="collapsed"
        )
    
    if st.session_state.page == "Dashboard": dashboard_page()
    elif st.session_state.page == "Stock": stock_page()
    elif st.session_state.page == "Bill": bill_page()
    elif st.session_state.page == "Business Analysis": analysis_page()
    elif st.session_state.page == "About": about_page()
