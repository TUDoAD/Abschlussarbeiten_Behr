Code from Alexander Behr @ TUDO University developed for NFDI4Cat

# setup.py
run this first, in order to set up the installation of vocexcel properly

# SKOS-plotter.py
This first translates the SKOS-Template Excel-file you created to another one with defined IRIs for the concept names.
Then, the respective SKOS-file in ttl-format as well as a dendrogram, and the documentation in html format are generated (see example dendrogram below).

# URIgenerator.py
The method URI_generation converts entries of preferred label (from column B) to concept URIs (into column A). Then it replaces the entries in columns children (column E) and related (column F) with their respective URIs.

![dendrogram](image/dendro.png?raw=true "example dendrogram from CFI-Device.xlsx")