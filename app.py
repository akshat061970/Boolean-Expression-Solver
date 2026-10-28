import streamlit as st
import sympy
from sympy.logic.boolalg import simplify_logic
import re

# Set up the page layout and title
st.set_page_config(page_title="Boolean Simplifier", layout="centered")
st.title("Boolean Expression Simplifier")
st.write("Build or type a boolean expression, and we will simplify it for you!")

# --- 1. Variables Setup ---
# Dropdown to select the number of variables (max 10)
num_vars = st.selectbox("Choose Number of Variables", list(range(1, 11)), index=3)

# Generate variables (A, B, C, D, etc. up to 10 variables)
variables = [chr(65 + i) for i in range(num_vars)]

# --- 2. State Management ---
# Initialize the session state for the expression if it doesn't exist
if "expr" not in st.session_state:
    st.session_state.expr = ""

# Callback function to append clicked button values to the text box
def append_to_expr(val):
    st.session_state.expr += val

# Callback function to clear the text box
def clear_expr():
    st.session_state.expr = ""

# --- 3. User Interface: Buttons ---
st.markdown("### Variables")
# Dynamically generate buttons for the chosen number of variables
var_cols = st.columns(num_vars)
for i, var in enumerate(variables):
    with var_cols[i]:
        st.button(var, on_click=append_to_expr, args=(var,), use_container_width=True)

st.markdown("### Operators")
# Predefined operators 
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

# --- 4. Expression Input & Display ---
# The text input is directly tied to the session state via the key="expr"
st.text_input("Current Boolean Expression:", key="expr", placeholder="e.g., A * B + (C ')")

col1, col2 = st.columns([1, 5])
with col1:
    st.button("Clear", on_click=clear_expr, type="secondary")
with col2:
    enter_clicked = st.button("Enter / Simplify", type="primary", use_container_width=True)

# --- 5. Backend Processing & Simplification ---
# --- 5. Backend Processing & Simplification ---
if enter_clicked:
    raw_expr = st.session_state.expr.strip()
    
    if not raw_expr:
        st.warning("Please enter a boolean expression before clicking Enter.")
    else:
        try:
            # 1. Convert B' to ~B (also handles accidental spaces like B ')
            processed_expr = re.sub(r"([A-Z])\s*'", r"~\1", raw_expr.upper())
            
            # 2. MAGIC STEP: Automatically insert '*' for implicit ANDs
            processed_expr = re.sub(r"([A-Z)])\s*(?=[A-Z(~])", r"\1 * ", processed_expr)
            
            # 3. Prepare the remaining string for SymPy
            processed_expr = processed_expr.replace('*', '&').replace('+', '|')
            
            # 4. Force SymPy to treat A, B, C, D, E, I etc. as standard variables
            local_dict = {var: sympy.Symbol(var) for var in variables}
            
            # 5. Convert the string to a SymPy expression safely 
            parsed_expr = sympy.sympify(processed_expr, locals=local_dict)
            
            # 6. Simplify the logic (Removed form='dnf' to force maximum simplification)
            simplified = simplify_logic(parsed_expr)
            
            # 7. Convert back to user-friendly string format
            final_output = str(simplified)
            
            # Catch absolute truths and falsehoods (A * A' = 0, A + A' = 1)
            if final_output == "False":
                final_output = "0 (Always False)"
            elif final_output == "True":
                final_output = "1 (Always True)"
            else:
                # Format standard expressions normally
                final_output = final_output.replace('&', '*').replace('|', '+')
                final_output = re.sub(r"~([A-Z])", r"\1'", final_output)
            
            st.success("### Simplified Expression:")
            st.code(final_output, language="text")
            
        except Exception as e:
            # Display the exact error message to help debug
            st.error(f"⚠️ Invalid input! Error details: {e}")
