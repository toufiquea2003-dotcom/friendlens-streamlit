from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, status, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
import pandas as pd, io, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from recommender import get_recommendations
from visualization import create_visualizations
from hobby_recommender import recommend_hobbies

app = FastAPI(title="FriendLens API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

# For production deployment, you might want to change this to 0.0.0.0
HOST = "0.0.0.0"
PORT = 8000

security = HTTPBasic()

# Simple user store
USERS = {
    "FriendLens1": "12345678"
}

DATA_DF = None
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")

def authenticate(credentials: HTTPBasicCredentials = Depends(security)):
    username = credentials.username
    password = credentials.password
    if username not in USERS or USERS[username] != password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return username

@app.post("/api/upload")
async def upload_csv(file: UploadFile = File(...), user: str = Depends(authenticate)):
    global DATA_DF
    contents = await file.read()
    try:
        DATA_DF = pd.read_csv(io.BytesIO(contents))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not read CSV: {e}")
    # save a copy
    path = os.path.join(UPLOAD_DIR, file.filename)
    with open(path, "wb") as f:
        f.write(contents)
    return {"filename": file.filename, "rows": DATA_DF.shape[0], "cols": DATA_DF.shape[1], "columns": list(DATA_DF.columns)}

@app.get("/api/health")
def health(user: str = Depends(authenticate)):
    return {"status": "authenticated"}

@app.get("/api/preview")
def preview(n: int = 10, user: str = Depends(authenticate)):
    if DATA_DF is None:
        raise HTTPException(404, "No data loaded. Upload CSV first.")
    return {"head": DATA_DF.head(n).to_dict(orient="records")}

@app.get("/api/summary")
def summary(user: str = Depends(authenticate)):
    if DATA_DF is None:
        raise HTTPException(404, "No data loaded. Upload CSV first.")
    df = DATA_DF
    return {
        "shape": df.shape,
        "dtypes": {c: str(t) for c,t in df.dtypes.items()},
        "missing": df.isnull().sum().to_dict(),
        "unique_counts": df.nunique().to_dict()
    }

@app.get("/api/recommend/{user_id}")
def recommend(user_id: str, top_k: int = 5, user: str = Depends(authenticate)):
    if DATA_DF is None:
        raise HTTPException(404, "No data loaded. Upload CSV first.")
    recs = get_recommendations(DATA_DF, user_id, top_k=top_k)
    return {"user": user_id, "recommendations": recs}

@app.get("/api/recommend_hobbies/{user_id}")
def recommend_hobbies_endpoint(user_id: str, top_k: int = 5, user: str = Depends(authenticate)):
    if DATA_DF is None:
        raise HTTPException(404, "No data loaded. Upload CSV first.")
    recs = recommend_hobbies(DATA_DF, user_id, top_k=top_k)
    return {"user": user_id, "hobby_club_recommendations": recs}

@app.get("/api/visualize")
def visualize(user: str = Depends(authenticate)):
    if DATA_DF is None:
        raise HTTPException(404, "No data loaded. Upload CSV first.")
    path = create_visualizations(DATA_DF)
    return {"chart_path": path}

@app.post("/api/analyze")
async def analyze_data(task: str = Form(...), user: str = Depends(authenticate)):
    if DATA_DF is None:
        raise HTTPException(404, "No data loaded. Upload CSV first.")

    task_lower = task.lower().strip()

    if "summary" in task_lower or "describe" in task_lower:
        result = {
            "task": task,
            "result": {
                "shape": DATA_DF.shape,
                "columns": list(DATA_DF.columns),
                "dtypes": {col: str(dtype) for col, dtype in DATA_DF.dtypes.items()},
                "missing_values": DATA_DF.isnull().sum().to_dict(),
                "unique_counts": DATA_DF.nunique().to_dict(),
                "sample_data": DATA_DF.head(5).to_dict(orient="records")
            }
        }
    elif "recommend" in task_lower and "friend" in task_lower:
        # Extract user from task if mentioned
        import re
        user_match = re.search(r'for\s+(\w+)', task_lower)
        target_user = user_match.group(1) if user_match else DATA_DF['User'].iloc[0] if 'User' in DATA_DF.columns else None

        if target_user and 'User' in DATA_DF.columns and 'Friend' in DATA_DF.columns:
            from recommender import get_recommendations
            recs = get_recommendations(DATA_DF, target_user, top_k=5)
            result = {
                "task": task,
                "result": {
                    "user": target_user,
                    "recommendations": recs
                }
            }
        else:
            result = {
                "task": task,
                "result": "Unable to find user or friendship data for recommendations"
            }
    elif "recommend" in task_lower and ("hobby" in task_lower or "hobbies" in task_lower or "club" in task_lower):
        # Extract user from task if mentioned
        import re
        user_match = re.search(r'for\s+(\d+)', task_lower)
        target_user = user_match.group(1) if user_match else DATA_DF['user_id'].iloc[0] if 'user_id' in DATA_DF.columns else None

        if target_user and 'user_id' in DATA_DF.columns and 'hobbies' in DATA_DF.columns:
            recs = recommend_hobbies(DATA_DF, target_user, top_k=5)
            result = {
                "task": task,
                "result": {
                    "user": target_user,
                    "hobby_club_recommendations": recs
                }
            }
        else:
            result = {
                "task": task,
                "result": "Unable to find user or lifestyle data for hobby/club recommendations"
            }
    elif "visualize" in task_lower or "chart" in task_lower or "plot" in task_lower:
        path = create_visualizations(DATA_DF)
        result = {
            "task": task,
            "result": {
                "chart_path": path,
                "message": "Visualization created successfully"
            }
        }
    elif "visualization" in task_lower:
        path = create_visualizations(DATA_DF)
        result = {
            "task": task,
            "result": {
                "chart_path": path,
                "message": "Visualization created successfully"
            }
        }
    elif "count" in task_lower or "frequency" in task_lower:
        if 'User' in DATA_DF.columns:
            counts = DATA_DF['User'].value_counts().to_dict()
            result = {
                "task": task,
                "result": {
                    "user_counts": counts,
                    "total_users": len(counts)
                }
            }
        else:
            result = {
                "task": task,
                "result": "No 'User' column found for counting"
            }
    else:
        result = {
            "task": task,
            "result": f"I can help with: summary, friend recommendations, hobby/club recommendations, visualizations, or user counts. Please specify one of these tasks."
        }

    return result

# Mount static files for the frontend
app.mount("/", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "../../frontend/dist"), html=True), name="static")

@app.get("/")
async def serve_frontend():
    """Serve the frontend application"""
    return HTMLResponse(content=open("../frontend/dist/index.html").read(), status_code=200)
