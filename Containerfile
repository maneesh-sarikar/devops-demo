 
FROM node:24-alpine AS frontend-build
 
WORKDIR /app
 
COPY app/package*.json ./
RUN npm install
 
COPY app/ ./
RUN npm run build
 
 
FROM nginx:alpine AS frontend
 
COPY --from=frontend-build /app/dist /usr/share/nginx/html
COPY nginx/default.conf /etc/nginx/conf.d/default.conf
 
EXPOSE 80
 
CMD ["nginx", "-g", "daemon off;"]
 
 
FROM python:3.12-slim AS backend
 
WORKDIR /app
 
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
 
COPY api/ ./api/
 
EXPOSE 8000
 
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
 