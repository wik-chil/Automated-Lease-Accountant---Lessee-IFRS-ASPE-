from dataclasses import dataclass
from typing import Optional


@dataclass()
class JournalEntry:
    """Class for creating accounting journal entries with consistent structure."""
    date: str
    debit_account: str
    credit_account: str
    amount: float
    description: str

    def print_entry(self):
        """Print the journal entry in a clear format."""
        print(f"{self.date}\n"
              f"Dr {self.debit_account}   {self.amount}\n"
              f"   Cr {self.credit_account}   {self.amount}\n"
              f"{self.description}")

@dataclass()
class LeaseInputs:
    """Class containing all the necessary information of a lease, for accounting purposes."""
    standard: str                                   # IFRS / ASPE
    role: str                                       # Lessee / Lessor
    lease_term_years: float                         # No. years the lease will last
    lease_pmt: float                                # Payment AMOUNT for lease
    payments_per_year: int                          # Amount of payments per year
    asset_fair_value: float
    asset_economic_life: float                      # No. useful years for asset
    implicit_rate: Optional[float]                  # float or None
    incremental_borrowing_rate: float
    ownership_transfer: bool                        # If transfer of ownership is true, bpo must not be None
    bargain_purchase_option: Optional[float]        # float or None
    guaranteed_residual_value: Optional[float]
    unguaranteed_residual_value: Optional[float]
