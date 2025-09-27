import TiledPreProcessor

processor = TiledPreProcessor('assets/data/maps/tiled/collisions.json') # enter the relative path here
# processor = TiledPreProcessor('assets/data/maps/tiled/collisions.json', True, Ture) # recommendation for a better approach
processor.read_data_file()
processor.store_data('test') # you can change the file name here
