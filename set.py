# -*- coding: utf-8 -*-

import base64
image='image1'


with open(image,'rb') as f:
    str_1=base64.b64encode(f.read())
print(str_1)


#str_1=""""""
#file_str=open('bb.7z','wb')
#file_str.write(base64.b64decode(str_1))
#file_str.close()

