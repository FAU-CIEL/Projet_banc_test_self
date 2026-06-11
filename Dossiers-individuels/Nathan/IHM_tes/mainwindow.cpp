#include "mainwindow.h"
#include "ui_mainwindow.h"
#include "spiasciicomm.h"
#include "UartComm.h"
#include <QDebug>
#include <QDir>
#include <QFile>
#include <QTextStream>
//#include <time.h>
#include <QMouseEvent>
#include <QDialog>
#include <QVBoxLayout>
#include <QComboBox>

/**
 * @brief Construit la fenetre principale et initialise l'interface.
 *
 * Cette fonction installe les connexions entre les widgets et les slots,
 * initialise le modèle d'historique, configure le graphique temps réel,
 * charge l'historique CSV et ouvre la communication UART.
 * Le mode de communication principale utilisée ici est la communication UART.
 *
 * @param parent Parent Qt
 */
MainWindow::MainWindow(QWidget *parent)
    : QMainWindow(parent),
    ui(new Ui::MainWindow),
    m_csv("mesures.csv"),
    m_uart(nullptr)
{
    ui->setupUi(this);
    m_comboFreqUnit = new QComboBox(this);
    m_comboFreqUnit->addItems({"Hz", "kHz", "MHz", "GHz"});
    m_comboFreqUnit->setObjectName("m_comboFreqUnit");

    QFormLayout *formLayout = qobject_cast<QFormLayout*>(ui->spinFe->parentWidget()->layout());
    if (formLayout) {
        int row;
        QFormLayout::ItemRole role;
        formLayout->getWidgetPosition(ui->spinFe, &row, &role);

        QHBoxLayout *hbox = new QHBoxLayout();
        hbox->addWidget(ui->spinFe);
        hbox->addWidget(m_comboFreqUnit);
        formLayout->setLayout(row, QFormLayout::FieldRole, hbox);
    }

    connect(ui->btnStart, &QPushButton::clicked, this, &MainWindow::onStartTest);
    connect(ui->btnStop, &QPushButton::clicked, this, &MainWindow::onStopTest);

    m_timer.setInterval(100);
    connect(&m_timer, &QTimer::timeout, this, &MainWindow::onTimerTick);

    m_historyModel = new QStandardItemModel(this);
    ui->tableHistory->setModel(m_historyModel);
    m_historyModel->setHorizontalHeaderLabels(
        {"Timestamp", "Courant (A)", "Tension (V)", "Inductance (H)"}
        );

    connect(ui->editSearch, &QLineEdit::textChanged,
            this, &MainWindow::onSearchTextChanged);
    connect(ui->btnClearHistory, &QPushButton::clicked,
            this, &MainWindow::onClearHistory);
    m_db = new DatabaseManager(this);
    m_db->connect();

    // --- Graphique ---
    m_seriesCourant = new QLineSeries();
    m_seriesCourant->setName("Courant (A)");

    m_seriesTension = new QLineSeries();
    m_seriesTension->setName("Tension (V)");

    m_seriesInductance = new QLineSeries();
    m_seriesInductance->setName("Iductance (H)");

    m_chartView = new QChartView(new QChart());
    m_chartView->chart()->addSeries(m_seriesCourant);
    m_chartView->chart()->addSeries(m_seriesTension);
    m_chartView->chart()->addSeries(m_seriesInductance);

    m_axisX = new QValueAxis();
    m_axisY = new QValueAxis();


    m_axisX->setTitleText("Temps (ms)");
    m_axisY->setTitleText("Valeurs");

    m_chartView->chart()->addAxis(m_axisX, Qt::AlignBottom);
    m_chartView->chart()->addAxis(m_axisY, Qt::AlignLeft);

    m_seriesCourant->attachAxis(m_axisX);
    m_seriesCourant->attachAxis(m_axisY);
    m_seriesTension->attachAxis(m_axisX);
    m_seriesTension->attachAxis(m_axisY);
    m_seriesInductance->attachAxis(m_axisX);
    m_seriesInductance->attachAxis(m_axisY);

    m_axisX->setRange(0, 1);
    m_axisY->setRange(0, 50);

    m_chartView->chart()->legend()->setVisible(true);
    m_chartView->chart()->legend()->setAlignment(Qt::AlignBottom);
    ui->graphLayout->addWidget(m_chartView);
    m_chartView->setRenderHint(QPainter::Antialiasing);
    m_chartView->installEventFilter(this);

    QPushButton *btnFullscreen = new QPushButton("Plein ecran", this);
    connect(btnFullscreen, &QPushButton::clicked, this, [this]() {
        QDialog *dialog = new QDialog(this);
        dialog->setWindowTitle("Graphique");
        dialog->setWindowState(Qt::WindowMaximized);

        QChartView *fullView = new QChartView(dialog);
        fullView->setChart(m_chartView->chart());
        fullView->setRenderHint(QPainter::Antialiasing);

        QVBoxLayout *layout = new QVBoxLayout(dialog);
        layout->setContentsMargins(0, 0, 0, 0);
        layout->addWidget(fullView);

        QPushButton *btnClose = new QPushButton("Fermer", dialog);
        connect(btnClose, &QPushButton::clicked, dialog, &QDialog::close);
        layout->addWidget(btnClose);

        dialog->exec();

        // Sauvegarde le chart avant de fermer
        QChart *chart = m_chartView->chart();
        fullView->setChart(new QChart()); // libere le chart de fullView
        m_chartView->setChart(chart);     // remet le chart dans la vue principale
    });
    ui->graphLayout->addWidget(btnFullscreen);


    // --- UART ---
    m_uart = new UartComm("/dev/ttyUSB0", 115200, this);

    connect(m_uart, &CommInterface::newMeasurement,
            this, &MainWindow::onNewMeasurement);

    connect(m_uart, &CommInterface::errorOccurred, this, [this](const QString &err){
        ui->plainTextEdit->appendPlainText("Erreur : " + err);
    });
    connect(m_uart, &CommInterface::statusMessage, this, [this](const QString &msg){
        ui->plainTextEdit->appendPlainText(msg);
    });

    m_uart->open();
}

