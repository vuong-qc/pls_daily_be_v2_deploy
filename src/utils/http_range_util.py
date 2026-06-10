def build_range_not_satisfiable_headers(file_size: int) -> dict[str, str]:
    return {"Content-Range": f"bytes */{file_size}"}


def parse_byte_range(range_header: str | None, file_size: int) -> tuple[int, int] | None:
    """
    Phân tích HTTP Range header (ví dụ: 'bytes=0-499').
    Trả về tuple (start, end) nếu hợp lệ, ngược lại trả về None.
    """
    if not range_header:
        return None

    if file_size <= 0:
        raise ValueError("Requested Range Not Satisfiable")

    # 1. Tách unit (bytes) và giá trị (0-499)
    # Strip để loại bỏ khoảng trắng thừa ở hai đầu
    parts = range_header.strip().split("=", 1)
    if len(parts) != 2:
        raise ValueError("Invalid Range header")

    unit, range_value = parts
    if unit.lower() != "bytes" or not range_value:
        raise ValueError("Invalid Range header")

    # Không hỗ trợ nhiều dải range (ví dụ: bytes=0-100, 500-600)
    if "," in range_value:
        raise ValueError("Invalid Range header")

    # 2. Tách start và end bằng partition để luôn có 3 phần
    start_str, dash, end_str = range_value.partition("-")
    if dash != "-":
        raise ValueError("Invalid Range header")

    start_str = start_str.strip()
    end_str = end_str.strip()

    # Trường hợp A: Suffix range (Ví dụ: "-500") -> Lấy 500 byte cuối
    if not start_str:
        if not end_str.isdigit():
            raise ValueError("Invalid Range header")

        suffix_length = int(end_str)
        if suffix_length <= 0:
            raise ValueError("Requested Range Not Satisfiable")

        start = max(file_size - suffix_length, 0)
        end = file_size - 1

    # Trường hợp B: Start-End hoặc Start- (Ví dụ: "0-499" hoặc "500-")
    else:
        if not start_str.isdigit():
            raise ValueError("Invalid Range header")

        start = int(start_str)
        # Nếu vị trí bắt đầu vượt quá kích thước file -> Không thỏa mãn (416)
        if start >= file_size:
            raise ValueError("Requested Range Not Satisfiable")

        if not end_str:
            # Dải mở: "500-" lấy đến cuối file
            end = file_size - 1
        else:
            if not end_str.isdigit():
                raise ValueError("Invalid Range header")

            end = int(end_str)
            # Giới hạn end không được vượt quá kích thước file thực tế
            end = min(end, file_size - 1)

    if start > end:
        raise ValueError("Requested Range Not Satisfiable")

    return start, end
