FROM node:alpine AS static-builder

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY ./probenplan/styles ./probenplan/styles
RUN npm run build


FROM python:alpine

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ARG PROBENPLAN_CALENDAR=none

WORKDIR /app

COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY ./probenplan/ ./probenplan
COPY --from=static-builder /app/probenplan/static ./probenplan/static

EXPOSE 8000
CMD ["waitress-serve", "probenplan:app"]