from pydantic import BaseModel, Field



class WeekDays(BaseModel):
    Saturday: int
    Sunday: int
    Monday: int
    Tuesday: int
    Wednesday: int
    Thursday: int
    Friday: int



class MahexShipment(BaseModel):
    stock_id: str = Field(..., alias="stockId")
    full_address: str = Field(..., alias="fullAddress")
    customer_id: str = Field(..., alias="cusromerId")
    city_id: str = Field(..., alias="city_id")
    phone_number: str = Field(..., alias="phone_number")
    customer_first_name: str = Field(..., alias="customer_first_name")
    customer_last_name: str = Field(..., alias="customer_last_name")
    count: int = Field(...)
    coverage_price: int = Field(..., alias="coveragePrice")
    products: str = Field(..., description="products name separated by -")
    order_number: str = Field(..., alias="orderId")
