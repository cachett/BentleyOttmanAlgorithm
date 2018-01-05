#!/usr/bin/env python3
"""
this tests bentley ottmann on given .bo files.
for each file:
    - we display segments
    - run bentley ottmann
    - display results
    - print some statistics
"""
import sys
import heapq
from sortedcontainers import SortedList
from geo.segment import load_segments
from geo.tycat import tycat
import events
import traitement

INTERSECTION = 0
NAISSANCE = 1
MORT = 2
SEG_HORIZONTAUX = 3

def test(filename):
    """
    run bentley ottmann
    """
    adjuster, segments = load_segments(filename)
    tycat(segments)
    # Initialisation du tas de départ, liste des segments vivants, clés et liste des intersections
    # tasEvents = Evenements initiaux stockés en tas pour un accès rapide au max
    tasEvents = events.initialize_tas_event(segments)
    #de droite à gauche grâce au calcul de clé
    list_intersections = [] #Liste contenant les points d'intersection
    cache_segments = dict()
    intersections_tmp = []
    # segmentAlive Contient les segments coupés par notre "ligne de vie" de manière ordonnée.
    segmentAlive = SortedList()
    #les élements sont classés selon la valeur de leur clef cad
    #les élèments de plus "grande" abscisses puis angles sont en fin de tableau

    #On itère tant qu'il reste des évènements dans le tas
    while tasEvents:
        #suppression de l'évenements courant
        event = heapq.heappop(tasEvents)
        #traitement de l'évenements courant :
        #cas d'une mort : on regarde l'intersection de ces voisins
        if event.type_event == MORT:
            #voisins est un tuple de deux segments ou de None si pas de voisins
            voisins = traitement.find_voisins(segmentAlive, event)
            traitement.maj_segmentAlive_currentPoint(segmentAlive, event)
            #intersections_tmp est une liste de tuple à 3 élèments
            intersections_tmp = traitement.find_intersection(event, voisins, adjuster, cache_segments)
        #cas d'une naissance : on regarde l'intersection du segment courant avec ces voisins
        #cas intersection:on regarde les intersections des 2 segments en intersection avec leur voisins
        elif event.type_event == INTERSECTION or event.type_event == NAISSANCE:
            #on supprime ou on ajoute le segment courant selon le type de l'évenement
            traitement.maj_segmentAlive_currentPoint(segmentAlive, event)
            voisins = traitement.find_voisins(segmentAlive, event)
            intersections_tmp = traitement.find_intersection(event, voisins, adjuster, cache_segments)
        #cas d'un segment horizontal : on cherche les segments vivants qui sont en intersection avec ce segment
        else:
            #vivants_coupes est la liste de segment vivants en intersection avec le segment courant
            vivants_coupes = traitement.find_vivants_coupes(event, segmentAlive)
            #intersections_horizontales est la liste des points d'intersection
            #du segment horizontal avec les segments vivants
            intersections_horizontales = traitement.find_intersections_horizontales(vivants_coupes, event, adjuster)
            list_intersections += intersections_horizontales

        for intersection in intersections_tmp:
             #intersection[0] correspond aux coordonnées du point d'intersection
            list_intersections.append(intersection[0])
            events.maj_tas_intersection(tasEvents, intersection) #ajout de l'intersection au tas

    total_coupes = len(list_intersections)
    list_intersections = list(set(list_intersections)) #élimine les doublons
    nbr_pts_differents = len(list_intersections)
    tycat(list_intersections, segments)
    print("le nombre d'intersections (= le nombre de points differents) est", nbr_pts_differents)
    print("le nombre de coupes dans les segments (si un point d'intersection apparait dans\
    plusieurs segments, il compte plusieurs fois) est", total_coupes, ("(<- valeur peut encore être fausse!)"))



def main():
    """
    launch test on each file.
    """

    for filename in sys.argv[1:]:
        test(filename)

main()
