QT += core gui
QT += widgets charts
QT += serialport
QT += sql

greaterThan(QT_MAJOR_VERSION, 4): QT += widgets

CONFIG += c++17

# You can make your code fail to compile if it uses deprecated APIs.
# In order to do so, uncomment the following line.
#DEFINES += QT_DISABLE_DEPRECATED_BEFORE=0x060000    # disables all the APIs deprecated before Qt 6.0.0

SOURCES += \
    UartComm.cpp \
    csvlogger.cpp \
    databasemanager.cpp \
    main.cpp \
    mainwindow.cpp \
    spiasciicomm.cpp

HEADERS += \
    UartComm.h \
    comminterface.h \
    csvlogger.h \
    databasemanager.h \
    mainwindow.h \
    measurementmodel.h \
    spiasciicomm.h

FORMS += \
    mainwindow.ui

# Default rules for deployment.
qnx: target.path = /tmp/$${TARGET}/bin
else: unix:!android: target.path = /opt/$${TARGET}/bin
!isEmpty(target.path): INSTALLS += target
