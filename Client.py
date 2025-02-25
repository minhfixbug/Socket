import socket
import time
import threading
import os

# Cấu hình địa chỉ Server
SERVER_IP = "127.0.0.1"
SERVER_PORT = 12345
BUFFER_SIZE = 1024

# Bước 1: Tạo socket UDP cho Client
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Khóa để đảm bảo rằng chỉ một luồng có thể cập nhật màn hình tại một thời điểm
print_lock = threading.Lock()

# Hàm hiển thị tiến độ tải của tất cả các phần
def display_progress(file_name, progress, start_time):
    with print_lock:
        os.system('cls' if os.name == 'nt' else 'clear')  # Xóa màn hình trước khi in trạng thái mới
        elapsed_time = time.time() - start_time
        for part_number, percent in enumerate(progress):
            print(f"{file_name} - Phần {part_number + 1}: Đang tải... {percent}%")
        print(f"Thời gian đã trôi qua: {elapsed_time:.2f} giây")

# Hàm tải xuống một phần của file từ máy cục bộ
def download_part(file_path, start, end, part_number, progress, start_time):
    part_file_name = f"{file_path}.part{part_number}"
    with open(file_path, "rb") as source_file:
        source_file.seek(start)
        with open(part_file_name, "wb") as part_file:
            total_length = end - start + 1
            downloaded = 0
            while downloaded < total_length:
                chunk = source_file.read(min(4096, total_length - downloaded))
                if not chunk:
                    break
                part_file.write(chunk)
                downloaded += len(chunk)
                progress[part_number] = int((downloaded / total_length) * 100)
                display_progress(file_path, progress, start_time)
    print(f"Đã tải xong phần {part_number + 1}")

# Hàm ghép tất cả các phần lại thành file hoàn chỉnh
def merge_file_parts(file_name, total_parts, output_file_name):
    try:
        with open(output_file_name, "wb") as merged_file:
            for part_number in range(total_parts):
                part_file_name = f"{file_name}.part{part_number}"
                print(f"Đang ghép file phần: {part_file_name}")
                with open(part_file_name, "rb") as part_file:
                    merged_file.write(part_file.read())
        print(f"Đã ghép xong file hoàn chỉnh: {output_file_name}")
    except Exception as e:
        print(f"Lỗi khi ghép các phần của file: {e}")

# Hàm tải xuống file với 4 kết nối song song
def download_file_parallel(file_path, total_parts):
    file_size = os.path.getsize(file_path)
    part_size = file_size // total_parts
    progress = [0] * total_parts
    start_time = time.time()

    threads = []
    for part_number in range(total_parts):
        start = part_number * part_size
        end = start + part_size - 1 if part_number < total_parts - 1 else file_size - 1
        thread = threading.Thread(target=download_part, args=(file_path, start, end, part_number, progress, start_time))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    # Ghép các phần lại thành file hoàn chỉnh với tên mới
    output_file_name = f"{os.path.splitext(file_path)[0]}_downloaded{os.path.splitext(file_path)[1]}"
    merge_file_parts(file_path, total_parts, output_file_name)
    print("Tải xuống hoàn tất.")

# Hàm đọc danh sách file từ input.txt
def read_input_file(file_path):
    with open(file_path, "r") as file:
        return [line.strip() for line in file.readlines()]

# Yêu cầu danh sách file từ server
def get_file_list():
    try:
        client_socket.sendto("GET_FILE_LIST".encode(), (SERVER_IP, SERVER_PORT))
        data, _ = client_socket.recvfrom(BUFFER_SIZE)
        file_list = data.decode()
        print("Danh sách file nhận được từ Server:")
        print(file_list)
        return file_list
    except Exception as e:
        print(f"Lỗi khi lấy danh sách file: {e}")

# Hàm chính để duyệt file input.txt và tải xuống các file mới
def main():
    input_file = "input.txt"
    downloaded_files = set()

    while True:
        try:
            files_to_download = read_input_file(input_file)
            new_files = [file for file in files_to_download if file not in downloaded_files]

            if new_files:
                for file_name in new_files:
                    print(f"Bắt đầu tải file: {file_name}")
                    download_file_parallel(file_name, 4)
                    downloaded_files.add(file_name)
            else:
                print("Không có file mới cần tải.")

            time.sleep(5)
        except Exception as e:
            print(f"Lỗi khi lấy danh sách file: {e}")

# Chạy chương trình
if __name__ == "__main__":
    main()

# Ví dụ sử dụng
# if __name__ == "__main__":
#     file_path = "File1.zip"
#     total_parts = 4
#     file_size = os.path.getsize(file_path)
#     part_size = file_size // total_parts
#     progress = [0] * total_parts
#     start_time = time.time()

#     # Tải xuống các phần của file
#     for part_number in range(total_parts):
#         start = part_number * part_size
#         end = start + part_size - 1 if part_number < total_parts - 1 else file_size - 1
#         download_part(file_path, start, end, part_number, progress, start_time)

#     # Ghép các phần lại thành file hoàn chỉnh với tên mới
#     output_file_name = "NewFile.zip"
#     merge_file_parts(file_path, total_parts, output_file_name)
#     print("Tải xuống hoàn tất.")

# # Vòng lặp chính
# if __name__ == "__main__":
#     downloaded_files = []
#     while True:
#         new_files = read_input_file(downloaded_files)

#         if new_files:
#             for file_name in new_files:
#                 print(f"Bắt đầu tải file: {file_name}")
#                 download_file(file_name)
#                 downloaded_files.append(file_name)
#         else:
#             print("Không có file mới cần tải.")

#         time.sleep(5)

#         print("\nLựa chọn:")
#         print("1. Xem danh sách file")
#         print("2. Thoát")
#         choice = input("Nhập lựa chọn của bạn (1/2): ")

#         if choice == "1":
#             get_file_list()
#         elif choice == "2":
#             print("Thoát chương trình.")
#             break
#         else:
#             print("Lựa chọn không hợp lệ. Vui lòng thử lại.")