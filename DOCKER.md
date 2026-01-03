# Docker Instructions for UzPassportReader

## Requirements

- Docker (version **20.10+**)
- **At least 8 GB of RAM and 4 CPU** (recommended)
- The container is configured to use **up to 16 CPU cores** and **16 GB of RAM**

---

```bash
# Build the Docker image
docker build -t uzpassport-reader .

# Run the container with resource limits
docker run -d \
  --name uzpassport-reader \
  -p 18000:18000 \
  --restart unless-stopped \
  --cpus="16" \
  --memory=16g \
  uzpassport-reader

# View container logs
docker logs uzpassport-reader

# Check container status
docker ps

# Test API (OpenAPI / Swagger UI)
curl http://localhost:18000/docs

# Stop the container
docker stop uzpassport-reader

# Remove the container
docker rm uzpassport-reader
