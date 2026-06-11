#ifndef DATABASEMANAGER_H
#define DATABASEMANAGER_H

#pragma once

#include <QObject>
#include <QtSql/QSqlDatabase>
#include <QtSql/QSqlQuery>
#include <QtSql/QSqlError>
#include <QDebug>
#include "measurementmodel.h"

/**
 * @brief Gère la connexion à la base de données et les opérations CRUD associées.
 *
 * Cette classe encapsule la gestion d'une base MySQL par Qt.
 * Elle permet de créer un test, d'insérer des mesures et d'ajouter des entrées
 * dans l'historique des test.
 */
class DatabaseManager : public QObject
{
    Q_OBJECT

public:
    /**
     * @brief Constructeur de DatabaseManager.
     * @param parent Objet parent Qt.
     */
    explicit DatabaseManager(QObject *parent = nullptr);

    /**
     * @brief Destructeur de DatabaseManager.
     * Ferme automatiquement la connexion si elle est encore ouverte.
     */
    ~DatabaseManager();

    /**
     * @brief Etablit la connexion à la base de données .
     * @return true si la connexion est réussi, false sinon.
     */
    bool connect();

    /**
     * @brief Ferme la connexion à la base de données.
     */
    void disconnect();

    /**
     * @brief Crée un nouveau test dans la base.
     * @param nEchantillons Nombre d'échantillons prévus pour le test.
     * @param frequence Fréquence prévus pour le test.
     * @return L'identifiant unique crée
     */
    int createTest(int nEchantillons, double frequence);

    /**
     * @brief Insère une mesure dans la base.
     * @param testId Identifiant auquel appartient la mesure.
     * @param m Objet Measurement contenant les données de la mesure.
     */
    void insertMesure(int testId, const Measurement &m);

    /**
     * @brief Ajoute une entrée dans l'historique d'un test.
     * @param testId Identifiant test  concerné.
     * @param statut Texte décrivant l'état ou l'événement à enregistrer.
     */
    void insertHistorique(int testId, const QString &statut);

private:
    /**
     * @brief Objet représentant la connexion à la base de données.
     */
    QSqlDatabase m_db;
};

#endif // DATABASEMANAGER_H
