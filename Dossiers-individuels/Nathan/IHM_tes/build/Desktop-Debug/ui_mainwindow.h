/********************************************************************************
** Form generated from reading UI file 'mainwindow.ui'
**
** Created by: Qt User Interface Compiler version 5.15.15
**
** WARNING! All changes made in this file will be lost when recompiling UI file!
********************************************************************************/

#ifndef UI_MAINWINDOW_H
#define UI_MAINWINDOW_H

#include <QtCore/QVariant>
#include <QtWidgets/QApplication>
#include <QtWidgets/QDoubleSpinBox>
#include <QtWidgets/QFormLayout>
#include <QtWidgets/QGridLayout>
#include <QtWidgets/QGroupBox>
#include <QtWidgets/QHBoxLayout>
#include <QtWidgets/QHeaderView>
#include <QtWidgets/QLabel>
#include <QtWidgets/QLineEdit>
#include <QtWidgets/QMainWindow>
#include <QtWidgets/QPlainTextEdit>
#include <QtWidgets/QPushButton>
#include <QtWidgets/QSpacerItem>
#include <QtWidgets/QTabWidget>
#include <QtWidgets/QTableView>
#include <QtWidgets/QVBoxLayout>
#include <QtWidgets/QWidget>

QT_BEGIN_NAMESPACE

class Ui_MainWindow
{
public:
    QWidget *centralwidget;
    QVBoxLayout *mainLayout;
    QTabWidget *tabWidget;
    QWidget *tabConfig;
    QVBoxLayout *configLayout;
    QGroupBox *groupConfig;
    QFormLayout *formLayoutConfig;
    QLabel *labelDuree;
    QDoubleSpinBox *spinNEchantillons;
    QLabel *labelFe;
    QDoubleSpinBox *spinFe;
    QHBoxLayout *layoutButtons;
    QPushButton *btnStart;
    QPushButton *btnStop;
    QPlainTextEdit *plainTextEdit;
    QSpacerItem *verticalSpacerConfig;
    QWidget *tabRealtime;
    QVBoxLayout *realtimeLayout;
    QGroupBox *groupValues;
    QGridLayout *gridValues;
    QLabel *valueL;
    QLabel *labelU;
    QLabel *labelI;
    QLabel *labelL;
    QLabel *valueU;
    QLabel *valueI;
    QGroupBox *groupGraph;
    QVBoxLayout *graphLayout;
    QLabel *placeholderGraph;
    QWidget *tabHistory;
    QVBoxLayout *historyLayout;
    QHBoxLayout *searchLayout;
    QLineEdit *editSearch;
    QPushButton *btnClearHistory;
    QTableView *tableHistory;

