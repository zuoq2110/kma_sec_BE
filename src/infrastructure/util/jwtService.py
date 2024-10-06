
from fastapi import Request,HTTPException

import jwt
from src.data.local.source.user import SECRET_KEY,ALGORITHM,oauth2_scheme

async def get_token(request: Request):
    token = request.headers.get("Authorization")
    if token and token.startswith("Bearer "):
        return token[7:]  # Trả về token mà không có "Bearer "
    return None  # Nếu không có token, trả về None

def decode_token( token: str):
        try:
            # Giải mã token
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except jwt.PyJWTError:
            raise HTTPException(status_code=403, detail="Invalid token")