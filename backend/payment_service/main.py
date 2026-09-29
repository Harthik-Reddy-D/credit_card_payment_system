from fastapi import FastAPI
from pydantic import BaseModel, Field
import random
app=FastAPI(title='Payment Simulation Service',version='1.0.0')
class Payment(BaseModel):
    amount: float=Field(gt=0)
    reference: str
@app.get('/health')
def health(): return {'status':'ok'}
@app.post('/simulate-payment')
def simulate(p:Payment):
    success=random.random() < 0.8
    return {'reference':p.reference,'status':'SUCCESS' if success else 'FAILED','reason':'' if success else 'Simulated payment failure'}
