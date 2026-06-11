#include "spiasciicomm.h"
#include <QDebug>

/**
 * @file spiasciicomm.cpp
 * @brief Implémentation de la classe SpiAsciiComm.
 *
 * Cette classe simule ou implémente une communication SPI envoyant
 * et recevant des trames ASCII.
 * Elle dérive de CommInterface et fournit les méthodes nécessaires
 * pour ouvrir, fermer et envoyer des commandes via SPI.
 */

SpiAsciiComm::SpiAsciiComm(QObject *parent)
    : CommInterface(parent)
{
}

/**
 * @brief Ouvre la communication SPI.
 *
 * Cette méthode devra etre complétée avec l'initialisation réelle du bus SPI.
 *
 * @return false pour l'instant car non implémenté.
 */
bool SpiAsciiComm::open()
{
    // TODO : implémenter l'ouverture SPI
    return false;
}

/**
 * @brief Ferme la communication SPI.
 *
 * Cette méthode devra libérer les ressources SPI utilisées.
 */
void SpiAsciiComm::close()
{
    // TODO : implémenter la fermeture SPI
}

/**
 * @brief Envoie une commande ASCII via SPI.
 *
 * Cette méthode devra convertir la commande en trame SPI et l'envoyer
 * via le périphérique SPI réel.
 *
 * @param cmd Commande ASCII à envoyer.
 * @return false pour l'instant car non implémenté.
 */
bool SpiAsciiComm::sendCommand(const QString &cmd)
{
    // TODO : implémenter l'envoi SPI
    Q_UNUSED(cmd);
    return false;
}

/**
 * @brief Analyse une trame SPI reéue.
 *
 * Cette méthode devra parser la trame ASCII recue, extraire les données,
 * puis émettre le signal newMeasurement() si une mesure valide est détectée.
 *
 * @param frame Trame brute recue via SPI.
 */
void SpiAsciiComm::parseFrame(const QByteArray &frame)
{
    // TODO : implémenter le parsing SPI
    Q_UNUSED(frame);
}
