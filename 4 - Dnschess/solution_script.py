

addresses_file = open('addresses.txt', 'r')
addresses = []

# read the addresses file and store the addresses into the array
# in the form that each entry in `addresses` is a list of four numbers
# which is the ip address
for line in addresses_file.readlines():
    line = line.split('.')
    addresses.append(
        list(map(int, line))
    )

encoded_flag = [121, 90, 184, 188, 236, 211, 223, 221, 153, 165, 182, 172,
                21, 54, 133, 141, 9, 8, 119, 82, 77, 113, 84, 125, 167, 167,
                8, 22, 253, 215]

decoded_flag = [0] * len(encoded_flag)


for address in addresses:
    # address[3] is even
    if(address[3] & 0x1 == 0):
        # because it checks that the address[2] == arg1 in getNextMove
        # then when decoding address[2] will be equal to arg1
        # which is being used as the index
        # So, we can use address[2] instead of arg1 in XORing

        index = address[2] & 0xf
        
        # decrypt two bytes
        decoded_flag[index * 2] = encoded_flag[index * 2] ^ address[1]
        decoded_flag[index * 2 + 1] = encoded_flag[index * 2 + 1] ^ address[1]

print("flag:", ''.join(map(chr, decoded_flag)) + "@flare-on.com")