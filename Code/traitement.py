"""
Fichier de traitement des évènements
"""


from geo.point import Point
from geo.segment import Segment


INTERSECTION = 0
NAISSANCE = 1
MORT = 2
SEG_HORIZONTAUX = 3

def maj_segmentAlive_currentPoint(segmentAlive, event):
    """
    Met à jour la liste des segments vivants à chaque nouvel évènement
    """

    if event.type_event == NAISSANCE:
        Segment.current_point = event.current_point
        #le segment courant apparait : on l'ajoute aux segments vivants
        segmentAlive.add(event.current_segment)

    elif event.type_event == MORT:
        #le segment courant disparait : on l'enleve des segments vivants
        segmentAlive.remove(event.current_segment)
        Segment.current_point = event.current_point

    #ATTENTION: un des 2 segments a pu être enlevé de la liste par une mort => pas d'échange a faire
    elif event.type_event == INTERSECTION:
    #juste mettre le point courant a jour
    #ici current_segment = (segment_gauche, segment_droit)
        #aucun des deux segments n'a été enlevé --> on échange
        if event.current_segment[1] in segmentAlive and event.current_segment[0] in segmentAlive:
            segmentAlive.remove(event.current_segment[1])
            Segment.current_point = event.current_point
            segmentAlive.add(event.current_segment[1])
        else:
            Segment.current_point = event.current_point

def find_voisins(segmentAlive, event):
    """
    Retourne un couple de segment (voisin_gauche, voisin_droite),
    tel que voisin_gauche et voisin_droite sont évalués à None s'il n'y en a pas.
    """
    if event.type_event == NAISSANCE or event.type_event == MORT:
        #deuxième mort au MEME point
        if event.current_point == Segment.current_point and event.type_event == 2:
            #on descend légèrement le point courant pour conserver une liste triée
            Segment.current_point.coordinates[1] += 10**-15
        index = segmentAlive.index(event.current_segment)

        #le voisin gauche, s'il existe, a un angle plus faible que le segment courant
        #il se situe donc un indice à gauche de lui dans segmentAlive
        if index > 0:
            voisin_gauche = segmentAlive[index-1]
        else:
            voisin_gauche = None

        #le voisin droite, s'il existe, a un angle plus grand que le segment,
        #il se situe donc un indice à droite de lui dans segmentAlive
        if index < (len(segmentAlive)-1):
            voisin_droite = segmentAlive[index+1]
        else:
            voisin_droite = None

    elif event.type_event == INTERSECTION:
        # voisin_gauche = le voisin gauche du segment gauche de l'intersection
        # voisin_droit = le voisin droit du segment droit de l'intersection
        #On doit trouver l'index des voisins, il est possible qu'un et un seul des deux segments de l'intersection soit déja mort
        #cas ou aucun des deux segments est mort
        if event.current_segment[1] in segmentAlive and event.current_segment[0] in segmentAlive:
            #index_droite = place du segment droit de l'intersection dans le sorted container
            index_droite = max(segmentAlive.index(event.current_segment[1]), segmentAlive.index(event.current_segment[0]))
            #index_gauche = place du segment gauche de l'intersection dans le sortedcontainer
            index_gauche = min(segmentAlive.index(event.current_segment[1]), segmentAlive.index(event.current_segment[0]))
        #le segment gauche est déjà mort
        elif event.current_segment[1] in segmentAlive:
            index_droite = segmentAlive.index(event.current_segment[1])
            index_gauche = index_droite
        else:
            index_droite = segmentAlive.index(event.current_segment[0])
            index_gauche = index_droite

        if index_droite < (len(segmentAlive)-1):
            voisin_droite = segmentAlive[index_droite+1]
        else:
            voisin_droite = None

        if index_gauche > 0:
            voisin_gauche = segmentAlive[index_gauche-1]
        else:
            voisin_gauche = None

    return (voisin_gauche, voisin_droite)