    void setupUi(QMainWindow *MainWindow)
    {
        if (MainWindow->objectName().isEmpty())
            MainWindow->setObjectName(QString::fromUtf8("MainWindow"));
        MainWindow->resize(1000, 650);
        centralwidget = new QWidget(MainWindow);
        centralwidget->setObjectName(QString::fromUtf8("centralwidget"));
        mainLayout = new QVBoxLayout(centralwidget);
        mainLayout->setObjectName(QString::fromUtf8("mainLayout"));
        tabWidget = new QTabWidget(centralwidget);
        tabWidget->setObjectName(QString::fromUtf8("tabWidget"));
        tabConfig = new QWidget();
        tabConfig->setObjectName(QString::fromUtf8("tabConfig"));
        configLayout = new QVBoxLayout(tabConfig);
        configLayout->setObjectName(QString::fromUtf8("configLayout"));
        groupConfig = new QGroupBox(tabConfig);
        groupConfig->setObjectName(QString::fromUtf8("groupConfig"));
        formLayoutConfig = new QFormLayout(groupConfig);
        formLayoutConfig->setObjectName(QString::fromUtf8("formLayoutConfig"));
        labelDuree = new QLabel(groupConfig);
        labelDuree->setObjectName(QString::fromUtf8("labelDuree"));

        formLayoutConfig->setWidget(0, QFormLayout::LabelRole, labelDuree);

        spinNEchantillons = new QDoubleSpinBox(groupConfig);
        spinNEchantillons->setObjectName(QString::fromUtf8("spinNEchantillons"));
        spinNEchantillons->setMinimum(0.100000000000000);
        spinNEchantillons->setMaximum(1000000000000000044885712678075916785549312.000000000000000);
        spinNEchantillons->setValue(1.000000000000000);

        formLayoutConfig->setWidget(0, QFormLayout::FieldRole, spinNEchantillons);

        labelFe = new QLabel(groupConfig);
        labelFe->setObjectName(QString::fromUtf8("labelFe"));

        formLayoutConfig->setWidget(1, QFormLayout::LabelRole, labelFe);

        spinFe = new QDoubleSpinBox(groupConfig);
        spinFe->setObjectName(QString::fromUtf8("spinFe"));
        spinFe->setDecimals(2);
        spinFe->setMinimum(0.000000000000000);
        spinFe->setMaximum(900.000000000000000);
        spinFe->setSingleStep(0.000001000000000);
        spinFe->setValue(10.000000000000000);

        formLayoutConfig->setWidget(1, QFormLayout::FieldRole, spinFe);


        configLayout->addWidget(groupConfig);

        layoutButtons = new QHBoxLayout();
        layoutButtons->setObjectName(QString::fromUtf8("layoutButtons"));
        btnStart = new QPushButton(tabConfig);
        btnStart->setObjectName(QString::fromUtf8("btnStart"));

        layoutButtons->addWidget(btnStart);

        btnStop = new QPushButton(tabConfig);
        btnStop->setObjectName(QString::fromUtf8("btnStop"));

        layoutButtons->addWidget(btnStop);


        configLayout->addLayout(layoutButtons);

        plainTextEdit = new QPlainTextEdit(tabConfig);
        plainTextEdit->setObjectName(QString::fromUtf8("plainTextEdit"));

        configLayout->addWidget(plainTextEdit);

        verticalSpacerConfig = new QSpacerItem(20, 200, QSizePolicy::Minimum, QSizePolicy::Expanding);

        configLayout->addItem(verticalSpacerConfig);

        tabWidget->addTab(tabConfig, QString());
        tabRealtime = new QWidget();
        tabRealtime->setObjectName(QString::fromUtf8("tabRealtime"));
        realtimeLayout = new QVBoxLayout(tabRealtime);
        realtimeLayout->setObjectName(QString::fromUtf8("realtimeLayout"));
        groupValues = new QGroupBox(tabRealtime);
        groupValues->setObjectName(QString::fromUtf8("groupValues"));
        gridValues = new QGridLayout(groupValues);
        gridValues->setObjectName(QString::fromUtf8("gridValues"));
        valueL = new QLabel(groupValues);
        valueL->setObjectName(QString::fromUtf8("valueL"));

        gridValues->addWidget(valueL, 2, 1, 1, 1);

        labelU = new QLabel(groupValues);
        labelU->setObjectName(QString::fromUtf8("labelU"));

        gridValues->addWidget(labelU, 1, 0, 1, 1);

        labelI = new QLabel(groupValues);
        labelI->setObjectName(QString::fromUtf8("labelI"));

        gridValues->addWidget(labelI, 0, 0, 1, 1);

        labelL = new QLabel(groupValues);
        labelL->setObjectName(QString::fromUtf8("labelL"));

        gridValues->addWidget(labelL, 2, 0, 1, 1);

        valueU = new QLabel(groupValues);
        valueU->setObjectName(QString::fromUtf8("valueU"));

        gridValues->addWidget(valueU, 1, 1, 1, 1);

        valueI = new QLabel(groupValues);
        valueI->setObjectName(QString::fromUtf8("valueI"));
        valueI->setMargin(0);

        gridValues->addWidget(valueI, 0, 1, 1, 1);


        realtimeLayout->addWidget(groupValues);

        groupGraph = new QGroupBox(tabRealtime);
        groupGraph->setObjectName(QString::fromUtf8("groupGraph"));
        graphLayout = new QVBoxLayout(groupGraph);
        graphLayout->setObjectName(QString::fromUtf8("graphLayout"));
        placeholderGraph = new QLabel(groupGraph);
        placeholderGraph->setObjectName(QString::fromUtf8("placeholderGraph"));
        placeholderGraph->setAlignment(Qt::AlignCenter);

        graphLayout->addWidget(placeholderGraph);


        realtimeLayout->addWidget(groupGraph);

        tabWidget->addTab(tabRealtime, QString());
        tabHistory = new QWidget();
        tabHistory->setObjectName(QString::fromUtf8("tabHistory"));
        historyLayout = new QVBoxLayout(tabHistory);
        historyLayout->setObjectName(QString::fromUtf8("historyLayout"));
        searchLayout = new QHBoxLayout();
        searchLayout->setObjectName(QString::fromUtf8("searchLayout"));
        editSearch = new QLineEdit(tabHistory);
        editSearch->setObjectName(QString::fromUtf8("editSearch"));

        searchLayout->addWidget(editSearch);

        btnClearHistory = new QPushButton(tabHistory);
        btnClearHistory->setObjectName(QString::fromUtf8("btnClearHistory"));

        searchLayout->addWidget(btnClearHistory);


        historyLayout->addLayout(searchLayout);

        tableHistory = new QTableView(tabHistory);
        tableHistory->setObjectName(QString::fromUtf8("tableHistory"));

        historyLayout->addWidget(tableHistory);

        tabWidget->addTab(tabHistory, QString());

        mainLayout->addWidget(tabWidget);

        MainWindow->setCentralWidget(centralwidget);

        retranslateUi(MainWindow);

        tabWidget->setCurrentIndex(1);


        QMetaObject::connectSlotsByName(MainWindow);
    } // setupUi

