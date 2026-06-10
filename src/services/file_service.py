import asyncio

from PIL import Image, ImageDraw, ImageFont
import io
import mimetypes
import os
import subprocess
import tempfile
import unicodedata
from collections.abc import AsyncIterator
from urllib.parse import quote

from PIL import Image, ImageDraw, ImageFont
from moviepy import VideoFileClip
from pdf2image import convert_from_path
from fastapi import HTTPException, Response, UploadFile, status

from src.exception.item_exception import ExceptionItemNotFound
from src.repositories.file.file_repository import FileRepository
from src.models.file.file_document import FileDocument
from fastapi.responses import StreamingResponse
from src.models.file.update_file_model import UpdateFileName
from bson import ObjectId
from src.enums.file_status_enum import FileStatusEnum
from src.enums.image_size_enum import ImageSizeEnum
from src.default.char_length_default import CHAR
from src.enums.file_format_enum import FileFormat
from src.exception.file_exception import FileNotFoundException, FileBadRequestException
from src.models.file.response_file_model import ResponseFileModel
from src.models.response_model import ResponseModel
from src.default.file_type_default import office_mimetypes
from src.utils.http_range_util import build_range_not_satisfiable_headers, parse_byte_range
from fastapi import BackgroundTasks
import zipfile

SIZE = ImageSizeEnum.STANDARD.value
DELETE = FileStatusEnum.DELETED.value
NORMAL = FileStatusEnum.NORMAL.value


def _split_filename(filename: str) -> tuple[str, str]:
    if not filename:
        return "file", ""
    name, extension = os.path.splitext(filename)
    return name or "file", extension.lstrip(".")


def _compose_filename(name: str, extension: str) -> str:
    return f"{name}.{extension}" if extension else name


def _build_content_disposition(disposition: str, filename: str) -> str:
    normalized = unicodedata.normalize("NFKD", filename)
    fallback = normalized.encode("ascii", "ignore").decode("ascii")
    fallback = fallback.replace("\\", "_").replace('"', "_").strip() or "file"
    encoded = quote(filename, safe="")
    return f"{disposition}; filename=\"{fallback}\"; filename*=UTF-8''{encoded}"