def find_intersection(event, voisins, adjuster, cache_segments):
    """
    Renvoie les intersections pour chaque cas ainsi que les segments
    qui s'intersectent le cas échéant sous forme de liste de tuple :
    [(point_intersection, segment1, segment2)]
    """
    intersection = []
    #le segment courant n'a pas de voisins
    if voisins[0] == (None, None):
        return

    if event.type_event == NAISSANCE:
        #voisins = (voisin_gauche, voisin_droite)
        for segment_voisin in voisins:
            if segment_voisin != None and (segment_voisin, event.current_segment) not in cache_segments.keys():
                #Si couple de segment pas déja testé! (grâce au cache)
                point_tmp = segment_voisin.intersection_with(event.current_segment)
                cache_segments[(segment_voisin, event.current_segment)] = 1
                cache_segments[(event.current_segment, segment_voisin)] = 1
                #s'il existe une intersection entre le segment courant et son voisin
                if point_tmp:
                    point_intersection = adjuster.hash_point(point_tmp) #ajuste le point :)
                    intersection.append((point_intersection, event.current_segment, segment_voisin))
                    #mise en cache de l'abscisse de l'intersection
                    Segment.cache_x[(event.current_segment, point_intersection.coordinates[1])] = point_intersection.coordinates[0]
                    Segment.cache_x[(segment_voisin, point_intersection.coordinates[1])] = point_intersection.coordinates[0]

    elif event.type_event == MORT:
        #dans le cas d'une mort, on teste l'intersection de ces voisins
        #si un des deux vaut None, il n'y a pas d'intersection
        if voisins[0] and voisins[1] and (voisins[0], voisins[1]) not in cache_segments.keys(): #les deux voisins existent
        #Si couple de segment pas déja testé! (grâce au cache)
            point_tmp = voisins[0].intersection_with(voisins[1])
            cache_segments[(voisins[0], voisins[1])] = 1
            cache_segments[(voisins[1], voisins[0])] = 1
            if point_tmp:
                point_intersection = adjuster.hash_point(point_tmp)
                intersection.append((point_intersection, voisins[0], voisins[1]))
                #mise en cache de l'abscisse de l'intersection
                Segment.cache_x[(voisins[0], point_intersection.coordinates[1])] = point_intersection.coordinates[0]
                Segment.cache_x[(voisins[1], point_intersection.coordinates[1])] = point_intersection.coordinates[0]

    elif event.type_event == INTERSECTION:
        #dans le cas de l'intersection, on regarde l'intersection entre :
            #le segment droit de l'intersetion et le voisin droit
            #le segment gauche de l'intersection et le voisin gauche
        if voisins[0] and (voisins[0], event.current_segment[0]) not in cache_segments.keys(): #si il y a un voisin gauche
            cache_segments[(voisins[0], event.current_segment[0])] = 1
            cache_segments[(event.current_segment[0], voisins[0])] = 1
        #Si couple de segment pas déja testé! (grâce au cache)
            point_tmp_droit = voisins[0].intersection_with(event.current_segment[0])
            # on vérifie si il y a un point d'intersection entre voisin gauche et segment gauche de l'intersection
            if point_tmp_droit:
                point_intersection_droit = adjuster.hash_point(point_tmp_droit)
                intersection.append((point_intersection_droit, event.current_segment[0], voisins[0]))
                #mise en cache de l'abscisse de l'intersection
                Segment.cache_x[(event.current_segment[0], point_intersection_droit.coordinates[1])] = point_intersection_droit.coordinates[0]
                Segment.cache_x[(voisins[0], point_intersection_droit.coordinates[1])] = point_intersection_droit.coordinates[0]

        # Deuxième condition pour le cas où un des deux était déja mort, ie indexdroit=indexgauche
        if voisins[1] and voisins[1] != voisins[0] and (voisins[1], event.current_segment[1]) not in cache_segments.keys():
            cache_segments[(event.current_segment[1], voisins[1])] = 1
            cache_segments[(voisins[1], event.current_segment[1])] = 1
            #Si couple de segment pas déja testé! (grâce au cache)
            point_tmp_gauche = voisins[1].intersection_with(event.current_segment[1])
            if point_tmp_gauche:
                point_intersection_gauche = adjuster.hash_point(point_tmp_gauche)
                intersection.append((point_intersection_gauche, event.current_segment[1], voisins[1]))
                #mise en cache de l'abscisse de l'intersection
                Segment.cache_x[(event.current_segment[1], point_intersection_gauche.coordinates[1])] = point_intersection_gauche.coordinates[0]
                Segment.cache_x[(voisins[1], point_intersection_gauche.coordinates[1])] = point_intersection_gauche.coordinates[0]

    return intersection


def find_vivants_coupes(event, segmentAlive):
    """
    Fonction utilisée pour le cas de segments horizontaux
    Retourne une liste de segment, qui sont vivants et qui "coupes" le segment (horizontal) courant
    """
    list_vivants_coupes = []

    for segment in segmentAlive:
        #on différencie les cas coefficient directeur du segment positif et negatif
        if segment.endpoints[1].coordinates[1] > segment.endpoints[0].coordinates[1]:
            point_haut = segment.endpoints[0] #le plus en bas sur l'ecran
            point_bas = segment.endpoints[1] #le plus en haut sur l'écran
        else:
            point_haut = segment.endpoints[1]
            point_bas = segment.endpoints[0]

        if point_haut.coordinates[0] == point_bas.coordinates[0]: # cas segment vertical
            X_intersection = point_haut.coordinates[0]
        else:
            X_intersection = (event.current_point.coordinates[1]-point_haut.coordinates[1])*((point_bas.coordinates[0]-point_haut.coordinates[0])/(point_bas.coordinates[1]-point_haut.coordinates[1])) + point_haut.coordinates[0]

        #on vérifie si  X_intersection appartient à l'intervalle [x_debut ,x_fin]  du segment horizontal --> dans ce cas, le segment vivant intersecte le segment (horizontal) courant
        if X_intersection <= max(event.current_segment.endpoints[1].coordinates[0], event.current_segment.endpoints[0].coordinates[0]) and X_intersection >= \
            min(event.current_segment.endpoints[1].coordinates[0], event.current_segment.endpoints[0].coordinates[0]):
            list_vivants_coupes.append(segment)

    return list_vivants_coupes


def find_intersections_horizontales(vivants_coupes, event, adjuster):
    """
    Retourne les points d'intersections entre le segment horizontal et les segments
    qui l'intersecte sous forme de liste de points
    """

    list_intersections_horizontales = []

    for segment in vivants_coupes:
        point_intersection = event.current_segment.intersection_with(segment)
        if type(point_intersection) == Point:
            point_intersection = adjuster.hash_point(point_intersection)
            list_intersections_horizontales.append(point_intersection)

    return list_intersections_horizontales
