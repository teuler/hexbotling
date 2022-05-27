
"""
direction     := int(dir *100)
sensor values := int(Ain *1_000); 1 == 1 mV   : 2 Byte * 6  == 12 Bytes
"""
import array

def encode(dir, rev, vel):
  data = bytearray([0]*4)
  data[1] = min(max(0, int(128 +dir*128)), 255)
  return data

def decode(data):
  dir = round((data[1]-128) /128 +0.005, 2)
  return dir


msg = encode(-1.0, False, 1.2)
print(decode(msg))
