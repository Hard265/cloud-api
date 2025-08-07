from PIL import Image
import io
import ffmpeg
import mimetypes
from pypdf import PdfReader
from pypdf.errors import PdfReadError


def _generate_pdf_thumbnail(file_path: str, size: tuple[int, int]) -> io.BytesIO:
    try:
        reader = PdfReader(file_path)
        page = reader.pages[0]
        xObject = page["/Resources"]["/XObject"].get_object()

        image_data = None
        for obj in xObject:
            if xObject[obj]["/Subtype"] == "/Image":
                image_data = xObject[obj].get_data()
                break

        if not image_data:
            return None

        img = Image.open(io.BytesIO(image_data))
        img.thumbnail(size)
        thumb_io = io.BytesIO()
        img.save(thumb_io, format="PNG")
        thumb_io.seek(0)
        return thumb_io
    except (PdfReadError, KeyError, IndexError):
        return None


def _generate_image_thumbnail(file_path: str, size: tuple[int, int]) -> io.BytesIO:
    img = Image.open(file_path)
    img.thumbnail(size)
    thumb_io = io.BytesIO()
    img.save(thumb_io, format="PNG")
    thumb_io.seek(0)
    return thumb_io


def _generate_video_thumbnail(file_path: str, size: tuple[int, int]) -> io.BytesIO:
    out, _ = (
        ffmpeg.input(file_path)
        .filter("scale", size[0], -1)
        .output("pipe:", vframes=1, format="image2", vcodec="png")
        .run(capture_stdout=True, quiet=True)
    )
    return io.BytesIO(out)


def generate_thumbnail(file_path: str, size: tuple[int, int] = (128, 128)):
    try:
        mime_type, _ = mimetypes.guess_type(file_path)
        if mime_type == "application/pdf":
            thumb_io = _generate_pdf_thumbnail(file_path, size)
        elif mime_type and mime_type.startswith("video/"):
            thumb_io = _generate_video_thumbnail(file_path, size)
        else:
            thumb_io = _generate_image_thumbnail(file_path, size)
        return thumb_io, None
    except Exception as e:
        return None, str(e)
