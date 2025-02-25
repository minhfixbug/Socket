import socket
import os

# Cấu hình địa chỉ và cổng cho Server
SERVER_IP = "127.0.0.1"  # Địa chỉ localhost (hoặc thay bằng IP server thật nếu cần)
SERVER_PORT = 12345       # Cổng cố định cho server
BUFFER_SIZE = 1024        # Kích thước tối đa mỗi lần nhận dữ liệu

# Bước 1: Tạo socket UDP cho Server
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((SERVER_IP, SERVER_PORT))

print(f"Server đang lắng nghe tại {SERVER_IP}:{SERVER_PORT}...")

# Hàm đọc danh sách file từ file_list.txt
def load_file_list():
    file_list = {}
    with open("DSFile.txt", "r") as f:
        for line in f:
            name, size = line.strip().split()  # Tách tên file và kích thước
            file_list[name] = size  # Lưu vào dictionary
    return file_list

# Tải danh sách file
file_list = load_file_list()
print("Danh sách file có sẵn:", file_list)

while True:
    # Nhận yêu cầu từ Client
    data, client_address = server_socket.recvfrom(BUFFER_SIZE)
    request = data.decode()

    if request == "GET_FILE_LIST":
        # Nếu Client yêu cầu danh sách file
        file_list_str = "\n".join([f"{name} {size}" for name, size in file_list.items()])
        server_socket.sendto(file_list_str.encode(), client_address)
        print(f"Đã gửi danh sách file cho Client tại {client_address}")
    if request.startswith("DOWNLOAD_PART"):
        _, file_name, part_number, total_parts = request.split(" ")
        part_number = int(part_number)
        total_parts = int(total_parts)

        if os.path.exists(file_name):
            file_size = os.path.getsize(file_name)
            part_size = file_size // total_parts
            start_offset = part_number * part_size
            end_offset = start_offset + part_size

            with open(file_name, "rb") as file:
                file.seek(start_offset)
                while start_offset < end_offset:
                    chunk = file.read(BUFFER_SIZE)
                    if not chunk:
                        break
                    server_socket.sendto(chunk, client_address)
                    start_offset += len(chunk)
            print(f"Đã gửi xong phần {part_number + 1} của file {file_name}")
        else:
            error_message = f"File {file_name} không tồn tại."
            server_socket.sendto(error_message.encode(), client_address)
            print(f"Lỗi: {error_message}")