    void retranslateUi(QMainWindow *MainWindow)
    {
        MainWindow->setWindowTitle(QCoreApplication::translate("MainWindow", "Banc de test inductance - IHM Qt", nullptr));
        groupConfig->setTitle(QCoreApplication::translate("MainWindow", "Param\303\250tres du test", nullptr));
        labelDuree->setText(QCoreApplication::translate("MainWindow", "Nombre d'\303\251chantillon :", nullptr));
        labelFe->setText(QCoreApplication::translate("MainWindow", "Fr\303\251quence \303\251chantillonnage :", nullptr));
        btnStart->setText(QCoreApplication::translate("MainWindow", "D\303\251marrer le test", nullptr));
        btnStop->setText(QCoreApplication::translate("MainWindow", "Arr\303\252ter le test", nullptr));
        tabWidget->setTabText(tabWidget->indexOf(tabConfig), QCoreApplication::translate("MainWindow", "Configuration", nullptr));
        groupValues->setTitle(QCoreApplication::translate("MainWindow", "Mesures instantan\303\251es", nullptr));
        valueL->setText(QCoreApplication::translate("MainWindow", "0.0", nullptr));
        labelU->setText(QCoreApplication::translate("MainWindow", "Tension (V) :", nullptr));
        labelI->setText(QCoreApplication::translate("MainWindow", "Courant (A) :", nullptr));
        labelL->setText(QCoreApplication::translate("MainWindow", "Inductance (mH) :", nullptr));
        valueU->setText(QCoreApplication::translate("MainWindow", "0.0", nullptr));
        valueI->setText(QCoreApplication::translate("MainWindow", "0.0", nullptr));
        groupGraph->setTitle(QCoreApplication::translate("MainWindow", "Graphique temps r\303\251el", nullptr));
        placeholderGraph->setText(QString());
        tabWidget->setTabText(tabWidget->indexOf(tabRealtime), QCoreApplication::translate("MainWindow", "Temps r\303\251el", nullptr));
        editSearch->setPlaceholderText(QCoreApplication::translate("MainWindow", "Rechercher...", nullptr));
        btnClearHistory->setText(QCoreApplication::translate("MainWindow", "Effacer l'historique", nullptr));
        tabWidget->setTabText(tabWidget->indexOf(tabHistory), QCoreApplication::translate("MainWindow", "Historique", nullptr));
    } // retranslateUi

};

namespace Ui {
    class MainWindow: public Ui_MainWindow {};
} // namespace Ui

QT_END_NAMESPACE

#endif // UI_MAINWINDOW_H
