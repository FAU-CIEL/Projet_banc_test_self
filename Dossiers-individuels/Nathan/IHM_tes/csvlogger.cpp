#include "csvlogger.h"
#include <QFile>
#include <QTextStream>
#include <QDir>

/**
 * @brief Construit le logger CSV.
 * @param filePath Chemin du fichier CSV demandé.
 *
 * Le chemin fourni est ignoré ici, et le fichier est placé dans le dossier
 * Document de l'utilisateur sous le nom "mesures.csv"
 */
CsvLogger::CsvLogger(const QString &filePath)
{
    Q_UNUSED(filePath);
    m_filePath = QDir::homePath() + "/Documents/mesures.csv";

    QFile file(m_filePath);
    if (file.exists() && file.size() > 0)
        m_headerWritten = true;
    else
        m_headerWritten = false;
}
/**
 * @brief Ecrit l'en-tete du fichier CSV si nécessaire.
 *
 * L'en-tete n'est écrit qu'une seule fois, lors du premier appel.
 */
void CsvLogger::writeHeaderIfNeeded()
{
    if (m_headerWritten)
        return;

    QFile file(m_filePath);
    if (file.open(QIODevice::Append | QIODevice::Text)) {
        QTextStream out(&file);
        out << "timestamp;currentA;voltageV;inductanceH\n";
        m_headerWritten = true;
    }
}

/**
 * @brief Ajoute une mesure dans le fichier CSV.
 * @param m Mesure à enregistrer.
 *
 * La ligne contient l'horodatage ISO puis les valeurs de courant,
 * tension, indcutance.
 */
void CsvLogger::log(const Measurement &m)
{
    writeHeaderIfNeeded();

    QFile file(m_filePath);
    if (!file.open(QIODevice::Append | QIODevice::Text))
        return;

    QTextStream out(&file);
    out << m.timestamp.toString(Qt::ISODate) << ";"
        << m.currentA << ";"
        << m.voltageV << ";"
        << m.inductanceH << "\n";
}
