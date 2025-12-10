from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import logging
import json
import time
import uuid
from contextvars import ContextVar, copy_context
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Define a ContextVar for request_id
request_id_var: ContextVar[Optional[str]] = ContextVar("request_id", default=None)

# Configure structured logging
class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "message": record.getMessage(),
            "name": record.name,
            "pathname": record.pathname,
            "lineno": record.lineno,
        }
        current_request_id = request_id_var.get()
        if current_request_id:
            log_record['request_id'] = current_request_id
        if record.exc_info:
            log_record['exc_info'] = self.formatException(record.exc_info)
        return json.dumps(log_record)

handler = logging.StreamHandler()
handler.setFormatter(JsonFormatter())
logger = logging.getLogger("uvicorn")
logger.setLevel(logging.INFO)
logger.addHandler(handler)

# Add CORS middleware
origins = [
    "http://localhost:3000",  # Frontend URL
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    request_id = str(uuid.uuid4()) # Generate a unique request ID
    
    # Set request_id in ContextVar for the duration of this request
    token = request_id_var.set(request_id)
    
    try:
        logger.info(f"Request started: {request.method} {request.url}")
        
        response = await call_next(request)
        
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        
        logger.info(f"Request finished: {request.method} {request.url} - Status: {response.status_code} - Time: {process_time:.4f}s")
        
        return response
    finally:
        # Reset ContextVar
        request_id_var.reset(token)

@app.get("/")
def read_root():
    logger.info("Root endpoint accessed.")
    return {"Hello": "World"}
