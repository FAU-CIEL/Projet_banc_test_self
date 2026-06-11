
#ifndef CSVLOGGER_H
#define CSVLOGGER_H

#pragma once

#include <QString>
#include "measurementmodel.h"

/**
 * @brief Classe permettant d'enregistrer des mesures dans une fichier CSV.
 *
 * CsvLogger écrit les donnéesde type Measurement dans un ficher CSV.
 * Il gere automatiquement de l'en-tete lors de la première insertion.
 */
class CsvLogger
{
public:
    /**
     * @brief Constructeur.
     * @param filePath Chemin du fichier CSV à utiliser pour l'enregistrement.
     */
    explicit CsvLogger(const QString &filePath);

    /**
     * @brief Ajoute une mesure dans le fichier CSV.
     * @param m La mesure à enregistrer.
     */
    void log(const Measurement &m);

private:
    QString m_filePath; /**< Chemin du fichier CSV. */
    bool m_headerWritten = false; /**< Indique si l'en-tete a déjà été écrit. */

    /**
     * @brief Ecrit l'en-tete du fichier CSV
     *
     * Cette méthode est appelé avant l'écriture des donnéespour garantir
     * que l'en-tete est présent une seule fois.
     */
    void writeHeaderIfNeeded();
};



#endif // CSVLOGGER_H
