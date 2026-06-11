#ifndef COMMINTERFACE_H
#define COMMINTERFACE_H

#pragma once
#include <QObject>
#include "measurementmodel.h"

/**
 * @brief Interface pour la communication
 *
 * Cette classe définit les méthodes de base pour ouvrir et fermer la connexion
 * et envoyer des commandes. Elle émet des signaux pour notifier la réception de nouvelles mesures ou d'erreurs.
 */
class CommInterface : public QObject
{
    Q_OBJECT
public:
    /**
     * @brief Constructeur
     * @param parent Objet parent Qt.
     */
    explicit CommInterface(QObject *parent = nullptr) : QObject(parent) {}

    /**
     * @brief Destructeur virtuel.
     */
    virtual ~CommInterface() = default;

    /**
     * @brief Ouvre la connexion.
     * @return true si la connexion est établie avec succès, flase sinon.
     */
    virtual bool open() = 0;

    /**
     * @brief Ferme la connexion.
     */
    virtual void close() = 0;

    /**
     * @brief Envoie des commandes.
     * @param cmd Commande à envoyer.
     * @return true si l'envoi a réussi, false sinon.
     */
    virtual bool sendCommand(const QString &cmd) = 0;

signals:
    /**
     * @brief Signal émis lorsqu'une nouvelle mesure est disponible
     * @param m La mesure reçue.
     */
    void newMeasurement(const Measurement &m);

    /**
     * @brief Signal émis en cas d'erreur.
     * @param err Message décrivant l'erreur.
     */
    void errorOccurred(const QString &err);

    /**
     * @brief Signal émis pour transmettre un message d'état (log, info, debug).
     * @param msg Message d'état.
     */
    void statusMessage(const QString &msg);

};


#endif // COMMINTERFACE_H
