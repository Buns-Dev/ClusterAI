# advanced_math.py - Full Symbolic Mathematics Engine
import sympy as sp
import re

def clean_expression(raw_expr):
    """Standardizes spoken math and symbols into Python-readable math notation."""
    expr_str = raw_expr.replace('^', '**')
    expr_str = expr_str.replace(' cube', '**3').replace(' square', '**2')
    # Convert implicit multiplication (e.g., "2x" to "2*x")
    expr_str = re.sub(r'(\d)([a-zA-Z])', r'\1*\2', expr_str)
    return expr_str.strip()

def process_math_query(query):
    """Routes and evaluates natural language mathematical problems symbolically."""
    clean_query = query.lower().strip()
    x = sp.Symbol('x')
    
    # 1. DEFINITE INTEGRALS (e.g., "integrate x^2 from 0 to 3")
    if "integrate" in clean_query and "from" in clean_query:
        try:
            match = re.search(r'integrate (.*) from ([-.\d]+) to ([-.\d]+)', clean_query)
            if match:
                raw_expr = match.group(1).strip()
                expr_str = clean_expression(raw_expr)
                lower_limit = float(match.group(2))
                upper_limit = float(match.group(3))
                
                expr = sp.sympify(expr_str)
                result = sp.integrate(expr, (x, lower_limit, upper_limit))
                if float(result).is_integer(): result = int(result)
                
                return {
                    "ui": f"🧮 CALCULUS MATRIX :: DEFINITE INTEGRATION\n"
                          f"———————————————————————————————————————————————————————\n"
                          f" 📊 FUNCTION  :: ∫ ({raw_expr}) dx\n"
                          f" 📉 LIMITS    :: {lower_limit} to {upper_limit}\n"
                          f" 🎯 EVALUATION:: {result}\n"
                          f"———————————————————————————————————————————————————————\n"
                          f"📡 Core integration verification sequence absolute.",
                    "voice": f"The definite integral evaluates exactly to {result}."
                }
        except Exception as e:
            return {"ui": f"⚠️ Integration Failure: {e}", "voice": "Failed to resolve integral bounds."}

    # 2. DERIVATIVES (e.g., "derivative of x^3 + 5x")
    elif "differentiate" in clean_query or "derivative" in clean_query:
        try:
            raw_expr = clean_query.replace("differentiate", "").replace("derivative of", "").strip()
            expr_str = clean_expression(raw_expr)
            
            expr = sp.sympify(expr_str)
            result = sp.diff(expr, x)
            clean_result = str(result).replace('**', '^').replace('*', '')
            
            return {
                "ui": f"📉 CALCULUS MATRIX :: SYMBOLIC DERIVATIVE\n"
                      f"———————————————————————————————————————————————————————\n"
                      f" 📊 FUNCTION   :: d/dx ({raw_expr})\n"
                      f" 🎯 DERIVATIVE :: {clean_result}\n"
                      f"———————————————————————————————————————————————————————\n"
                      f"📡 Derivative computation complete.",
                "voice": f"The derivative is {clean_result}."
            }
        except Exception as e:
            return {"ui": f"⚠️ Differentiation Failure: {e}", "voice": "Failed to differentiate function."}

    # 3. ALGEBRAIC EQUATION SOLVING (e.g., "solve x^2 - 9")
    elif "solve" in clean_query:
        try:
            raw_eq = clean_query.replace("solve", "").strip()
            if "=" in raw_eq:
                parts = raw_eq.split("=")
                eq_str = f"({clean_expression(parts[0])}) - ({clean_expression(parts[1])})"
            else:
                eq_str = clean_expression(raw_eq)
                
            expr = sp.sympify(eq_str)
            solutions = sp.solve(expr, x)
            
            return {
                "ui": f"🧩 ALGEBRAIC MATRIX :: EQUATION SOLVER\n"
                      f"———————————————————————————————————————————————————————\n"
                      f" 📊 EQUATION :: {raw_eq} = 0\n"
                      f" 🎯 ROOT SET :: x = {solutions}\n"
                      f"———————————————————————————————————————————————————————\n"
                      f"📡 Matrix equations resolved successfully.",
                "voice": f"The solutions for x are {solutions}."
            }
        except Exception as e:
            return {"ui": f"⚠️ Equation Failure: {e}", "voice": "Unable to solve equation variables."}

    # 4. EXPRESSION SIMPLIFICATION (e.g., "simplify (x^2 - 1) / (x - 1)")
    elif "simplify" in clean_query:
        try:
            raw_expr = clean_query.replace("simplify", "").strip()
            expr_str = clean_expression(raw_expr)
            
            expr = sp.sympify(expr_str)
            result = sp.simplify(expr)
            clean_result = str(result).replace('**', '^').replace('*', '')
            
            return {
                "ui": f"🧪 REDUCTION MATRIX :: EXPRESSION SIMPLIFIER\n"
                      f"———————————————————————————————————————————————————————\n"
                      f" 📊 ORIGINAL   :: {raw_expr}\n"
                      f" 🎯 SIMPLIFIED :: {clean_result}\n"
                      f"———————————————————————————————————————————————————————\n"
                      f"📡 Expression compressed to lowest terms.",
                "voice": f"The simplified expression is {clean_result}."
            }
        except Exception as e:
            return {"ui": f"⚠️ Simplification Failure: {e}", "voice": "Could not reduce expression terms."}

    return None