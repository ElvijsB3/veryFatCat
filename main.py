import struct
import sys
import tabulate
import hashlib

image_location = sys.argv[1]

# Read binary data
with open(image_location, mode="rb") as raw_data:
    # Read File in bytes
    data = raw_data.read()

# Read boot record
with open(image_location, 'rb') as f:
    boot_sector = f.read(512)

    # Set variables for VBR
    sector_size = 2 ** struct.unpack_from("B", boot_sector, 0x6C)[0] #bytes per sector
    cluster_size = 2 ** struct.unpack_from("B", boot_sector, 0x6D)[0] * sector_size  # 3 pow 2 * 512 = 4096
    fat_offset = struct.unpack_from("<I", boot_sector, 0x50)[0] * sector_size
    fat_size = struct.unpack_from("<I", boot_sector, 0x54)[0] * sector_size
    datazone = struct.unpack_from("I", boot_sector, 0x58)[0] * sector_size

def get_vbr_information():
    # Print VBR information
    data = [
        {
            'Sector size': sector_size,
            'Cluster size': cluster_size,
            'FAT offset': fat_offset,
            'FAT size': fat_size,
            'Datazone': datazone
        }
    ]
    headers = data[0].keys()
    table = tabulate.tabulate([d.values() for d in data], headers=headers, tablefmt='grid')
    print(table)


def extract_non_fragmented_file(cluster_size, datazone):
    # Retrive non fragmented file
    file_size = int(input("Enter file size: "))  # 918557
    first_cluster = int(input("Enter first cluster: "))  # Replace with the first cluster of the file 280
    file_name = input("Enter file name: ")  # OurFile34.jpg

    output = bytearray()
    clusters = (file_size // cluster_size) + 1

    for idx in range(clusters):
        # Calculate the offsets of the fragment
        start_offset_in_bytes = datazone + (first_cluster + idx - 2) * cluster_size
        end_offset_in_bytes = start_offset_in_bytes + (first_cluster + idx - 1) * cluster_size
        # Add the fragment to the bytearray
        output.extend(bytearray(data[start_offset_in_bytes: end_offset_in_bytes]))
    # Create a file with the recovered byte data
    f = open(file_name, "wb")
    f.write(output[:file_size])
    f.close()
    print(f"\nFile saved as '{file_name}'")


def check_file_integrity():
    file1 = input("Enter file name: ")
    file2 = input("Enter file name: ")
    hash1 = hashlib.sha256(open(file1, 'rb').read()).hexdigest()
    hash2 = hashlib.sha256(open(file2, 'rb').read()).hexdigest()
    data = [
        {
            'File 1 name': file1,
            'File 1 SHA256': hash1,
        },
        {
            'File 2 name': file2,
            'File 2 SHA256': hash2,
        }
    ]
    headers = data[0].keys()
    table = tabulate.tabulate([d.values() for d in data], headers=headers, tablefmt='grid')
    print(table)

    if hash1 == hash2:
        print("Files are identical")
    else:
        print("Files are different")


if __name__ == '__main__':

    while True:
        print("\n======THIS CODE IS EXAMPLE=======\n")
        print("Please select a function to run:")
        print("1. Get VBR Information")
        print("2. Extract non-fragmented file")
        print("3. File integrity check (Compare files SHA256)")
        print("Enter 'exit' to close the program")

        user_input = input("Enter your choice: ")

        if user_input == "1":
            get_vbr_information()
            print("\n")
        elif user_input == "2":
            extract_non_fragmented_file(cluster_size, datazone)
            print("\n")
        elif user_input == "3":
            check_file_integrity()
            print("\n")
        elif user_input.lower() == "exit":
            print("Exiting program...")
            break
        else:
            print("Invalid input. Please try again.")
    sys.exit()
