## Though /dev/mem read/write gpio status

1. check if exists /dev/mem
adb shell ls /dev/mem

2. check if /system/bin/r 
adb shell which r

3. read register by /system/bin/r
adb shell /system/bin/r 0x01000000


4. LE platform need to push le_32_r to /apps/usr/bin/r
adb push le_32_r  /apps/usr/bin/r
adb shell chmod +x /apps/usr/bin/r

