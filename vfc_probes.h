/*****************************************************************************
 *                                                                           *
 *  This file is part of Verificarlo.                                        *
 *                                                                           *
 *  Copyright (c) 2015-2021                                                  *
 *     Verificarlo contributors                                              *
 *     Universite de Versailles St-Quentin-en-Yvelines                       *
 *     CMLA, Ecole Normale Superieure de Cachan                              *
 *                                                                           *
 *  Verificarlo is free software: you can redistribute it and/or modify      *
 *  it under the terms of the GNU General Public License as published by     *
 *  the Free Software Foundation, either version 3 of the License, or        *
 *  (at your option) any later version.                                      *
 *                                                                           *
 *  Verificarlo is distributed in the hope that it will be useful,           *
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of           *
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the            *
 *  GNU General Public License for more details.                             *
 *                                                                           *
 *  You should have received a copy of the GNU General Public License        *
 *  along with Verificarlo.  If not, see <http://www.gnu.org/licenses/>.     *
 *                                                                           *
 *****************************************************************************/

/*
 * This file defines "vfc_probes", a hashtable-based structure which can be used
 * to place "probes" in a code and store the different values of test variables.
 * These test results can then be exported in a CSV file, and used to generate a
 * Verificarlo test report.
 */

#ifndef __VFC_HASHMAP_H__
#define __VFC_HASHMAP_H__

#define __VFC_HASHMAP_HEADER__

struct vfc_hashmap_st {
  size_t nbits;
  size_t mask;

  size_t capacity;
  size_t *items;
  size_t nitems;
  size_t n_deleted_items;
};
typedef struct vfc_hashmap_st *vfc_hashmap_t;

// allocate and initialize the map
vfc_hashmap_t vfc_hashmap_create();

// get the value at an index of a map
size_t get_value_at(size_t *items, size_t i);

// get the key at an index of a map
size_t get_key_at(size_t *items, size_t i);

// set the value at an index of a map
void set_value_at(size_t *items, size_t value, size_t i);

// set the key at an index of a map
void set_key_at(size_t *items, size_t key, size_t i);

// free the map
void vfc_hashmap_destroy(vfc_hashmap_t map);

// insert an element in the map
void vfc_hashmap_insert(vfc_hashmap_t map, size_t key, void *item);

// remove an element of the map
void vfc_hashmap_remove(vfc_hashmap_t map, size_t key);

// test if an element is in the map
char vfc_hashmap_have(vfc_hashmap_t map, size_t key);

// get an element of the map
void *vfc_hashmap_get(vfc_hashmap_t map, size_t key);

// get the number of elements in the map
size_t vfc_hashmap_num_items(vfc_hashmap_t map);

// Hash function for strings
size_t vfc_hashmap_str_function(const char *id);

// Free the hashmap
void vfc_hashmap_free(vfc_hashmap_t map);

#endif
