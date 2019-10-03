from PIL import Image
from sys import argv

def extract_LSB_data(img, out):
    data = img.load()

    for i in range(img.width):
        for j in range(img.height):
            pixel = data[i, j]

            byte = 0
            byte |= (pixel[0] & 0b111)
            byte |= (pixel[1] & 0b111) << 8 - 5
            byte |= (pixel[2] & 0b11) << 8 - 2

            out.write(bytes([byte]))


def printhelp():
    print(f"USAGE: {argv[0]} <bmp_image> <out_file>")
    exit(0)

if __name__ == '__main__':
    if len(argv) < 3:
        printhelp()
        
    img = Image.open(argv[1])
    out = open(argv[2], 'wb')
    
    extract_LSB_data(img, out)
    
    out.close()
    img.close()

