#include "databasemanager.h"
#include <QDateTime>

/**
 * @brief Constructeur Initialise la configuration de la base MariaDB/MySQL.
 * @param parent Objet parent Qt.
 */
DatabaseManager::DatabaseManager(QObject *parent)
    : QObject(parent)
{
    m_db = QSqlDatabase::addDatabase("QMYSQL");
    m_db.setHostName("localhost");
    m_db.setPort(3306);
    m_db.setDatabaseName("banc_inductance");
    m_db.setUserName("user");
    m_db.setPassword("admin");
}

/**
 * @brief DatabaseManager Ferme la connexion si nécessaire.
 */
DatabaseManager::~DatabaseManager()
{
    disconnect();
}

/**
 * @brief Ouvre la connexion à la base et crée les tables si elles n'existent pas.
 * @return true si la connexion est établie, false sinon.
 */
bool DatabaseManager::connect()
{
    if (!m_db.open()){
        qDebug() << "BD Erreur de connexion : " << m_db.lastError().text();
        return false;
    }

    //Création des tables
    QSqlQuery query;

    query.exec(
        "CREATE TABLE IF NOT EXISTS tests ("
        "id INT AUTO_INCREMENT PRIMARY KEY,"
        "timestamp DATETIME NOT NULL,"
        "n_echantillons INT NOT NULL,"
        "frequence DOUBLE NOT NULL"
        ")"
        );

    query.exec(
        "CREATE TABLE IF NOT EXISTS mesures ("
        "id INT AUTO_INCREMENT PRIMARY KEY,"
        "test_id INT NOT NULL,"
        "temps DOUBLE NOT NULL,"
        "courant DOUBLE NOT NULL,"
        "tension DOUBLE NOT NULL,"
        "inductance DOUBLE NOT NULL,"
        "FOREIGN KEY (test_id) REFERENCES tests(id)"
        ")"
        );

    query.exec(
        "CREATE TABLE IF NOT EXISTS historique ("
        "id INT AUTO_INCREMENT PRIMARY KEY,"
        "test_id INT NOT NULL,"
        "timestamp DATETIME NOT NULL,"
        "statut VARCHAR(50),"
        "FOREIGN KEY (test_id) REFERENCES tests(id)"
        ")"
        );

    qDebug() << "BD Connectée à MariaDB";
    return true;
}

/**
 * @brief Ferme proprement la connexion à la base.
 */
void DatabaseManager::disconnect()
{
    if(m_db.isOpen())
        m_db.close();
}

/**
 * @brief Crée un nouveau test dans la base.
 * @param nEchantillons Nombre d'échantillons prévus.
 * @param frequence Frequence d'acquisition.
 * @return L'identifiant du test créé.
 */
int DatabaseManager::createTest(int nEchantillons, double frequence)
{
    QSqlQuery query;
    query.prepare(
        "INSERT INTO tests (timestamp, n_echantillons, frequence) "
        "VALUES (:timestamp, :n, :fe)"
        );
    query.bindValue(":timestamp", QDateTime::currentDateTime().toString("yyyy-MM-dd hh:mm:ss"));
    query.bindValue(":n", nEchantillons);
    query.bindValue(":fe", frequence);

    if(!query.exec()){
        qDebug() << "BD Erreur creation de la table: "<<query.lastError().text();
        return -1;
    }

    int testId = query.lastInsertId().toInt();
    qDebug() << "BD Test crée avec id=" << testId;
    return testId;
}

/**
 * @brief Insère une mesure dans la table 'mesure'.
 * @param testId Identifiant du test associé.
 * @param m Mesure à insérer.
 */
void DatabaseManager::insertMesure(int testId, const Measurement &m)
{
    QSqlQuery query;
    query.prepare(
        "INSERT INTO mesures (test_id, temps, courant, tension, inductance) "
        "VALUES (:test_id, :temps, :courant, :tension, :inductance)"
        );
    query.bindValue(":test_id", testId);
    query.bindValue(":temps", m.timeS);
    query.bindValue(":courant", m.currentA);
    query.bindValue(":tension", m.voltageV);
    query.bindValue(":inductance", m.inductanceH);

    if (!query.exec())
        qDebug() << "BD Erreur Mesure :" <<query.lastError().text();
}

/**
 * @brief Ajoute une entrée dans l'historique d'un test.
 * @param testId Identifiant du test.
 * @param statut Texte décrivant l'événement.
 */
void DatabaseManager::insertHistorique(int testId, const QString &statut)
{
    QSqlQuery query;
    query.prepare(
        "INSERT INTO historique (test_id, timestamp, statut) "
        "VALUES (:test_id, :timestamp, :statut)"
        );
    query.bindValue(":test_id", testId);
    query.bindValue(":timestamp", QDateTime::currentDateTime().toString("yyyy-MM-dd hh:mm:ss"));
    query.bindValue(":statut", statut);

    if(!query.exec())
        qDebug() << "BD Erreur Historique" <<query.lastError().text();
}
