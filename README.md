# UzPassportReader

A FastAPI-based OCR service for extracting structured data from Uzbek passport and ID cards using PaddleOCR.

## 📋 Overview

UzPassportReader is an OCR API that processes images of Uzbek passports and ID cards, extracting structured personal information including names, dates, document numbers, and other relevant fields. The service uses PaddleOCR for text recognition and custom parsers optimized for Uzbek document formats.

## ✨ Features

- **Dual Document Support**:
    - **Passport**: Processes front page only
    - **ID Card**: Processes both front and back sides (including QR code extraction)

- **Extracted Fields**:
    - Personal information: surname, given name, patronymic
    - Dates: birth, issue, expiry
    - Document details: card/passport number, authority
    - Additional: place of birth, personal number (ID cards only), sex

- **Image Processing**:
    - Automatic image validation and format checking
    - Image resizing for optimal OCR performance
    - Support for JPEG, JPG, and PNG formats

- **API Features**:
    - RESTful API with OpenAPI/Swagger documentation + ReDOC GitHub Pages
    - Type-safe request/response models using Pydantic


## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- pip
- Min RAM 8GB

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Yusk03/UzPassportReader.git
   cd UzPassportReader
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

   **Note**: PaddleOCR installation may take some time as it downloads model files on first use.

4. **Configure environment** (optional):
   ```bash
   cp .env.example .env
   # Edit .env and set your API_KEY if needed
   ```

### Running the Server

Start the server with uvicorn:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI JSON**: `http://localhost:8000/openapi.json`

## 📚 API Documentation

### Interactive Documentation

- **Local**: Available at `/docs` (Swagger UI) and `/redoc` (ReDoc) when running the server
- **Online**: Hosted on GitHub Pages at `/docs` (see [Documentation](#-documentation) section)

### API Endpoint

#### POST `/ocr`

Perform OCR on passport or ID card images.

**Request Parameters**:

The endpoint uses `multipart/form-data` with different requirements based on document type:

**For Passport** (`isIdCard=false`):
- `isIdCard` (boolean, required): Must be `false`
- `frontPhoto` (file, required): Front page of passport

**For ID Card** (`isIdCard=true`):
- `isIdCard` (boolean, required): Must be `true`
- `frontPhoto` (file, required): Front side of ID card
- `backPhoto` (file, required): Back side of ID card

**Response**:

The response format depends on the document type:

**ID Card Response**:
```json
{
  "status": "ok",
  "document_type": "id_card",
  "result": {
    "surname": "ABDULBOQIYEV",
    "given_name": "FARRUX",
    "patronymic": "ABDULLO O'G'LI",
    "date_of_birth": "03.04.2005",
    "sex": "M",
    "date_of_issue": "11.11.2024",
    "date_of_expiry": "10.11.2034",
    "card_number": "AD1234567",
    "personal_number": "51111055950034",
    "place_of_birth": "NORIN TUMANI",
    "authority": "IIV 14242",
    "raw": ["..."]
  }
}
```

**Passport Response**:
```json
{
  "status": "ok",
  "document_type": "passport",
  "result": {
    "surname": "ABDULBOQIYEV",
    "given_name": "FARRUX",
    "patronymic": "ABDULLO O'G'LI",
    "date_of_birth": "03.04.2005",
    "sex": "M",
    "date_of_issue": "11.11.2024",
    "date_of_expiry": "10.11.2034",
    "card_number": "AD1234567",
    "place_of_birth": "NORIN TUMANI",
    "authority": "MIA 33222",
    "raw": ["..."]
  }
}
```

**Error Responses**:
- `400 Bad Request`: Invalid request parameters or image format
- `413 Payload Too Large`: Image file too large (>10MB)
- `422 Unprocessable Entity`: Missing required fields (e.g., backPhoto for ID card)
- `500 Internal Server Error`: OCR processing failure

## 💻 Usage Examples

### Using curl

**Passport**:
```bash
curl -X POST "http://localhost:8000/ocr" \
  -F "isIdCard=false" \
  -F "frontPhoto=@passport_front.jpg"
```

**ID Card**:
```bash
curl -X POST "http://localhost:8000/ocr" \
  -F "isIdCard=true" \
  -F "frontPhoto=@id_card_front.jpg" \
  -F "backPhoto=@id_card_back.jpg"
```

### Using JavaScript (fetch)

```javascript
const formData = new FormData();
formData.append('isIdCard', 'true');
formData.append('frontPhoto', frontPhotoFile);
formData.append('backPhoto', backPhotoFile);

const response = await fetch('http://localhost:8000/ocr', {
  method: 'POST',
  body: formData
});

const data = await response.json();
console.log(data);
```

## 📖 Documentation

### Online Documentation

API documentation is hosted on GitHub Pages:
- **ReDoc**: Available at `/docs` in the repository's GitHub Pages
- **OpenAPI Spec**: `docs/openapi.json`

### Local Documentation

When running the server locally:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## ⚠️ Disclaimer

This project is provided for educational and technical purposes only.

The authors do not guarantee the accuracy of parsed data and are not responsible for any misuse of the software or for processing personal data without proper legal grounds.

Users are solely responsible for compliance with local data protection laws (including GDPR).

See [DISCLAIMER.md](DISCLAIMER.md) for full details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 👤 Author

**yusk03**

## 🙏 Acknowledgments

- [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR) for OCR capabilities
- [FastAPI](https://fastapi.tiangolo.com/) for the web framework
- [Pydantic](https://docs.pydantic.dev/) for data validation

---

**Note**: First OCR request may be slower as PaddleOCR downloads model files if not already cached.

