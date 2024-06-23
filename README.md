# PharmaTracker

PharmaTracker is a cloud native web application created for pharmacies or private users. It is a data warehouse for tracking medicine stored in a pharmacy or a home cabinet.

1. Builds the image
```
./build/build.sh
```
2. Runs the container
```
docker run -p 80:80 pharmatracker:latest
```
3. Runs the app
```lua
uvicorn src.main:app --host 0.0.0.0 --port 80 
```