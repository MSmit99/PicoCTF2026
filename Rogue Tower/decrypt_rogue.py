import base64

encoded = 'R19WWHthcE1FBlJCC2pVBVtaakMIQgVEaAVXAgANV1cASw=='
decoded = base64.b64decode(encoded)

imsi = '310410176578566'

# Try every possible substring of the IMSI as a key
for length in range(4, len(imsi)+1):
    for start in range(len(imsi) - length + 1):
        candidate = imsi[start:start+length]
        key = candidate.encode()
        try:
            flag = bytes([decoded[i] ^ key[i % len(key)] for i in range(len(decoded))])
            text = flag.decode('ascii')
            # Check if it looks like a readable flag
            if text.startswith('picoCTF{'):
                print(f'Key [{candidate}] (pos {start}, len {length}): {text}')
        except:
            pass