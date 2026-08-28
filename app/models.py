from dataclasses import dataclass
from typing import Optional
from datetime import date, datetime

@dataclass
class Booker:
    id: int
    name: str
    is_active: bool
    created_at: str

@dataclass
class Area:
    id: int
    name: str

@dataclass
class City:
    id: int
    name: str

@dataclass
class Customer:
    id: int
    name: str
    area_id: Optional[int]
    city_id: Optional[int]
    booker_id: Optional[int]
    opening_date: Optional[str]
    opening_balance: int # in paisa
    last_order_date: Optional[str]
    is_active: bool
    created_at: str
    updated_at: str

@dataclass
class Transaction:
    id: int
    customer_id: int
    booker_id: int
    type: str # 'Bill' or 'Recovery'
    amount: int # in paisa
    transaction_date: str
    notes: Optional[str]
    created_at: str
    updated_at: str
