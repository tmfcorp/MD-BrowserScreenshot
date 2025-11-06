import os
import uuid
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from playwright.async_api import async_playwright

app = FastAPI()

os.makedirs("screenshots", exist_ok=True)

class ScreenshotRequest(BaseModel):
    html: str = None
    url: str = None

async def renderHtml(code: str = None, url: str = None) -> str:
    if not code and not url:
        raise ValueError("html or url is required")
        
    filename = f"screenshots/{uuid.uuid4()}.png"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            if url:
                await page.goto(url)
            else:
                await page.set_content(code)
            
            await page.set_viewport_size({"width": 1280, "height": 720})
            
            await page.screenshot(path=filename, full_page=True)
            return filename
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            await browser.close()

@app.post("/screenshot")
async def takeScreenshot(request: ScreenshotRequest):
    try:
        screenshot_path = await renderHtml(code=request.html, url=request.url)
        return FileResponse(screenshot_path, media_type="image/png")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
