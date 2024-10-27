from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
import shutil

app = FastAPI()

@app.post("/upload-audio")
async def upload_audio(audio: UploadFile = File(...)):
    print(audio.filename)
    file_location = f"uploaded_audio/{audio.filename}"
    
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(audio.file, buffer)
    return JSONResponse(content={"message": "Audio uploaded successfully", "filename": audio.filename})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8502)
