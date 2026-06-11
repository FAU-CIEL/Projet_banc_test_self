#ifndef SPI_ASCII_COMM_H
#define SPI_ASCII_COMM_H

#include "comminterface.h"
#include <QByteArray>
#include <QString>

/**
 * @brief Communication SPI utilisant un protocole ASCII.
 *
 * Cette classe implémente l'interface CommInterface pour gérer l'ouverture,
 * la fermeture, l'envoie de commandes et l'analyse des trames reçues via SPII.
 */
class SpiAsciiComm : public CommInterface
{
    Q_OBJECT
public:
    /**
     * @brief Construit l'objjet de communication SPI ASCII.
     * @param parent Parent Qt
     */
    explicit SpiAsciiComm(QObject *parent = nullptr);

    /**
     * @brief Ouvre la communcation SPI.
     * @return ture si l'ouverture a reussi, false sinon.
     */
    bool open() override;

    /**
     * @brief Ferme la communcation SPI.
     */
    void close() override;

    /**
     * @brief Envoie une commande sous forme de texte ASCII.
     * @param cmd Commande à envoyer.
     * @return true si l'envoie a réussi, false sinon.
     */
    bool sendCommand(const QString &cmd) override;

private:
    /**
     * @brief Analyse une trame reçue au format QByteArray.
     * @param frame Trame brute reçue.
     */
    void parseFrame(const QByteArray &frame);
};

#endif // SPI_ASCII_COMM_H
