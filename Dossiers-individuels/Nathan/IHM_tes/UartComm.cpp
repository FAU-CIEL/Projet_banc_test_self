#include "UartComm.h"
#include <QDebug>
#include <QJsonDocument>
#include <QJsonObject>
#include <QJsonArray>

/**
 * @brief Construit la communication UART.
 * @param portName Nom du port série à utiliser.
 * @param baudrate Débit en bauds.
 * @param parent Parent Qt.
 *
 * Initialise le nom du port, le débit et connecte le signal de réception
 * du port série à la fonction de traitement des données entrantes.
 */
UartComm::UartComm(const QString &portName, int baudrate, QObject *parent)
    : CommInterface(parent),
    m_portName(portName),
    m_baudrate(baudrate)
{
    connect(&m_serial, &QSerialPort::readyRead,
            this, &UartComm::handleReadyRead);
}

/**
 * @brief Ouvre le port série.
 * @return  true si l'ouverture a réussi, false sinon.
 *
 * Si le port est déjà ouvert, il est d'abord refermé. En cas d'échec,
 * un signal d'erreur est émis.
 */
bool UartComm::open()
{
    if (m_serial.isOpen())
        m_serial.close();

    m_serial.setPortName(m_portName);
    m_serial.setBaudRate(m_baudrate);

    if (!m_serial.open(QIODevice::ReadWrite)) {
        emit errorOccurred("Impossible d'ouvrir le port " + m_portName);
        return false;
    }

    return true;
}

/**
 * @brief Ferme le port série, si necessaire.
 */
void UartComm::close()
{
    if (m_serial.isOpen())
        m_serial.close();
}

/**
 * @brief Envoie une commande ASCII sur le port série.
 * @param cmd Commande à transmettre.
 * @return  true si l'envoie a été effectué, false si le port n'est pas ouvert.
 *
 * La commande est terminée par un retour à la ligne avant la transmission.
 */
bool UartComm::sendCommand(const QString &cmd)
{
    if (!m_serial.isOpen()) {
        emit errorOccurred("Port serie non ouvert");
        return false;
    }

    QByteArray data = cmd.toUtf8();
    data.append('\n');
    m_serial.write(data);
    return true;
}

/**
 * @brief Lit les données disponibles et extrait les lignes complètes.
 *
 * Les octets reçus sont accumulés dans un tampon jusqu'à la présence d'un
 * caractère de fin de ligne. Chaque ligne complète est ensuite transmise
 * à parseLine()
 */
void UartComm::handleReadyRead()
{
    QByteArray data = m_serial.readAll();

    for (char c : data)
    {
        if (!m_jsonReceiving) {
            if (c == '{') {
                m_jsonReceiving = true;
                m_jsonBraceCount = 1;
                m_jsonAccumulator = "{";
                continue;
            }
            // Seulement les octets NON-JSON vont dans le buffer ASCII
            m_buffer.append(c);
        } else {
            m_jsonAccumulator.append(c);

            if (c == '{') m_jsonBraceCount++;
            if (c == '}') m_jsonBraceCount--;

            if (m_jsonBraceCount == 0) {
                parseJsonMeas(m_jsonAccumulator);
                m_jsonReceiving = false;
                m_jsonAccumulator.clear();
            }
        }
    }

    // Traitement ASCII (ne contient plus les données JSON)
    while (m_buffer.contains('\n'))
    {
        int idx = m_buffer.indexOf('\n');
        QString line = QString::fromUtf8(m_buffer.left(idx)).trimmed();
        m_buffer.remove(0, idx + 1);
        parseLine(line);
    }
}

/**
 * @brief Analyse une ligne reçue et traite le message correspondant.
 * @param line Ligne brute reçue depuis l'UART.
 *
 * La fonction reconnait plusieurs formats :
 * - JSON.
 * - ACK sous la forme OK;commande.
 * - erreur sous la forme ERR;code.
 * - statut sous la forme STATUS;texte.
 * - mesure sous la forme MEAS;U;I;L;ISAT.
 */
