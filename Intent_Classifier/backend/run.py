import uvicorn
import nest_asyncio

# Apply nest_asyncio to allow nested event loops (useful for Jupyter notebooks)
nest_asyncio.apply()

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True) 