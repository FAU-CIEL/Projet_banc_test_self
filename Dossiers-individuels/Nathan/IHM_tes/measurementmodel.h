#ifndef MEASUREMENTMODEL_H
#define MEASUREMENTMODEL_H

#pragma once

#include <QDateTime>

/**
 * @brief Structure représentant une mesure acquise par le banc.
 *
 * Cette structure regroupe l'ensemble des valeurs mesurées à un instant donné :
 * courant,tension,inductance et horodatage.
 * Elle est utilisée pour l'affichage temps réel, l'enregistrement CSV
 * et l'insertion en base de données.
 */
struct Measurement
{
    QDateTime timestamp; ///< Horodatage de la mesure.
    double currentA = 0.0; ///< Courant mesuré en ampères.
    double voltageV = 0.0; ///< Tension mesurée en volts.
    double inductanceH = 0.0; ///< Inductance mesurée en henrys.
    double saturationCurrentA = 0.0; ///< Courant de saturation mesurée en ampères.
    double timeS = 0.0; ///< Temps de l'aquisition.
};



#endif // MEASUREMENTMODEL_H
