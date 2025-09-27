import os
import json
from pathlib import Path

class TiledPreProcessor:
    """
    Class responsible for processing JSON files exported from the Tiled Map Editor.

    This class allows you to:
    - Read and extract data from layers and objects (including shapes like polylines and polygons).
    - Store the processed data in a new structured JSON file.

    Args:
        rel_file_path (str): Relative path to the JSON file exported from Tiled.
        image_origin_correction (bool, optional): Corrects the coordinates relative to the top-left corner of the image.
        return_image_relative_path (bool, optional): Returns the image's relative path.

    Attributes:
        abs_path (str): Absolute path to the input JSON file.
        layers (dict): Dictionary that stores data organized by layer and object.

    """

    def __init__(self, rel_file_path: str, image_origin_correction: bool = False, return_image_relative_path: bool = False) -> None:
        self.image_origin_correction: bool = image_origin_correction
        self.return_image_relative_path: bool = return_image_relative_path

        self.abs_path: str = os.path.join(os.getcwd(), rel_file_path)
        self.layers: dict = dict()

    def _extract_dots(self, object: dict, key: str) -> list[list]:
        origin_dot: list = [object['x'], object['y']]
        dots: list = list()

        for i in range(len(object[key])):
            new_dot: list = [origin_dot[0] + object[key][i]['x'], origin_dot[1] + object[key][i]['y']]
            dots.append(new_dot)

        return dots

    def _process_objects(self, data: dict, name: str, lyr_i: int, obj_i: int) -> None:
        obj: dict = data['layers'][lyr_i]['objects'][obj_i] # for better comprehension
        self.layers[name][obj_i]['name'] = obj['name']
        self.layers[name][obj_i]['width'] = obj['width']
        self.layers[name][obj_i]['height'] = obj['height']

        if 'polyline' in obj:
            self.layers[name][obj_i]['dots'] = self._extract_dots(obj, 'polyline')
        elif 'polygon' in obj:
            self.layers[name][obj_i]['dots'] = self._extract_dots(obj, 'polygon')
        else:
            self.layers[name][obj_i]['x'] = obj['x']
            self.layers[name][obj_i]['y'] = obj['y']

        # You can add any further information you feel is necessary to collect by referencing the corresponding key.
        # e.g.:
        #
        # if obj['type'] != '':
        #     self.layers[name][obj_i]['type'] = obj['type']

    def _process_images(self, data: dict, name: str, lyr_i: int, obj_i: int, gid: int) -> None:
        obj: dict = data['layers'][lyr_i]['objects'][obj_i] # for better comprehension
        self.layers[name][obj_i]['x'] = obj['x']
        self.layers[name][obj_i]['y'] = obj['y'] - obj['height'] if self.image_origin_correction else obj['y']
        self.layers[name][obj_i]['image'] = self._get_image(data, gid)

    def _rel_path(self, path: str) -> str | None:
        parts: list[str] = path.split('/')
        temp_list: list[str] = [p for p in parts  if p != '..']
        return Path(os.path.join(*temp_list)).as_posix()

    def _same_path(self, path: str) -> str | None:
        return Path(path).as_posix()

    def _image_path(self, data: dict, gid: int, i: int) -> str | None:
        for img in data['tilesets'][i]['tiles']:
            if img['id'] == gid - data['tilesets'][i]['firstgid']:
                path: str | None = self._rel_path(img['image']) if self.return_image_relative_path else self._same_path(img['image'])
                return path
            
        return None

    def _get_image(self, data: dict, gid: int) -> str:
        for i in range(len(data['tilesets'])):

            # Searching for the right tileset:
            # - firstgid <= gid < firstgid of the next tileset
            # - tileId = gid - firstgid

            if data['tilesets'][i]['firstgid'] <= gid:
                if i != len(data['tilesets']) - 1:
                    if i != len(data['tilesets']) - 1 and gid < data['tilesets'][i + 1]['firstgid']:
                        return self._image_path(data, gid, i)
                else:
                    return self._image_path(data, gid, i)


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

        with open(self.abs_path, mode='r', encoding='utf-8') as file: data = json.load(file)

        for i in range(len(data['layers'])):
            lyr_name: str = data['layers'][i]['name']
            self.layers[lyr_name] = list()

            for j in range(len(data['layers'][i]['objects'])):
                self.layers[lyr_name].append(dict())

                if 'gid' in data['layers'][i]['objects'][j]:
                    gid: int = data['layers'][i]['objects'][j]['gid']
                    self._process_images(data, lyr_name, i, j, gid)
                else:
                    self._process_objects(data, lyr_name, i, j)


    def store_data(self, name: str, destiny: str = os.path.dirname(os.path.abspath(__file__))) -> None:
        """
        Stores the processed data (self.layers) in a new JSON file.

        If the file already exists, it asks the user if they want to overwrite it.

        Args:
            name (str): Name of the output file (no extension).
            destiny (str, optional): Relative path to the folder where the file will be saved.
        """

        path: str = Path(os.path.join(os.getcwd(), Path(destiny), f'{name}.json')).as_posix()
        
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
        
        try:
            with open(path, 'w', encoding='utf-8') as file: json.dump(self.layers, file, indent=2) # you can change the indentation
            print(f'\n{Path(path)}\nEnd of processing.')

        except Exception as e:
            print('Unexpected Error:', e)
