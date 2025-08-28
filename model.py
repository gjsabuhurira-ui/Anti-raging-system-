class ComplaintForm(BaseModel):
    register_number: str = Field(..., min_length=6, description="Student's register number.")
    complaint_text: str = Field(..., min_length=10, description="Details of the complaint.")