FROM node:22-slim

# Install python3 and pip
RUN apt-get update && apt-get install -y python3 python3-pip && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy python dependencies
COPY requirements.txt .
RUN pip3 install --no-cache-dir --break-system-packages -r requirements.txt

# Copy whatsapp dependencies
COPY whatsapp/package.json whatsapp/
WORKDIR /app/whatsapp
RUN npm install

WORKDIR /app
COPY . .

EXPOSE 5000

CMD ["sh", "-c", "python3 api.py & cd whatsapp && node bot.js"]
