/*
* This file defines "ProbesHT", a hashtable-like structure which can be used
* to place "probes" in a code and store the different values of test variables.
* These test results can then be exported in a CSV file, and used to generate a
* Verificarlo test report.
*/


#include <stdlib.h>
#include <string.h>
#include <stdio.h>

#define VAR_NAME(var) #var  // Simply returns the name of var into a string


/*
* Represents a node of the hashtable. The key will be a string of the shape :
* TEST_NAME:VAR_NAME. The "values" array will contain all elements added
* with this key (so each node actually contains a key/array of values
* association, as opposed to a single key/value association).
*/

struct ProbeNode {
    char * key;
    unsigned int nValues;
    double * values;
};

typedef struct ProbeNode ProbeNode;



/*
* The actual hashtable structure. Simply contains an array of nodes.
*/

struct ProbesHT {
    unsigned int size;
    ProbeNode ** nodes;
};

typedef struct ProbesHT ProbesHT;



/*
* Initialize an empty ProbesHT instance (the hashtable's default size is 10000)
*/

void init_probes_ht(ProbesHT * probes) {
    probes->size = 10000;
    probes->nodes = (ProbeNode**) calloc(10000, sizeof(ProbeNode*));
}



/*
* Free a hashtable content, and reset its size to 0
*/

void free_probes_ht(ProbesHT * probes) {

    if(probes == NULL) {
        return;
    }

    for(unsigned i=0; i<probes->size; i++) {
        if(probes->nodes[i] != NULL) {
            if(probes->nodes[i]->values != NULL) {
                free(probes->nodes[i]->values);
            }
            free(probes->nodes[i]);
        }
    }

    free(probes->nodes);
    probes->size = 0;
}



/*
* Free and resize a hashtable (in case the default size is too small/large,
* or creates a collision error).
*/

void resize_probes_ht(ProbesHT * probes, unsigned int newSize) {
    free_probes_ht(probes);

    probes->size = newSize;
    probes->nodes = (ProbeNode**) calloc(newSize, sizeof(ProbeNode*));
}



/*
* A simple hash function returning the index associated with a key(depends on
* the table's size)
* NOTE : Use a better hash function to be closer to a uniform distribution ?
*/

unsigned int get_probe_index(char * key, unsigned int size) {

    char * c;
    unsigned int hash = 0;
    unsigned int i = 1;
    for (c=key; *c!='\0'; c++) {
        hash += (*c) * i;
        i++;
    }

    return hash % size;
}



/*
* Helper function to detect forbidden characters (':' and ',') in the keys
*/

void validate_probe_key(char * str) {
    unsigned int len = strlen(str);

    for(unsigned int i=0; i<len; i++) {
        if(str[i] == ':' || str[i] == ',') {
            fprintf(
                stderr,
                "ERROR : One of your Verificarlo probe has a ':' or ',' in its test or variable name (\"%s\"), which is forbidden\n",
                str
            );
            exit(1);
        }
    }

}



/*
* Add an element to the hashtable. If it is the first element for this
* combination of test/variable, a new node will actually be appended. Otherwise,
* a new value will be added to the existing node's array.
*/

void put_probe(
    ProbesHT * hashTable,
    char * testName, char * varName,
    double val
) {

    // Make sure testName and varName don't contain any ':' or ',', which would
    // interfere with the key/CSV encoding
    validate_probe_key(testName);
    validate_probe_key(varName);

    // Get the key, which is : testName + ":" + varName
    char * key = (char *) malloc(strlen(testName) + strlen(varName) + 2);
    strcpy(key, testName);
    strcat(key, ":");
    strcat(key, varName);

    unsigned int index = get_probe_index(key, hashTable->size);


    // If this is the first insertion with this key, append the new element to
    // the HT ...
    if(hashTable->nodes[index] == NULL) {
        hashTable->nodes[index] = (ProbeNode*) malloc(sizeof(ProbeNode));

        hashTable->nodes[index]->nValues = 1;
        hashTable->nodes[index]->values = (double*) malloc(sizeof(double));
        hashTable->nodes[index]->values[0] = val;

        // Also copy the key (which will be used when dumping the HT)
        hashTable->nodes[index]->key = (char*) malloc(
            strlen(key) * sizeof(key) + 1
        );
        strncpy(hashTable->nodes[index]->key, key, strlen(key));
    }

    // ... otherwise, just add the value to the existing node
    else {
        // Make sure that the new and old keys are the same, otherwise we have a
        // collision
        if(strcmp(key, hashTable->nodes[index]->key) != 0) {
            fprintf(
                stderr,
                "ERROR : you have a hashtable collision between two Verificarlo probes(\"%s\" and \"%s\"). Try changing the hashtable size or some of your probe's names.\n",
                key, hashTable->nodes[index]->key
            );
            exit(1);
        }

        hashTable->nodes[index]->nValues++;
        unsigned int nValues = hashTable->nodes[index]->nValues;

        hashTable->nodes[index]->values = (double*) realloc(
            hashTable->nodes[index]->values,
            nValues* sizeof(double)
        );

        hashTable->nodes[index]->values[nValues-1] = val;
    }

}



/*
* Helper function to encode a double into a Base64 string
* (based on : https://nachtimwald.com/2017/11/18/base64-encode-and-decode-in-c/)
*/

char* double_to_base64(double val) {

    // Get the size of the string to output (based on the size of a double)

    int doubleSize  = sizeof(double);
    int stringSize  = doubleSize;
    if(stringSize % 3 != 0) {
        stringSize += 3 - (stringSize % 3);
    }
    stringSize = stringSize * 4 / 3;


    // Initialize in (from val) and out (base64) strings

    char * in = (char*) malloc(doubleSize + 1);
    in[stringSize] = '\0';
    printf("in = %s\n", in);
    memcpy(in, &val, doubleSize);
    printf("in = %s\n", in);


    char * out = (char*) malloc(stringSize + 1);
    out[stringSize] = '\0';


    // Write on out string

    const char b64chars[] = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
    int i, j, v;

    for(i=0, j=0; i<doubleSize; i+=3, j+=4) {
        v = in[i];
        v = i+1 < doubleSize ? v << 8 | in[i+1] : v << 8;
        v = i+2 < doubleSize ? v << 8 | in[i+2] : v << 8;

        out[j] = b64chars[(v >> 18) & 0x3F];
        out[j+1] = b64chars[(v >> 12) & 0x3F];

        if(i+1 < doubleSize) {
            out[j+2] = b64chars[(v >> 6) & 0x3F];
        } else {
            out[j+2] = '=';
        }

        if(i+2 < doubleSize) {
            out[j+3] = b64chars[v & 0x3F];
        } else {
            out[j+3] = '=';
        }
    }

    printf("out = %s\n", out);
    free(in);

    return out;

}


/*
* Dumps a probes HT in a .csv file (the double values are converted to base 64)
*/

void dump_probes_ht(ProbesHT * probes, char * exportPath) {
    double_to_base64(42);
}
