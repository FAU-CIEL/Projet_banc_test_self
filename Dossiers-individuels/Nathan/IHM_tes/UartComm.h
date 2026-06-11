#ifndef UARTCOMM_H
#define UARTCOMM_H

#include "comminterface.h"
#include <QSerialPort>
#include <QByteArray>

/**
 * @brief Communicationnnn série UART.
 *
 * Cette classe implémente l'interface CommInterface pour gérer l'ouverture
 * d'un port série, l'envoi de commandes et la reception/analyse des trames
 * de mesures.
 */
class UartComm : public CommInterface
{
    Q_OBJECT

public:
    /**
     * @brief Construit l'objet de communication UART.
     * @param portName Nom du port série à utiliser.
     * @param baudrate Débit en bauds, par défaut 115200.
     * @param parent Parent Qt.
     */
    explicit UartComm(const QString &portName,
                      int baudrate = 115200,
                      QObject *parent = nullptr);

    /**
     * @brief Ouvre le port série.
     * @return true si l'ouverture a réussi, false sinon.
     */
    bool open() override;

    /**
     * @brief Ferme le port série.
     */
    void close() override;

    /**
     * @brief Envoie une commande sur la liaison UART.
     * @param cmd Commande a transmettre.
     * @return true si l'envoie a réussi, false sinon.
     */
    bool sendCommand(const QString &cmd) override;

private slots:
    /**
     * @brief Traite les données disponibles en réception.
     *
     * Cette méthode lit les octets reçus, les accumule dans un tampon
     * et déclenche l'analyse des trames complètes.
     */
    void handleReadyRead();

private:
    QSerialPort m_serial;///< Port série utilisé pour la communication.
    QString m_portName;///< Nom port série.
    int m_baudrate;///< Débit en bauds
    QByteArray m_buffer;///< Tampon de reception.

    /**
     * @brief Analyse une ligne reçue.
     * @param line Ligne brute reçue.
     */
    void parseLine(const QString &line);


    /**
     * @brief Analyse une mesure au format JSON.
     * @param json Chaine JSON reçue.
     */
    void parseJsonMeas(const QString &json);

    QString m_jsonAccumulator; ///< Accumulateur pour reconstruction JSON.
    int m_jsonBraceCount = 0; ///< Compteur d'accolades pour détecter les blocs JSON complets.
    bool m_jsonReceiving = false; ///< Indique si une trame JSON est en cours de reception.
};

#endif // UARTCOMM_H
