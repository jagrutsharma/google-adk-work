from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.genai import types
from google.adk.code_executors import BuiltInCodeExecutor
from google.adk.tools import AgentTool

# =============================================================================
# Day 2A: Agent Tools - Currency Converter
# =============================================================================

# Configure retry options for reliability (exponential backoff)
retry_config = types.HttpRetryOptions(
    attempts=5,
    exp_base=7,
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504]
)


# =============================================================================
# Custom Function Tool 1: Fee Lookup
# Note that return value is a dictionary
# Document the method well
# =============================================================================
def get_fee_for_payment_method(method: str) -> dict:
    """
    Looks up the transaction fee percentage for a given payment method.

    This tool simulates looking up a company's internal fee structure based on
    the name of the payment method provided by the user.

    Args:
        method: The name of the payment method. It should be descriptive,
                e.g., "platinum credit card" or "bank transfer".

    Returns:
        Dictionary with status and fee information.
        Success: {"status": "success", "fee_percentage": 0.02}
        Error: {"status": "error", "error_message": "Payment method not found"}
    """
    # Simulates company's internal fee structure
    fee_database = {
        "platinum credit card": 0.02,    # 2%
        "gold debit card": 0.035,        # 3.5%
        "bank transfer": 0.01,           # 1%
    }

    fee = fee_database.get(method.lower())
    if fee is not None:
        return {
                "status": "success",
                "fee_percentage": fee
            }
    else:
        return {
            "status": "error",
            "error_message": "Payment method not found"
            }

# =============================================================================
# Custom Function Tool 2: Exchange Rate
# Note that return value is a dictionary
# Document the method well
# =============================================================================

def get_exchange_rate(base_currency: str, target_currency: str) -> dict:
    """
    Looks up and returns the exchange rate between two currencies.

    Args:
        base_currency: The ISO 4217 currenc code of the currency
        you are converting from (e.g., "USD")

        target_currency: The ISO 4217 currency code of the currency
        you are converting to (e.g., "EUR")

    Returns:
        Dictionary with status and rate information.
        Success: {"status": "success", "rate": 0.93}
        Error: {"status": "error", "error_message": "Unsupported currency pair"}
    """
    # Static data simulating a live exchange rate API
    rate_database = {
        "usd": {
            "eur": 0.93,        # Euro
            "jpy": 157.50,      # Japanese Yen
            "inr": 83.58        # Indian Rupee
        }
    }

    # Input validation and processing
    base = base_currency.lower()
    target = target_currency.lower()

    # Return structured result with status
    rate = rate_database.get(base, {}).get(target)
    if rate is not None:
        return {"status": "success", "rate": rate}
    else:
        return {"status": "error", "error_message": f"Unsupported currency pair {base_currency}/{target_currency}"}


# =============================================================================
# Basic Currency Agent with Function Tools
# Note that this may give answers that may be mathematically a bit off
# =============================================================================
currency_agent = LlmAgent(
    name="currency_agent",
    model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
    instruction="""
        You are a smart currency conversion assistant.
        
        For currency conversion requests:
        1. Use `get_fee_for_payment_method()` to find transaction fees
        2. Use `get_exchange_rate()` to get currency conversion rates
        3. Check the "status" field in each tool's response for errors
        4. Calculate the final amount after fees and provide a clear breakdown
        5. First, state the final converted amount. Then, explain how you got that result.
        
        If any tool returns status "error", explain the issue to the user clearly.
    """,
    tools=[get_fee_for_payment_method, get_exchange_rate]
)

# =============================================================================
# Enhanced Version: Add Code Execution for Reliable Math
# =============================================================================

# Calculation Agent: Generates and executes Python code
# This agent will be used by another agent (enhanced_currency_agent) as a tool
# When code_executor=BuiltInCodeExecutor() is set:
#   - ADK automatically detects code blocks in the LLM's response
#   - It extracts the Python code
#   - It executes it in a sandbox
#   - It returns the execution result back to the agent

# Side Note: The tool_code prefix is ADK's way of marking this as generated code.
# Via WebUI, this is the code generated and executed by the CalculationAgent
# "tool_code initial_amount_usd = 100 fee_percentage = 0.01 exchange_rate = 83.58 fee_amount_usd = initial_amount_usd * fee_percentage amount_after_fee_usd =
# initial_amount_usd - fee_amount_usd final_amount_inr = amount_after_fee_usd * exchange_rate print(f'{final_amount_inr=}') "
calculation_agent = LlmAgent(
    name="CalculationAgent",
    model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
    instruction="""
    You are a specialized calculator that ONLY responds with Python ocde.
    Your task is to take a request for a calculation and translate it into Python code.
    
    RULES:
    1. Your output MUST be ONLY a Python code block
    2. Do NOT write any text before or after the code block
    3. The Python code MUST calculate a result
    4. The Python code MUST print the final result to stdout
    5. You are PROHIBITED from doing the calculation yourself
    
    Failure to follow these rules will result in an error.
    """,
    code_executor=BuiltInCodeExecutor()
)

# Enhanced Currency Agent
enhanced_currency_agent = LlmAgent(
    name="enhanced_currency_agent",
    model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
    instruction="""
    You are a smart currency conversion assistant.
    You must strictly follow these steps and use the available tools.
    
    For any currency conversion request:
    1. Get Transaction Fee: Use get_fee_for_payment_method() to get the fee.
    2. Get Exchange Rate: Use get_exchange_rate(0 to get the conversion rate
    3. Error Check: After each tool call, check the "status" field.
    If status is "error", stop and explain the issue
    4. Calculate Final Amount (CRITICAL): You are PROHIBITED from doing the math yourself.
    You MUST use the CalculationAgent tool to generate Python code that calculates 
    the final converted amount using the fee and exchange rate
    5. Provide Breakdown: State the final amount and explain:
    - The fee percentage and fee amount in original currency
    - The amount remaining after the fee
    - The exchange rate applied
    
    If any tool returns status "error", explain the issue clearly.
    """,
    tools = [
        get_fee_for_payment_method,
        get_exchange_rate,
        AgentTool(agent=calculation_agent)      # Using another agent as tool, control still remain with enhanced currency agent
    ]
)

# root_agent = currency_agent
root_agent = enhanced_currency_agent