void UartComm::parseLine(const QString &line)
{
    qDebug() << "[UART RAW] len=" << line.size() << " |" << line << "|";

    if (line.isEmpty()) return;

    if (line.startsWith('{')) {
        parseJsonMeas(line);
        return;
    }

    // ACK ignore silencieusement
    if (line.startsWith("OK;"))
        return;

    // ERREUR
    if (line.startsWith("ERR;")) {
        int code = line.section(';', 1, 1).toInt();
        emit errorOccurred("Erreur " + QString::number(code));
        return;
    }

    // STATUS
    if (line.startsWith("Parametre;")) {
        QString params = line.mid(line.indexOf(';') + 1).replace(';', "  ");
        emit statusMessage("Parametre : " + params);
        return;
    }

    if (line.startsWith("inductance=")) {
        QString val = line.mid(line.indexOf('=') + 1);
        emit statusMessage("Inductance : " + val);
        return;
    }

    if (line.trimmed().toLower() == "simulation prete") {
        emit statusMessage("Simulation prete");
        return;
    }

    // MEAS
    if (line.startsWith("MEAS;")) {
        QStringList p = line.split(';');
        if (p.size() == 5) {
            Measurement m;
            m.timestamp          = QDateTime::currentDateTime();
            m.voltageV           = p[1].toDouble();
            m.currentA           = p[2].toDouble();
            m.inductanceH        = p[3].toDouble();
            m.saturationCurrentA = p[4].toDouble();
            emit newMeasurement(m);
        }
        return;
    }

    emit errorOccurred("Trame inconnue : " + line);
}


/**
 * @brief Analyse une mesure reçue au format JSON.
 * @param json Chaine JSON à interpéter.
 *
 * Les tableaux "intensite", "temps" et "tension" sont lus en parallèle.
 * Chaque triplet de valeurs génère une mesure émise via newMeasurement().
 */
void UartComm::parseJsonMeas(const QString &json)
{
    QJsonParseError err;
    QJsonDocument doc = QJsonDocument::fromJson(json.toUtf8(), &err);
    if (err.error != QJsonParseError::NoError || !doc.isObject()) {
        emit errorOccurred("JSON invalide : " + err.errorString());
        return;
    }

    QJsonObject obj = doc.object();
    QJsonArray intensites = obj.value("intensite").toArray();
    QJsonArray temps      = obj.value("temps").toArray();
    QJsonArray tensions   = obj.value("tension").toArray();

    int n = qMin(intensites.size(), qMin(temps.size(), tensions.size()));

    qDebug() << "[JSON] n=" << n;

    for (int i = 0; i < n; i++)
    {
        Measurement m;
        m.timestamp          = QDateTime::currentDateTime();
        m.currentA           = intensites[i].toDouble();
        m.voltageV           = tensions[i].toDouble();
        m.timeS              = temps[i].toDouble();
        m.saturationCurrentA = 0.0;

        if (i < n - 1)
        {
            double dI   = intensites[i + 1].toDouble() - intensites[i].toDouble();
            double dt   = temps[i + 1].toDouble()      - temps[i].toDouble();
            double dIdt = (dt > 0 ? dI / dt : 0);

            if (qAbs(dIdt) > 1e-6)
                m.inductanceH = qAbs(m.voltageV / dIdt);
            else
                m.inductanceH = 0.0;
        }
        else
        {
            double dI = intensites[i].toDouble() - intensites[i - 1].toDouble();
            double dt = temps[i].toDouble()      - temps[i - 1].toDouble();

            if (dt > 0 && qAbs(dI) > 0.1)
                m.inductanceH = qAbs(m.voltageV / (dI / dt));
            else
                m.inductanceH = 0.0;
        }

        emit newMeasurement(m);
    }

}

