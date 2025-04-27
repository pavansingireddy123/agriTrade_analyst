# # # main.py
# # from fastapi import FastAPI, HTTPException
# # from pydantic import BaseModel
# # from model import calculate_financials
# # from fastapi.middleware.cors import CORSMiddleware

# # app = FastAPI()

# # # Allow CORS for frontend


# # class FinancialRequest(BaseModel):
# #     district: str
# #     crop: str
# #     season: str
# #     acres: int
# #     start_date: str  # frontend sends date string

# # @app.post("/financial-summary")
# # def financial_summary(request: FinancialRequest):
# #     try:
# #         result = calculate_financials(
# #             district=request.district,
# #             crop=request.crop,
# #             season=request.season,
# #             acres=request.acres,
# #             start_date=request.start_date
# #         )
# #         return result
# #     except Exception as e:
# #         raise HTTPException(status_code=400, detail=str(e))
# import numpy as np
# from fastapi import FastAPI
# from pydantic import BaseModel

# app = FastAPI()

# class InputData(BaseModel):
#     district: str
#     crop: str
#     season: str
#     date: str

# @app.post("/financial-summary")
# def financial_summary(data: InputData):
#     # Suppose your model or code returns a numpy.int64
#     revenue = np.int64(5000)  # Just example
#     cost = np.int64(2000)
#     profit = revenue - cost

#     # Convert numpy values to regular Python int
#     return {
#         "revenue": int(revenue),
#         "cost": int(cost),
#         "profit": int(profit)
#     }

# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# import pandas as pd

# app = FastAPI()

# # Allow CORS
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Load the CSVs
# districts_df = pd.read_csv("./datasets/DISTRTICTS_DATASET final.csv")
# crops_df = pd.read_csv("./datasets/Cropcost.csv")

# @app.get("/options")
# def get_options():
#     districts = sorted(districts_df['District'].unique())
#     crops = sorted(crops_df['Crop'].unique())
#     seasons = sorted(crops_df['Season'].unique())
#     return {
#         "districts": districts,
#         "crops": crops,
#         "seasons": seasons
#     }
# app.py
from flask import Flask, jsonify, request
from flask_cors import CORS
from model import calculate_financials, df_districts, df_crop

app = Flask(__name__)
CORS(app)

@app.route('/districts', methods=['GET'])
def get_districts():
    districts = df_districts['District'].unique().tolist()
    return jsonify(sorted(districts))

@app.route('/crops', methods=['GET'])
def get_crops():
    crops = df_districts['Crop'].unique().tolist()
    return jsonify(sorted(crops))

@app.route('/seasons', methods=['GET'])
def get_seasons():
    seasons = df_crop['Season'].unique().tolist()
    return jsonify(sorted(seasons))

@app.route('/calculate', methods=['POST'])
def calculate():
    try:
        data = request.get_json()
        result = calculate_financials(
            district=data['district'],
            crop=data['crop'],
            season=data['season'],
            acres=data['acres'],
            start_date="2023-01-01"  # You might want to make this dynamic
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)