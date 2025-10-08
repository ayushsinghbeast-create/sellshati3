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
    b64 = base64.b64encode(val)  # val looks like b'...'
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
# This is like a temporary database for the app session
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_data = {}
    st.session_state.stock = [] # List of dicts: {name, buy_price, sell_price, qty}
    st.session_state.sales = [] # List of dicts: {name, buy_price, sell_price, qty, date}
    st.session_state.expenditures = [] # List of dicts: {reason, amount, date}
    st.session_state.bills = [] # List of bill data
    st.session_state.page = "Dashboard"

# --- UI Customization ---
st.markdown("""
<style>
    .st-emotion-cache-1y4p8pa {
        padding-top: 2rem;
    }
    .st-emotion-cache-16txtl3 {
        padding: 2rem 1rem;
    }
    .st-emotion-cache-1d3w5bk {
        background-color: #0d6efd;
        color: white;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
    }
    .st-emotion-cache-1d3w5bk .stMetricLabel {
        color: white;
    }
    .st-emotion-cache-1d3w5bk .stMetricValue {
        color: white;
    }
    .stButton>button {
        border-radius: 8px;
        background-color: #0d6efd;
        color: white;
        border: none;
    }
    .stButton>button:hover {
        background-color: #0a58ca;
        color: white;
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
                    "name": name,
                    "email": email,
                    "business_name": business_name,
                    "business_type": business_type
                }
                st.session_state.logged_in = True
                st.success("Registration Successful!")
                st.rerun() # Rerun to redirect to dashboard
            else:
                st.error("Please fill all the details.")

# 2. Dashboard Page
def dashboard_page():
    st.title(st.session_state.user_data.get("business_name", "Dashboard"))
    
    # Calculate Metrics
    today = date.today()
    sales_df = pd.DataFrame(st.session_state.sales)
    exp_df = pd.DataFrame(st.session_state.expenditures)
    
    # Today's metrics
    today_sales_total = 0
    today_profit_total = 0
    if not sales_df.empty:
        sales_df['date'] = pd.to_datetime(sales_df['date']).dt.date
        today_sales_df = sales_df[sales_df['date'] == today]
        today_sales_total = (today_sales_df['sell_price'] * today_sales_df['qty']).sum()
        today_profit_total = ((today_sales_df['sell_price'] - today_sales_df['buy_price']) * today_sales_df['qty']).sum()

    today_exp_total = 0
    if not exp_df.empty:
        exp_df['date'] = pd.to_datetime(exp_df['date']).dt.date
        today_exp_df = exp_df[exp_df['date'] == today]
        today_exp_total = today_exp_df['amount'].sum()
        
    # Monthly metrics
    monthly_sales_total = 0
    monthly_profit_total = 0
    if not sales_df.empty:
        monthly_sales_df = sales_df[pd.to_datetime(sales_df['date']).dt.month == today.month]
        monthly_sales_total = (monthly_sales_df['sell_price'] * monthly_sales_df['qty']).sum()
        monthly_profit_total = ((monthly_sales_df['sell_price'] - monthly_sales_df['buy_price']) * monthly_sales_df['qty']).sum()

    monthly_exp_total = 0
    if not exp_df.empty:
        monthly_exp_df = exp_df[pd.to_datetime(exp_df['date']).dt.month == today.month]
        monthly_exp_total = monthly_exp_df['amount'].sum()

    # Display Metrics
    col1, col2, col3 = st.columns(3)
    col4, col5, col6 = st.columns(3)

    with col1:
        st.metric(label="Today's Sales", value=f"₹{today_sales_total:,.2f}")
    with col2:
        st.metric(label="Today's Profit", value=f"₹{today_profit_total:,.2f}")
    with col3:
        st.metric(label="Today's Expenditure", value=f"₹{today_exp_total:,.2f}")
    with col4:
        st.metric(label="Monthly Sales", value=f"₹{monthly_sales_total:,.2f}")
    with col5:
        st.metric(label="Monthly Profit", value=f"₹{monthly_profit_total:,.2f}")
    with col6:
        st.metric(label="Monthly Expenditure", value=f"₹{monthly_exp_total:,.2f}")

    st.markdown("---")

    # Add Sales and Expenditure Forms
    form_col1, form_col2 = st.columns(2)

    with form_col1:
        with st.expander("Add Sale", expanded=False):
            with st.form("add_sale_form", clear_on_submit=True):
                product_names = [p['name'] for p in st.session_state.stock if p['qty'] > 0]
                if not product_names:
                    st.warning("No products in stock. Please add products in the 'Stock' page first.")
                else:
                    selected_product_name = st.selectbox("Search Product", options=product_names)
                    
                    # Find selected product details
                    selected_product = next((p for p in st.session_state.stock if p['name'] == selected_product_name), None)
                    
                    if selected_product:
                        sell_price = st.number_input("Sell Price", value=selected_product['sell_price'], min_value=0.0)
                        quantity = st.number_input("Quantity", min_value=1, max_value=selected_product['qty'], value=1, step=1)
                        
                        sale_submitted = st.form_submit_button("Confirm Sale")
                        if sale_submitted:
                            # Add to sales list
                            st.session_state.sales.append({
                                'name': selected_product_name,
                                'buy_price': selected_product['buy_price'],
                                'sell_price': sell_price,
                                'qty': quantity,
                                'date': datetime.now()
                            })
                            # Update stock quantity
                            selected_product['qty'] -= quantity
                            st.success(f"Sale of {quantity} x {selected_product_name} recorded!")
                            st.rerun()

    with form_col2:
        with st.expander("Add Expenditure", expanded=False):
            with st.form("add_expenditure_form", clear_on_submit=True):
                reason = st.text_input("Reason for Expenditure")
                amount = st.number_input("Amount", min_value=0.01)
                exp_submitted = st.form_submit_button("Confirm Expenditure")
                if exp_submitted:
                    st.session_state.expenditures.append({
                        'reason': reason,
                        'amount': amount,
                        'date': datetime.now()
                    })
                    st.success("Expenditure recorded!")
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
                    # Check if product already exists
                    existing_product = next((p for p in st.session_state.stock if p['name'].lower() == product_name.lower()), None)
                    if existing_product:
                        # Update existing product
                        existing_product['buy_price'] = (existing_product['buy_price'] * existing_product['qty'] + buy_price * quantity) / (existing_product['qty'] + quantity) # Average buy price
                        existing_product['sell_price'] = sell_price # Update sell price
                        existing_product['qty'] += quantity
                        st.success(f"Stock for '{product_name}' updated!")
                    else:
                        # Add new product
                        st.session_state.stock.append({
                            "name": product_name,
                            "buy_price": buy_price,
                            "sell_price": sell_price,
                            "qty": quantity
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
            if 'bill_products' not in st.session_state:
                st.session_state.bill_products = []

            # Function to add a product to the current bill
            def add_product_to_bill():
                product_name = st.session_state['bill_product_name']
                quantity = st.session_state['bill_product_qty']
                product_details = next((p for p in st.session_state.stock if p['name'] == product_name), None)
                if product_details:
                    st.session_state.bill_products.append({
                        "name": product_name,
                        "quantity": quantity,
                        "price": product_details['sell_price']
                    })
            
            # Product selection UI
            bill_col1, bill_col2, bill_col3 = st.columns([3,1,1])
            with bill_col1:
                product_names = [p['name'] for p in st.session_state.stock]
                st.selectbox("Select Product", options=product_names, key='bill_product_name')
            with bill_col2:
                st.number_input("Quantity", min_value=1, step=1, key='bill_product_qty')
            with bill_col3:
                st.write("") # for alignment
                st.button("Add Product", on_click=add_product_to_bill)
            
            if st.session_state.bill_products:
                st.write("Products in current bill:")
                temp_bill_df = pd.DataFrame(st.session_state.bill_products)
                st.dataframe(temp_bill_df, use_container_width=True)

            submitted = st.form_submit_button("Confirm and Generate Bill")
            if submitted:
                if customer_name and st.session_state.bill_products:
                    bill_data = {
                        'business_name': st.session_state.user_data.get("business_name"),
                        'customer_name': customer_name,
                        'customer_contact': customer_contact,
                        'selling_date': str(selling_date),
                        'products': st.session_state.bill_products,
                        'bill_id': f"BILL-{len(st.session_state.bills) + 1}-{datetime.now().strftime('%Y%m%d')}"
                    }
                    st.session_state.bills.append(bill_data)
                    st.session_state.bill_products = [] # Clear for next bill
                    st.success("Bill generated successfully!")

                    # PDF Download
                    pdf_data = generate_bill_pdf(bill_data)
                    st.markdown(create_download_link(pdf_data, bill_data['bill_id']), unsafe_allow_html=True)
                    st.rerun()

                else:
                    st.error("Please enter customer name and add at least one product.")
    
    st.markdown("---")
    st.subheader("Bill History")
    if not st.session_state.bills:
        st.info("No bills generated yet.")
    else:
        for bill in reversed(st.session_state.bills):
            with st.container(border=True):
                st.write(f"**Bill ID:** {bill['bill_id']}")
                st.write(f"**Customer:** {bill['customer_name']}")
                st.write(f"**Date:** {bill['selling_date']}")
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

    # Most Selling Product
    most_selling_product = sales_df.groupby('name')['qty'].sum().idxmax()
    most_selling_qty = sales_df.groupby('name')['qty'].sum().max()

    # Least Selling Product
    least_selling_product = sales_df.groupby('name')['qty'].sum().idxmin()
    least_selling_qty = sales_df.groupby('name')['qty'].sum().min()

    # Most Profitable Product
    most_profitable_product = sales_df.groupby('name')['profit'].sum().idxmax()
    most_profit_amount = sales_df.groupby('name')['profit'].sum().max()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.subheader("Most Selling Product")
        st.info(f"**{most_selling_product}** ({most_selling_qty} units)")
    with col2:
        st.subheader("Least Selling Product")
        st.info(f"**{least_selling_product}** ({least_selling_qty} units)")
    with col3:
        st.subheader("Most Profitable Product")
        st.info(f"**{most_profitable_product}** (Profit: ₹{most_profit_amount:,.2f})")

    st.markdown("---")

    # Sales over time
    st.subheader("Daily Sales Performance")
    daily_sales = sales_df.groupby('date')['total_sale'].sum()
    st.bar_chart(daily_sales)

    st.subheader("All Sales Data")
    st.dataframe(sales_df, use_container_width=True)


# 6. About Page
def about_page():
    st.title("About")
    st.header("About Sellsathi")
    st.write("""
    Sellsathi is a simple and intuitive application designed to help small business owners manage their sales, stock, and billing with ease. 
    It provides a clear dashboard with key metrics, a straightforward stock management system, and quick bill generation. 
    The business analysis section helps you understand your performance and make better decisions.
    """)

    st.header("About Your Business")
    user_data = st.session_state.user_data
    st.write(f"**Business Name:** {user_data.get('business_name')}")
    st.write(f"**Owner Name:** {user_data.get('name')}")
    st.write(f"**Contact Email:** {user_data.get('email')}")
    st.write(f"**Business Type:** {user_data.get('business_type')}")


# --- MAIN APP ROUTING ---
if not st.session_state.logged_in:
    register_page()
else:
    # Sidebar Navigation
    with st.sidebar:
        st.header("Sellsathi")
        st.session_state.page = st.radio(
            "Navigation",
            ["Dashboard", "Stock", "Bill", "Business Analysis", "About"],
            label_visibility="hidden"
        )
    
    # Page Display
    if st.session_state.page == "Dashboard":
        dashboard_page()
    elif st.session_state.page == "Stock":
        stock_page()
    elif st.session_state.page == "Bill":
        bill_page()
    elif st.session_state.page == "Business Analysis":
        analysis_page()
    elif st.session_state.page == "About":
        about_page()
