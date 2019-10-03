from sys import argv, stdout
from extractLSB import extract_LSB_data
from io import BytesIO
from PIL import Image

PROGRESS_LINE_LEN = 20

def G(idx):
    b = ((idx + 1) * 309030853) & 0xff
    k = ((idx + 2) * 209897853) & 0xff
    return b ^ k

def rightRotate(num, amount):
    for i in range(amount):
        num = ((num >> 1) & 0xff) + (num & 1) * 128
    
    return num & 0xff

def leftRotate(num, amount):
    for i in range(amount):
        num = ((num << 1) & 0xff) + ((num & 128) // 128)
    
    return num & 0xff
    
def write_progress(prcentage):
    buf = ""
    buf += "\r("    # reset the line
    buf += f"{('=' * int(prcentage        * PROGRESS_LINE_LEN))}"
    buf += f"{('-' * int((1 - prcentage)  * PROGRESS_LINE_LEN))}"
    buf += ")("
    buf += f"{prcentage * 100:06.02f}%"
    buf += ")"
    stdout.write(buf)
    
def printhelp():
    print(f"USAGE: {argv[0]} <bmp_image> <out_file>")
    exit(0)

if __name__ == '__main__':
    if len(argv) < 3:
        printhelp()
        
    img = Image.open(argv[1])
    extracted_f = BytesIO()
    
    extract_LSB_data(img, extracted_f)
    
    extracted_f.seek(0)
    data = extracted_f.read()
    
    data_len = len(data)

    decoded_data = [0] * data_len
    f = open(argv[2], 'wb')

    num = 0
    counter = 0
    for i in range(data_len):
        x = data[i]

        # generate all the Gs from the beginning
        firstF = G(num)
        num += 1
        secondF = G(num)
        num += 1

        x = leftRotate(x, 3)
        x ^= secondF
        x = rightRotate(x, 7)
        x ^= firstF

        decoded_data[i] = x

        prcentage_done = (i / data_len)

        write_progress(prcentage_done)


    f.write(bytes(decoded_data))
    f.close()
