from fastapi import FastAPI, UploadFile, File, Form, HTTPException
import boto3

app = FastAPI(title="FastAPI S3 Images")

s3 = boto3.client("s3")

BUCKET_NAME = "alejo-fastapi-images-2026"
ALLOWED_TYPES = ["image/png", "image/jpeg"]


@app.get("/")
def root():
    return {"message": "API funcionando correctamente"}

@app.post("/upload/")
async def upload_image(
    username: str = Form(...),
    file: UploadFile = File(...)
):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=415,
            detail="Formato inválido. Solo PNG/JPG/JPEG"
        )

    contents = await file.read()

    s3.put_object(
        Bucket=BUCKET_NAME,
        Key=f"{username}/{file.filename}",
        Body=contents,
        ContentType=file.content_type
    )

    return {
        "message": "Imagen almacenada correctamente",
        "usuario": username,
        "archivo": file.filename
    }


@app.get("/get-image/{username}/{image_name}")
def get_image(username: str, image_name: str):
    key = f"{username}/{image_name}"

    try:
        metadata = s3.head_object(
            Bucket=BUCKET_NAME,
            Key=key
        )
    except:
        raise HTTPException(
            status_code=404,
            detail="Usuario o imagen no existen"
        )

    url = s3.generate_presigned_url(
        "get_object",
        Params={
            "Bucket": BUCKET_NAME,
            "Key": key
        },
        ExpiresIn=3600
    )

    return {
        "usuario": username,
        "imagen": image_name,
        "url": url,
        "fecha_almacenamiento": str(metadata["LastModified"])
    }
