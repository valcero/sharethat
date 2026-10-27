import os
from dotenv import load_dotenv
from imagekitio import ImageKit

load_dotenv()

imagekit = ImageKit(
    private_key=os.getenv("IMAGEKIT_PRIVATE_KEY") or "dev_private_key",
    public_key=os.getenv("IMAGEKIT_PUBLIC_KEY") or "dev_public_key",
    url_endpoint=os.getenv("IMAGEKIT_URL") or "https://ik.imagekit.io/sharethat_dev",
)