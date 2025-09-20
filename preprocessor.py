import os
import json

class TiledPreProcessor:
    """
    Class responsible for processing JSON files exported from the Tiled Map Editor.

    This class allows you to:
    - Read and extract data from layers and objects (including shapes like polylines and polygons).
    - Store the processed data in a new structured JSON file.

    Args:
        rel_file_path (str): Relative path to the JSON file exported from Tiled.

    Attributes:
        abs_path (str): Absolute path to the input JSON file.
        layers (dict): Dictionary that stores data organized by layer and object.

    """

    def __init__(self, rel_file_path: str) -> None:
        self.abs_path: str = os.path.join(os.getcwd(), rel_file_path)
        self.layers: dict = dict()

    def read_data_file(self) -> None:
        """
        Reads the JSON file and extracts the data from all layers and objects.

        Objects of the 'polyline' and 'polygon' types have their points converted to lists of absolute coordinates.
        Simple objects directly store the 'x' and 'y' coordinates, as well as width and height.

        The result is stored in the `self.layers` attribute with the following structure:
            {
                "nome_da_camada": [
                    {
                        "name": str,
                        "width": float,
                        "height": float,
                        "dots": [[x1, y1], [x2, y2], ...] | opcional
                        "x": float,
                        "y": float
                    },
                    ...
                ],
                ...
            }
        """

        def extract_dots(object: dict, key: str) -> list[list]:
            origin_dot: list = [object['x'], object['y']]
            dots: list = list()

            for i in range(len(object[key])):
                new_dot: list = [origin_dot[0] + object[key][i]['x'], origin_dot[1] + object[key][i]['y']]
                dots.append(new_dot)

            return dots

        with open(self.abs_path, mode='r', encoding='utf-8') as file: data = json.load(file)

        for i in range(len(data['layers'])):
            lyr_name: str = data['layers'][i]['name']
            self.layers[lyr_name] = list()
            
            for obj_i in range(len(data['layers'][i]['objects'])):
                self.layers[lyr_name].append(dict())
                self.layers[lyr_name][obj_i]['name'] = data['layers'][i]['objects'][obj_i]['name']
                self.layers[lyr_name][obj_i]['width'] = data['layers'][i]['objects'][obj_i]['width']
                self.layers[lyr_name][obj_i]['height'] = data['layers'][i]['objects'][obj_i]['height']

                if 'polyline' in data['layers'][i]['objects'][obj_i]:
                    self.layers[lyr_name][obj_i]['dots'] = extract_dots(data['layers'][i]['objects'][obj_i], 'polyline')
                elif 'polygon' in data['layers'][i]['objects'][obj_i]:
                    self.layers[lyr_name][obj_i]['dots'] = extract_dots(data['layers'][i]['objects'][obj_i], 'polygon')
                else:
                    self.layers[lyr_name][obj_i]['x'] = data['layers'][i]['objects'][obj_i]['x']
                    self.layers[lyr_name][obj_i]['y'] = data['layers'][i]['objects'][obj_i]['y']

                # You can add any further information you feel is necessary to collect by referencing the corresponding key.
                # e.g.:
                #
                # if data['layers'][i]['objects'][obj_i]['type'] != '':
                #     self.layers[lyr_name][obj_i]['type'] = data['layers'][i]['objects'][obj_i]['type']


    def store_data(self, name: str, destiny: str = os.path.dirname(os.path.abspath(__file__))) -> None:
        """
        Stores the processed data (self.layers) in a new JSON file.

        If the file already exists, it asks the user if they want to overwrite it.

        Args:
            name (str): Name of the output file (no extension).
            destiny (str, optional): Relative path to the folder where the file will be saved.
        """

        path = os.path.join(os.getcwd(), destiny, f'{name}.json')

        def reply_loop() -> str | None:
            loop = True
            while loop:
                reply: str = input('Do you want to replace the file? [ y | n ] ')

                if reply == 'n' or reply == 'N':
                    print('End of processing.')
                    loop = False
                    return 'END_PROGRAM'
                elif reply == 'y' or reply == 'Y':
                    loop = False
                    return
                else:
                    print('\n')

        try:
            open(path, 'x') # creates a new file

        except FileExistsError:
            print(f'The file "{name}" already exists.')
            if reply_loop() == 'END_PROGRAM': return
                
        except FileNotFoundError:
            print(f'The path you entered was not found: {path}\nThe program has been terminated.')
            return
        
        with open(path, 'w', encoding='utf-8') as file: json.dump(self.layers, file, indent=2) # you can change the indentation
        print('End of processing.')


