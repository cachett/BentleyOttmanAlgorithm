#!/usr/bin/env python3
"""
Fichier implémentant la classe évènement et les fonctions de gestion du tas d'évènement
"""

import heapq
from geo.segment import Segment


class Event:
    """
    Classe utilisée pour définir les évenements
    """
    def __init__(self, type_event, current_segment, current_point):
        """
        -type_event vaut 0 dans le cas d'un évènement d'intersection,
        1 en cas de début, 2 en cas de fin, 3 en cas de segment horizontal
        -Dans le cas d'une intersection, current_segment est un couple des segments intersectés :
         (segment_gauche, segment_droite)
        """
        self.type_event = type_event
        #!!current_segm = Tableau de couple de segments intersectés dans le cas d'une intersection(gauche, droite)!!
        self.current_segment = current_segment
        self.current_point = current_point #Point droit par défaut dans le cas horizontal

    def __lt__(self, other):
        """
        Permet a heapq de comparer l'objet 'Event' par son attribu: ordonné
        On priorise par :
            1) Ordonnée
            2) Si même ordonnée:d'abord les horizontaux,les morts,les naissances,puis les intersections
            3) Si même ordonnée et meme type d'évenement :  abscisse_max à abscisse_min
            4) Si même ordonnée et même type d'évenement et même abscisse(cas extrême): trié suivant la clé des segments
        """
        if self.current_point.coordinates[1] == other.current_point.coordinates[1]: #si mm ordonnée
            if self.type_event == other.type_event: #priorise horizontaux puis mort puis naissance puis intersection
                if self.current_point.coordinates[0] == other.current_point.coordinates[0] and self.type_event != 3: #plsr naissances/mort en un mm point
                    if Segment.current_point is None: #pour l'initialisation des events car current_point = None à t = 0
                        Segment.current_point = self.current_point
                        return self.current_segment > other.current_segment
                        Segment.current_point = None
                    return self.current_segment > other.current_segment
                return self.current_point.coordinates[0] > other.current_point.coordinates[0] # si meme type, priorise de droite à gauche
            return self.type_event > other.type_event
        return self.current_point.coordinates[1] > other.current_point.coordinates[1]

    def __eq__(self, other):
        """
        opérateur d'égalité entre deux Events
        """
        return self.current_point == other.current_point and self.type_event == other.type_event and self.current_segment == other.current_segment

    def __str__(self):
        """
        Affichage des attribus de l'évenement
        """
        return "type:"+str(self.type_event)+"\npoint:" + str(self.current_point) + "\nordonnee :" + str(self.current_point.coordinates[1])+ "\ncurrent_segment:" + str(self.current_segment)



def create_event_death_birth(segment):
    """
    Retourne un évènement de naissance et de mort pour chaque segment initial
    """
    #comparaison des ordonnées pour identifier la naissance et la fin du segment
    if segment.endpoints[0].coordinates[1] < segment.endpoints[1].coordinates[1]:
        point_birth = segment.endpoints[1]
        point_death = segment.endpoints[0]
    else:
        point_birth = segment.endpoints[0]
        point_death = segment.endpoints[1]
    #creations des nouveaux évenements
    birth = Event(1, segment, point_birth)
    death = Event(2, segment, point_death)
    return birth, death


def create_event_horizontal(segment):
    """
    Retourne un évenement pour le cas horizontal
    """
    #par défaut le point courant est le point d'abscisse le plus grand
    #(c'est à dire le plus à droite) pour le cas du segment horizontal
    if segment.endpoints[0].coordinates[0] < segment.endpoints[1].coordinates[0]:
        return Event(3, segment, segment.endpoints[1])
    return Event(3, segment, segment.endpoints[0])


def initialize_tas_event(segments):
    """
    Retourne le tas d'évenement initial, contenant tout les évenements de debut et de fin de segment
    """
    tasEvents = []
    for segment in segments:
        debut, fin = segment.endpoints[0], segment.endpoints[1]
        #cas du segment horizontal
        if debut.coordinates[1] == fin.coordinates[1]:
            event = create_event_horizontal(segment)
            heapq.heappush(tasEvents, event)
        #cas naissance ou mort (on initialise donc pas de cas intersection)
        else:
            #ajout dans le cache du segment et de ces points de depart et de fin
            #--> utilisation pour les clefs, cf segment.py
            Segment.cache_x[(segment, debut.coordinates[1])] = debut.coordinates[0]
            Segment.cache_x[(segment, fin.coordinates[1])] = fin.coordinates[0]
            birth, death = create_event_death_birth(segment)
            heapq.heappush(tasEvents, birth)
            heapq.heappush(tasEvents, death)
    return tasEvents


def maj_tas_intersection(tasEvents, intersection):
    """
    Créer et ajoute l'évènement intersection au tas d'évènement (si il n'y est pas déjà)
    """
    #intersection est un tupple (point_inter, segment_courant, voisins)
    #dans le cas de l'intersection, current_segment=(segment_gauche, segment_droit)
    #donc celui de gauche est celui de plus grand angle (car ils ont la même abscisse)
    event_intersection = Event(0, [max(intersection[1], intersection[2]), min(intersection[1], intersection[2])], intersection[0])
    heapq.heappush(tasEvents, event_intersection)
    return tasEvents
