# =============================================================================
# CURRENCY CONVERSION
# =============================================================================

# Third-Party Imports
import forex_python.converter  # Currency conversion for superchat values

# =============================================================================

def convert_to_usd(value: float = 1, currency_name: str = "USD") -> float:
    """
    Convert currency value to USD.
    
    Args:
        value: Amount to convert
        currency_name: Source currency code
        
    Returns:
        float: Value in USD
    """
    converter = forex_python.converter.CurrencyRates()
    usd_value = converter.convert(currency_name, 'USD', value)
    return usd_value