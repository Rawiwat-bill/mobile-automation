*** Variables ***
${APP_PACKAGE}              com.bangkokbank.blue.dev
${APP_ACTIVITY}             com.bangkokbank.blue.MainActivity
${ANDROID_RESOLVER_SIT_PACKAGE}    com.bangkokbank.blue.sit
${ANDROID_RESOLVER_DEV_PACKAGE}    com.bangkokbank.blue.dev
&{ANDROID_RESOLVER_TARGET_LABELS}    com.bangkokbank.blue.sit=NCBD-SIT    com.bangkokbank.blue.dev=NCBD-DEV
${APPIUM_URL}               http://127.0.0.1:4723
${DEVICE_NAME}              Android Emulator
${DEVICE_UDID}              ${EMPTY}
${APK_PATH}                 ${CURDIR}/../../apps/android/app-dev.apk

${NCBD_LOADING_TIMEOUT}     40s

${BLUR_AFTER_CITIZEN_Y}     780
${BLUR_AFTER_DOB_Y}         1095
${BLUR_AFTER_MOBILE_Y}      1600

${DOB_DRAG_DURATION}        400
${DOB_COARSE_START_RATIO}   0.70
${DOB_COARSE_END_RATIO}     0.30
${DOB_FINE_START_RATIO}     0.60
${DOB_FINE_END_RATIO}       0.40
${DOB_SETTLE_TIME}          0.3

&{MONTH_MAP}        01=January    02=February    03=March    04=April    05=May    06=June    07=July    08=August    09=September    10=October    11=November    12=December
&{MONTH_INDEXES}    January=1     February=2     March=3     April=4     May=5     June=6     July=7     August=8     September=9      October=10     November=11     December=12
