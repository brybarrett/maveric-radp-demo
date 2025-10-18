# Build stage
FROM node:18-alpine AS build

WORKDIR /app

# Copy package files from frontend directory
COPY frontend/package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy frontend code
COPY frontend/ .

# Build the React app
RUN npm run build

# Production stage
FROM node:18-alpine

WORKDIR /app

# Install serve
RUN npm install -g serve

# Copy built files from build stage
COPY --from=build /app/build ./build

# Expose port 3000
EXPOSE 3000

# Serve the production build
CMD ["serve", "-s", "build", "-l", "3000"]