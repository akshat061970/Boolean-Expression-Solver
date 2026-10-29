import streamlit as st
import sympy
from sympy.logic.boolalg import simplify_logic
import re


st.set_page_config(page_title="Boolean Simplifier", layout="centered")
st.title("Boolean Expression Simplifier")
st.write("Build or type a boolean expression, and we will simplify it for you!")



num_vars = st.selectbox("Choose Number of Variables", list(range(1, 11)), index=3)


variables = [chr(65 + i) for i in range(num_vars)]


if "expr" not in st.session_state:
    st.session_state.expr = ""


def append_to_expr(val):
    st.session_state.expr += val


def clear_expr():
    st.session_state.expr = ""


st.markdown("### Variables")

var_cols = st.columns(num_vars)
for i, var in enumerate(variables):
    with var_cols[i]:
        st.button(var, on_click=append_to_expr, args=(var,), use_container_width=True)

st.markdown("### Operators")
 
operators = [
    ("AND (*)", "*"), 
    ("OR (+)", "+"), 
    ("NOT (')", "'"), 
    ("XOR (^)", "^"), 
    ("(", "("), 
    (")", ")")
]

op_cols = st.columns(len(operators))
for i, (label, val) in enumerate(operators):
    with op_cols[i]:
        st.button(label, on_click=append_to_expr, args=(val,), use_container_width=True)


st.text_input("Current Boolean Expression:", key="expr", placeholder="e.g., A * B + (C ')")

col1, col2 = st.columns([1, 5])
with col1:
    st.button("Clear", on_click=clear_expr, type="secondary")
with col2:
    enter_clicked = st.button("Enter / Simplify", type="primary", use_container_width=True)


if enter_clicked:
    raw_expr = st.session_state.expr.strip()
    
    if not raw_expr:
        st.warning("Please enter a boolean expression before clicking Enter.")
    else:
        try:
            
            processed_expr = re.sub(r"([A-Z])\s*'", r"~\1", raw_expr.upper())
            
            
            processed_expr = re.sub(r"([A-Z)])\s*(?=[A-Z(~])", r"\1 * ", processed_expr)
            
            
            processed_expr = processed_expr.replace('*', '&').replace('+', '|')
            
            
            local_dict = {var: sympy.Symbol(var) for var in variables}
            
            
            parsed_expr = sympy.sympify(processed_expr, locals=local_dict)
            
            
            simplified = simplify_logic(parsed_expr)
            
            
            final_output = str(simplified)
            
            
            if final_output == "False":
                final_output = "0 (Always False)"
            elif final_output == "True":
                final_output = "1 (Always True)"
            else:
                
                final_output = final_output.replace('&', '*').replace('|', '+')
                final_output = re.sub(r"~([A-Z])", r"\1'", final_output)
            
            st.success("### Simplified Expression:")
            st.code(final_output, language="text")
            
        except Exception as e:
            
            st.error(f"⚠️ Invalid input! Error details: {e}")