class FileService:

    def __init__(self, repo: FileRepository):
        self.repo = repo
        # self.fs = repo.fs

    def saved_data(self, file_id, file_name: str, type: str = "png"):
        return FileDocument(type=type,
                            status=NORMAL,
                            name=file_name,
                            file_id=str(file_id), )

    async def _close_grid_out(self, grid_out) -> None:
        close_method = getattr(grid_out, "close", None)
        if close_method is None:
            return

        close_result = close_method()
        if asyncio.iscoroutine(close_result):
            await close_result

    async def _iter_grid_out(self, grid_out, start: int, end: int) -> AsyncIterator[bytes]:
        await grid_out.seek(start)
        remaining = max(end - start + 1, 0)

        try:
            while remaining > 0:
                chunk = await grid_out.readchunk()
                if not chunk:
                    break
                if len(chunk) > remaining:
                    chunk = chunk[:remaining]
                remaining -= len(chunk)
                yield chunk
        finally:
            await self._close_grid_out(grid_out)

    def _build_stream_headers(
            self,
            file_name: str,
            file_size: int,
            byte_range: tuple[int, int] | None,
            disposition: str = "inline",
    ) -> dict[str, str]:
        headers = {
            "Accept-Ranges": "bytes",
            "Content-Disposition": _build_content_disposition(disposition, file_name),
        }

        if byte_range is None:
            headers["Content-Length"] = str(file_size)
            return headers

        start, end = byte_range
        headers["Content-Length"] = str(end - start + 1)
        headers["Content-Range"] = f"bytes {start}-{end}/{file_size}"
        return headers

    async def _build_file_response(
            self,
            file,
            range_header: str | None = None,
            disposition: str = "inline",
    ) -> StreamingResponse:
        file_name = _compose_filename(file.name, file.type)
        mime_type, _ = mimetypes.guess_type(file_name)
        mime_type = mime_type or "application/octet-stream"

        grid_out = await self.repo.open_download_stream(ObjectId(file.file_id))
        file_size = grid_out.length
        print("file size", file_size)
        byte_range = None
        if range_header:
            try:
                byte_range = parse_byte_range(range_header, file_size)
            except ValueError as exc:
                await self._close_grid_out(grid_out)
                raise HTTPException(
                    status_code=status.HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE,
                    detail=str(exc),
                    headers=build_range_not_satisfiable_headers(file_size),
                ) from exc

        start, end = byte_range or (0, file_size - 1)
        status_code = (
            status.HTTP_206_PARTIAL_CONTENT
            if byte_range is not None
            else status.HTTP_200_OK
        )
        headers = self._build_stream_headers(file_name, file_size, byte_range, disposition)

        return StreamingResponse(
            self._iter_grid_out(grid_out, start, end),
            media_type=mime_type,
            status_code=status_code,
            headers=headers,
        )

    async def _build_file_head_response(self, file, disposition: str = "inline") -> Response:
        file_name = _compose_filename(file.name, file.type)
        mime_type, _ = mimetypes.guess_type(file_name)
        mime_type = mime_type or "application/octet-stream"

        grid_out = await self.repo.open_download_stream(ObjectId(file.file_id))
        try:
            file_size = grid_out.length
        finally:
            await self._close_grid_out(grid_out)

        headers = self._build_stream_headers(file_name, file_size, None, disposition)
        return Response(
            media_type=mime_type,
            headers=headers,
        )

    async def create_thumbnail_img(self, file: UploadFile, filename: str) -> None:
        # code for img ok
        # data = await file.read()
        # await file.seek(0)
        # io.BytesIO()
        # other way: io.BytesIO(data)
        img = Image.open(file.file)
        img.thumbnail(SIZE)
        buffer = io.BytesIO()
        img.save(buffer, format=FileFormat.PNG.value)
        thumbnail = buffer.getvalue()
        upload_name, _ = _split_filename(file.filename or filename)
        file_id = await self.repo.upload_from_stream(upload_name, thumbnail)

        data = self.saved_data(file_id, filename)
        return await self.repo.save(data)

    # file: video
    async def create_thumbnail_vid_text_ppt(self, file: UploadFile, content_type: str, filename: str) -> None:
        # await file.seek(0)

        with tempfile.TemporaryDirectory() as temp_dir:
            tempfile_path = os.path.join(temp_dir, file.filename)
            # print(file.filename)
            # save the uploaded file
            with open(tempfile_path, 'wb') as temp_file:
                content = await file.read()
                temp_file.write(content)
            upload_name, _ = _split_filename(file.filename or filename)
            if content_type.startswith("video"):
                # use context manager to delete file after use, else must use video.close()
                with VideoFileClip(tempfile_path) as video:
                    get_frame = video.get_frame(1)
                    img = Image.fromarray(get_frame)
                    img.thumbnail(SIZE)
                    buffer = io.BytesIO()
                    img.save(buffer, format=FileFormat.PNG.value)
                    thumbnail = buffer.getvalue()
                    file_id = await self.repo.upload_from_stream(upload_name, thumbnail)

                    data = self.saved_data(file_id, filename)
                    return await self.repo.save(data)

            elif content_type == "application/pdf":
                # change this var to run on win ,poppler_path=poppler_path
                # poppler_path = r"C:\tool\Release-25.12.0-0\poppler-25.12.0\Library\bin"
                images = convert_from_path(tempfile_path, first_page=1, last_page=1)
                img = images[0]
                img.thumbnail(SIZE)
                buffer = io.BytesIO()
                img.save(buffer, format=FileFormat.PNG.value)
                thumbnail = buffer.getvalue()
                file_id = await self.repo.upload_from_stream(upload_name, thumbnail)

                data = self.saved_data(file_id, filename)
                return await self.repo.save(data)

            elif content_type in office_mimetypes:
                try:
                    # thumbnail_path = os.path.join(temp_dir, filename)
                    with zipfile.ZipFile(tempfile_path,'r') as zip_file:
                        file_list = zip_file.namelist()
                        target_thumbnails = ['docProps/thumbnail.jpeg', 'Thumbnails/thumbnail.png']
                        thumbnail_bytes = None

                        for target in target_thumbnails:
                            if target in file_list:
                                thumbnail_bytes = zip_file.read(target)
                                break  # find thumbnail with right format
                        if not thumbnail_bytes:
                            for file_name in file_list:
                                lower_name = file_name.lower()
                                if lower_name.endswith(('.png', '.jpg', '.jpeg', '.webp')):
                                    thumbnail_bytes = zip_file.read(file_name)
                                    break
                                else:
                                    raise zipfile.BadZipFile(
                                        "Không tìm thấy ảnh nào trong file, chuyển sang dùng LibreOffice.")
                        if thumbnail_bytes:
                            file_id = await self.repo.upload_from_stream(upload_name, thumbnail_bytes)
                            data = self.saved_data(file_id, filename)
                            return await self.repo.save(data)
                except zipfile.BadZipfile:
                    # ppt, can eror with libre
                    result = subprocess.run([
                        'soffice', '--headless', '--convert-to', 'pdf',
                        '--outdir', temp_dir, tempfile_path
                    ], check=True, capture_output=True, text=True, timeout=30)
                    # debug
                    print(f"soffice stdout: {result.stdout}")
                    print(f"soffice stderr: {result.stderr}")

                    pdf_path = os.path.join(temp_dir, os.path.splitext(file.filename)[0] + '.pdf')
                    # debug
                    # Check if PDF was actually created
                    if not os.path.exists(pdf_path):
                        raise FileNotFoundError(f"PDF conversion failed. Expected file at: {pdf_path}")

                    print(f"PDF created at: {pdf_path}, size: {os.path.getsize(pdf_path)} bytes")

                    # get path of pdf
                    images = convert_from_path(pdf_path, first_page=1, last_page=1)
                    img = images[0]
                    img.thumbnail(SIZE)
                    buffer = io.BytesIO()
                    img.save(buffer, format=FileFormat.PNG.value)
                    thumbnail = buffer.getvalue()
                    file_id = await self.repo.upload_from_stream(upload_name, thumbnail)

                    data = self.saved_data(file_id, filename)
                    return await self.repo.save(data)

            elif content_type == "text/plain":
                with open(tempfile_path, 'r', encoding='utf-8') as f:
                    text = f.read(CHAR)
                    # print(text)
                    has_more = len(f.read(1)) > 0
                    img = Image.new('RGB', SIZE, 'white')
                    draw = ImageDraw.Draw(img)

                    try:
                        font = ImageFont.truetype("arial.ttf", 12)
                    except:
                        font = ImageFont.load_default()
                    display_text = text + "..." if has_more else text
                    draw.text((10, 10), display_text, fill='black', font=font)
                    buffer = io.BytesIO()
                    img.save(buffer, format=FileFormat.PNG.value)
                    thumbnail = buffer.getvalue()
                    file_id = await self.repo.upload_from_stream(upload_name, thumbnail)

                    data = self.saved_data(file_id, filename)
                    return await self.repo.save(data)
            else:
                raise ValueError(f"Unsupported file type: {content_type}")

    async def create_thumbnail(self, file: UploadFile, file_name):
        content_type = file.content_type
        # print(content_type)
        thumbnail_id = ""
        if content_type.startswith("image"):
            thumbnail_id = await self.create_thumbnail_img(file, file_name)
        else:
            thumbnail_id = await self.create_thumbnail_vid_text_ppt(file, content_type, file_name)
        return ResponseFileModel(thumbnail_id=thumbnail_id, file_id="")

    async def get_thumbnail(self, id: str):
        file = await self.repo.get_by_id(id)
        if file is None:
            raise FileNotFoundException()
        if file.name.startswith("thumbnail"):
            return await self._build_file_response(file)
        raise FileBadRequestException()

    async def get_file(
            self,
            id: str,
            range_header: str | None = None,
            download: bool = False,
    ):
        file = await self.repo.get_by_id(id)
        if file is None:
            raise FileNotFoundException()
        # print(file)
        if file.name.startswith("thumbnail"):
            raise FileBadRequestException()
        disposition = "attachment" if download else "inline"
        return await self._build_file_response(file, range_header, disposition)

    async def get_file_metadata(self, id: str, download: bool = False) -> Response:
        file = await self.repo.get_by_id(id)
        if file is None:
            raise FileNotFoundException()
        if file.name.startswith("thumbnail"):
            raise FileBadRequestException()
        disposition = "attachment" if download else "inline"
        return await self._build_file_head_response(file, disposition)

    async def upload_file(self, file: UploadFile, background_tasks: BackgroundTasks):
        original_name = file.filename or "file"
        base_name, extension = _split_filename(original_name)
        data = await file.read()
        upload_bytes = data

        file_id = await self.repo.upload_from_stream(base_name, upload_bytes)

        record_id = await self.repo.save(self.saved_data(
            file_id, base_name, extension))
        print("save file with", record_id)
        # check type mp3
        if file.content_type in ["audio/mpeg", "audio/mp3"]:
            return ResponseFileModel(file_id=record_id, file_name=base_name)
        await file.seek(0)
        # thumbnail_id = await self.create_thumbnail(file, f"thumbnail_{id}")

        # return ResponseFileModel(thumbnail_id=thumbnail_id,file_id=id, file_name=file.filename)

        background_tasks.add_task(
            self.process_thumbnail_task,
            str(record_id),
            data,
            file.content_type,
            original_name
        )
        return ResponseFileModel(thumbnail_id="", file_id=record_id, file_name=file.filename)

    async def process_thumbnail_task(self, record_id: str, data: bytes, content_type: str, filename: str):
        print(f"!!! BACKGROUND TASK STARTED: {record_id} !!!", flush=True)
        try:
            print(f"--- Start background task for {record_id} ---", flush=True)
            print(f"Data size: {len(data)} bytes", flush=True)

            class StubFile:
                def __init__(self, content, name, c_type):
                    self.content = content
                    self.filename = name
                    self.content_type = c_type
                    self.file = io.BytesIO(content)

                async def read(self, size=-1): return self.file.read(size)

                async def seek(self, offset, whence=0): self.file.seek(offset, whence)

                async def tell(self): return self.file.tell()

            stub_file = StubFile(data, filename, content_type)

            print(f"Invoking create_thumbnail for {record_id}...", flush=True)
            result = await self.create_thumbnail(stub_file, f"thumbnail_{record_id}")
            print(f"Create thumbnail result: {result}", flush=True)

            if result and result.thumbnail_id:
                print(f"Updating DB with thumbnail_id: {result.thumbnail_id}", flush=True)
                await self.repo.update_thumbnail_id(record_id, result.thumbnail_id)
                print(f"Update success for {record_id}", flush=True)
            else:
                print(f"No thumbnail_id returned for {record_id}", flush=True)

        except Exception as e:
            print(f"!!! ERROR in process_thumbnail_task: {str(e)} !!!", flush=True)
            import traceback
            traceback.print_exc()

    async def rename_file(self, id: str, data: UpdateFileName):

        file = await self.repo.get_by_id(id)
        if file is None:
            raise FileNotFoundException()
        print(file.status)
        if file.status == DELETE:
            raise FileNotFoundException()
        if file is None:
            raise FileNotFoundException()
        if file.name.startswith("thumbnail"):
            raise FileBadRequestException()
        file.name = data.name
        data = await self.repo.update(file)
        return ResponseModel(data=data)

    async def delete_file(self, id: str):
        file = await self.repo.get_by_id(id)
        if file is None:
            raise FileNotFoundException()
        if file.status == DELETE:
            raise FileNotFoundException()
        file.status = DELETE
        await self.repo.update(file)
        return

    async def upload_multiple_files(self, files: list[UploadFile], background_tasks: BackgroundTasks):
        tasks = [self.upload_file(file, background_tasks) for file in files]
        results = await asyncio.gather(*tasks)
        return results


    async def get_info_by_id(self, file_id: str):
        file_dump = await self.repo.get_info_by_id(file_id)
        if not file_dump:
            raise ExceptionItemNotFound()
        return ResponseModel(data=file_dump)


    async def get_info_files_by_ids(self, ids: list[str]):
        results = await self.repo.get_info_files_by_ids(ids)
        return ResponseModel(data=results)
