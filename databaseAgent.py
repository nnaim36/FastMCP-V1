from fastapi import FastAPI
from fastmcp import FastMCP
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

mcp = FastMCP()
