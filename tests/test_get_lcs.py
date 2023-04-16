import sys 
sys.path.append("..")
from ScreenCompareStrategy import *


str1 = "   旧设备扫码验证支付宝验证发送短信验证人工申诉 联系客服"
str2 = "   旧设备扫码验证支付宝验证发送短信验证人工申诉 联系客服"
ab = ScreenCompareStrategy(LCSComparator())
res, ratio = ab.compare_screen(str1, str2)
print(f"The result is {res} and {ratio}")

str3 = "   旧设备扫码验证发送短信验证人工申诉 联系客服 "
str4 = "   旧设备扫码验证发送短信验证人工申诉 联系客服 我知道了 "
res, ratio = ab.compare_screen(str3, str4)
print(f"The result is {res} and {ratio}")