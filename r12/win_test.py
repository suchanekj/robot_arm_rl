import usb

print(usb.core.find(idVendor=0x0403, idProduct=0x6001))
