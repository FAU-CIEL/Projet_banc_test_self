#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#pragma once

#include <QMainWindow>
#include <QTimer>
#include <QStandardItemModel>
#include <QtCharts/QChartView>
#include <QtCharts/QLineSeries>
#include <QtCharts/QValueAxis>
#include "comminterface.h"
#include "csvlogger.h"
#include "measurementmodel.h"
#include "UartComm.h"
#include "databasemanager.h"
#include <QComboBox>

QT_BEGIN_NAMESPACE
namespace Ui { class MainWindow; }
QT_END_NAMESPACE

using namespace QtCharts;

/**
 * @brief Fenetre principale de l'IHM.
 *
 * Cette classe gère l'interface utilisateur, la communication avec
 * le périphereique, l'affichage des mesures en temps réel, l'historique, ainsi
 * que l'export CSV.
 */
class MainWindow : public QMainWindow
{
    Q_OBJECT

public:
    /**
     * @brief Construit la fenetre principale.
     * @param parent Parent Qt.
     */
    explicit MainWindow(QWidget *parent = nullptr);

    /**
     * @brief Détruit la fenetre principale.
     */
    ~MainWindow();

private slots:
    /**
     * @brief Démarre le teste et active l'acquisition.
     */
    void onStartTest();

    /**
     * @brief Arrete le teste et stoppe l'acquisition.
     */
    void onStopTest();

    /**
     * @brief Traite une nouvelle mesure reçue.
     * @param m Nouvelle mesure acquise.
     */
    void onNewMeasurement(const Measurement &m);

    /**
     * @brief Met à jour les éléments périodiques de l'interface.
     */
    void onTimerTick();

    /**
     * @brief Filtre l'historique selon le texte saisi.
     * @param text Texte de recherche.
     */
    void onSearchTextChanged(const QString &text);

    /**
     * @brief Vide l'historique des mesures.
     */
    void onClearHistory();


private:
    Ui::MainWindow *ui; ///< Interface graphique générée par Qt Designer.
    CsvLogger m_csv; /**< Gestionnaire d'écriture des mesures dans un fichier CSV. */
    QTimer m_timer; /**< Minuterie pour les mises à jour périodiques. */
    bool m_running = false; /**< Indique si l'acquisition est en cours. */
    QStandardItemModel *m_historyModel; /**< Modèle contenant l'historique des mesures. */
    QChartView *m_chartView; /**< Vue du graphique en temps réel. */
    QLineSeries *m_seriesCourant; /**< Série représentant le courant. */
    QLineSeries *m_seriesTension; /**< Série représentant la tension. */
    QLineSeries *m_seriesInductance; /**< Série représentant l'inductance. */
    QValueAxis *m_axisX; /**< Axe horizontal du graphique. */
    QValueAxis *m_axisY; /**< Axe vertical du graphique. */
    bool m_firstPoint = true; /**< Indique si le premier point du graphe a été ajouté. */
    UartComm *m_uart; /**< Gestionnaire communcation UART. */
    double m_lastValidL = 0.0;  /**< Dernière valeur valide d'inductance. */
    DatabaseManager *m_db;  /**< Gestionnaire de base de données. */
    int m_currentTestId = -1;  /**< Identifiant du teste en cours. */
    QComboBox *m_comboFreqUnit; /**< Sélecteur d'unité de fréquence. */

    /**
     * @brief Met a jour l'affichage en temps réel avec une nouvelle mesure.
     * @param m Mesure à afficher.
     */
    void updateRealtimeDisplay(const Measurement &m);

    /**
     * @brief Charge le contenue CSV dans le modèle d'historique
     */
    void loadCsvIntoHistory();
};

#endif // MAINWINDOW_H