/**
 * @brief Détruit la fenetre principale.
 */
MainWindow::~MainWindow()
{
    delete ui;
}

/**
 * @brief Lance le test et démarre l'acquisition.
 *
 * Réinitialse les courbes, lit les paramètres de configuration
 * depuis l'interface, envoie les commandes à l'UART puis démarre
 * la minuterie périodique.
 */
void MainWindow::onStartTest()
{
    m_seriesCourant->clear();
    m_seriesTension->clear();
    m_seriesInductance->clear();
    m_historyModel->removeRows(0, m_historyModel->rowCount());

    m_firstPoint = true;
    m_axisY->setRange(0, 60);

    double n = ui->spinNEchantillons->value();
    double fe = ui->spinFe->value();
    QString unit = m_comboFreqUnit ->currentText();
    m_lastValidL = 0.0;

    QString cmd = QString("SET_CONF;N=%1;FE=%2;%3")
                      .arg(n)
                      .arg(fe)
                      .arg(unit);
    m_uart->sendCommand(cmd);

    QTimer::singleShot(500, this, [this]() {
        m_uart->sendCommand("START");
    });

    QTimer::singleShot(500, this, [this]() {
        m_uart->sendCommand("GET_STATUS");
    });
    m_running = true;
    m_timer.start();
    QTimer::singleShot(2000, this, [this]() {
    });
    m_currentTestId = m_db->createTest(
        ui->spinNEchantillons->value(),
        ui->spinFe->value()
        );
    m_db->insertHistorique(m_currentTestId, "STARTED");
}

/**
 * @brief Arrete le teste en cours
 *
 * Envoie la commande d'arret, stop la minuterie et recharge
 * l'historique depuis le fichier CSV.
 */
void MainWindow::onStopTest()
{
    m_uart->sendCommand("STOP\n");
    m_running = false;
    m_timer.stop();
    loadCsvIntoHistory();
}

/**
 * @brief Traite une nouvelle mesure reçue.
 * @param m Mesure reçue à afficher et enregistrer.
 *
 * La mesure est mise à jour dans l'interface, ajoutée au graphique
 * temps réel, puis enregistrée dans le fichier CSV.
 */
void MainWindow::onNewMeasurement(const Measurement &m)
{
    updateRealtimeDisplay(m);
    if (m_currentTestId != -1)
        m_db->insertMesure(m_currentTestId, m);

    QList<QStandardItem*> row;
    row.append(new QStandardItem(m.timestamp.toString(Qt::ISODate)));
    row.append(new QStandardItem(QString::number(m.currentA)));
    row.append(new QStandardItem(QString::number(m.voltageV)));
    row.append(new QStandardItem(QString::number(m.inductanceH)));
    m_historyModel->appendRow(row);
}

/**
 * @brief Met à jour l'affichage en temps réel avec une mesure.
 * @param m Mesure à afficher.
 *
 * Met à jour les champs de valeur, ajoute les points au graphique
 * et ajuste automatiquement l'axe temporel si necessaire.
 */
