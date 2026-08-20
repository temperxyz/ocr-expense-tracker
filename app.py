import streamlit as st
import os 
os.makedirs("uploads",exist_ok=True)
from preprocess import find_receipt_corners,order_points,warp_receipt,binarize
from datetime import date as dt_date
from ocr_raw import extract_text_from_receipt
from parser import parse_receipt
from categorize import categorize_expense,CATEGORIES
from db import init_db,insert_expense,get_all_expenses,get_expenses_by_category,get_expenses_by_date_range,delete_expense,update_expense
from dashboard import show_dashboard

st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["ShowDashboard","Add Receipt", "View All Expenses", "Monthly View", "Update / Delete"])
if page=="ShowDashboard":
    show_dashboard()
elif page == "Add Receipt":
    st.title("OCR Expense Tracker")
    init_db()

    uploaded_file=st.file_uploader("Upload a receipt  (jpg)",type="jpg")
    if uploaded_file is not None:
        image_path=f"uploads/{uploaded_file.name}"
        with open(image_path,"wb") as f:
            f.write(uploaded_file.getbuffer())
        st.image(image_path,caption="Uploaded receipt")

        st.write("Preprocessing...")

        raw_text,source_label=extract_text_from_receipt(image_path)#Returning the best text and type of preprocessing 
        parsed=parse_receipt(raw_text)#Extracts date and total from the receipt(merchant,date,total,rawtext)
        date=parsed["date"]
        total=parsed["total"]
        st.subheader("Verify Details")
        merchant_input=st.text_input("Merchant name",value="")

        if date is None:
            st.write("No date found, renter it!")
        date_default=date if date is not None else ""
        date_input=st.text_input("Date",value=date_default)# Gives Default value of date which is parsed by ocr
        if total is None:
            st.write("No total Found, Renter it!")
        total_default=float(total) if total is not None else 0.0
        total_input=st.number_input("Total",value=total_default)

        status,category,confidence=categorize_expense(merchant_input)
        st.write(f"Predicted Category {category} ({status},confidence={confidence:.2f})")

        category_input=st.selectbox(
            "Category (edit if wrong)",
            options=CATEGORIES,
            index= CATEGORIES.index(category)
        )

        if st.button("Save expenses"):
            success=insert_expense(merchant_input,date_input,total_input,category_input,raw_text,image_path)#merchant, date, total, category, raw_text, image_path
            if success:
                st.success("Expense Saved!")
            else:
                st.error("Failed to saved, duplicate image may exist?")

elif page == "View All Expenses":
        rows=get_all_expenses()
        if not rows:
            st.write("No expenses recorded yet.")
        else:
            data = [dict(row) for row in rows]#Converting each sqlite row into plain dict
            st.dataframe(data)
elif page == "Monthly View":
    st.subheader("Expenses By date Range")
    col1,col2=st.columns(2)
    with col1:
        start_input=st.date_input("From",value=dt_date.today().replace(day= 1))
    with col2:
        end_input=st.date_input("End",value=dt_date.today())
    rows=get_expenses_by_date_range(start_input.isoformat(),end_input.isoformat())# Montly expenses from start of the month to end
    if not rows:
        st.write("No expenses found in this month")
    else:
        data=[dict(row) for row in rows]
        st.dataframe(data)
elif page == "Update / Delete":
    st.subheader("Update/Delete Expense")
    rows=get_all_expenses()
    if not rows:
        st.write("No expense to edit")
    else:
        data=[dict(row) for row in rows]
        options = {f"#{d['expense_id']}-{d['merchant']}-{d['total']}-{d['date']}": d for d in data}
        selected_label=st.selectbox("Choose and expense",options=list(options.keys()))
        selected=options[selected_label]

        merchant_edit=st.text_input("Merchant name",value=selected['merchant'])
        date_edit = st.text_input("Date", value=selected['date'])
        total_edit = st.number_input("Total", value=selected['total'])
        category_edit = st.selectbox("Category", options=CATEGORIES, index=CATEGORIES.index(selected['category']))
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Update"):
                update_expense(selected['expense_id'],merchant_edit,date_edit,total_edit,category_edit,selected['raw_text'],selected['image_path'])  # what args, in what order? check db.py
                st.success("Updated!")
        with col2:
            if st.button("Delete"):
                delete_expense(selected['expense_id'])
                st.warning("Deleted!")