from decimal import Decimal
from typing import Annotated

from pydantic import PlainSerializer

# Money is sent to the frontend as a string with 2 decimals, e.g. "249.00" (no float rounding problems).
Money = Annotated[Decimal, PlainSerializer(lambda v: f"{v:.2f}", return_type=str, when_used="json")]