void MainWindow::updateRealtimeDisplay(const Measurement &m)
{
    ui->valueI->setText(QString::number(m.currentA, 'f', 6) + " A");
    ui->valueU->setText(QString::number(m.voltageV, 'f', 2) + " V");

    if (m.inductanceH > 0)
        m_lastValidL = m.inductanceH;
    ui->valueL->setText(QString::number(m_lastValidL * 1e3, 'f', 3) + " mH");


    double tGraph = m.timeS * 1000.0; // secondes -> ms
    m_seriesCourant->append(tGraph, m.currentA);
    m_seriesTension->append(tGraph, m.voltageV);
    double L = (m.inductanceH > 1e-6) ? m.inductanceH : m_lastValidL;
    m_seriesInductance->append(tGraph, L * 1e3);


    // Axe X
    static qint64 lastUpdate = 0;
    qint64 now = QDateTime::currentMSecsSinceEpoch();

    if (now - lastUpdate > 200) {
        m_axisX->setRange(0, tGraph * 1.1);
        lastUpdate = now;
    }


    // Calcul yMin/yMax sur toute la serie
    double yMin = qMin(m.currentA, m.voltageV);
    double yMax = qMax(m.currentA, m.voltageV);

    for (const QPointF &p : m_seriesTension->points())
    {
        yMin = qMin(yMin, p.y());
        yMax = qMax(yMax, p.y());
    }
    for (const QPointF &p : m_seriesCourant->points())
    {
        yMin = qMin(yMin, p.y());
        yMax = qMax(yMax, p.y());
    }
    for (const QPointF &p : m_seriesInductance->points())
    {
        yMin = qMin(yMin, p.y());
        yMax = qMax(yMax, p.y());
    }

    double margin = (yMax - yMin) * 0.1;
    m_axisY->setRange(yMin - margin, yMax + margin);
}
/**
 * @brief Fonction appelée périodiquement par la minuterie.
 *
 * Si un teste est en cours, cette fonction peut demander une nouvelle
 * mesure à la carte cible. Dans le code actuel, les envois sont commentés.
 */
void MainWindow::onTimerTick()
{
    if (!m_running)
        return;
}

/**
 * @brief Recharge le contenu d'un fichier CSV dans le tableau d'historique.
 *
 * Efface d'abord le modèle actuel, puis relit le fichier "mesures.csv"
 * situé dans le dossier Documents de l'utilisateur.
 */
void MainWindow::loadCsvIntoHistory()
{
    m_historyModel->removeRows(0, m_historyModel->rowCount());

    QString path = QDir::homePath() + "/Documents/mesures.csv";
    QFile file(path);

    if (!file.open(QIODevice::ReadOnly | QIODevice::Text))
        return;

    QTextStream in(&file);

    bool firstLine = true;
    while (!in.atEnd())
    {
        QString line = in.readLine();
        if (line.trimmed().isEmpty())
            continue;

        if (firstLine) {
            firstLine = false;
            continue;
        }

        QStringList parts = line.split(';');
        if (parts.size() < 4)
            continue;

        QList<QStandardItem*> row;
        for (const QString &p : parts)
            row.append(new QStandardItem(p));

        m_historyModel->appendRow(row);
    }
}

/**
 * @brief Filtre les lignes de l'historique selon le texte saisi.
 * @param text Texte de recherche.
 *
 * Chaque cellule du tableau est testée, et les lignes ne correspondant
 * pas au texte saisi sont masquées.
 */
void MainWindow::onSearchTextChanged(const QString &text)
{
    for (int row = 0; row < m_historyModel->rowCount(); row++)
    {
        bool match = false;

        for (int col = 0; col < m_historyModel->columnCount(); col++)
        {
            QString cell = m_historyModel->item(row, col)->text();
            if (cell.contains(text, Qt::CaseInsensitive))
            {
                match = true;
                break;
            }
        }

        ui->tableHistory->setRowHidden(row, !match);
    }
}

/**
 * @brief Efface l'hsitorique des mesures.
 *
 * Le fichier CSV est réinitialisé avec uniquement l'en-tete,
 * puis le tableau de l'interface est rechargé.
 */
void MainWindow::onClearHistory()
{
    QString path = QDir::homePath() + "/Documents/mesures.csv";
    QFile file(path);
    if (file.open(QIODevice::WriteOnly | QIODevice::Text))
    {
        QTextStream out(&file);
        out << "timestamp;currentA;voltageV;inductanceH\n";
    }

    loadCsvIntoHistory();
}


