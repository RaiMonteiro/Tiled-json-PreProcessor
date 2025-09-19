import TiledPreProcessor

processor = TiledPreProcessor('assets/data/maps/tiled/collisions.json') # enter the relative path here
processor.read_data_file()
processor.store_data('test') # you can change the file name here
