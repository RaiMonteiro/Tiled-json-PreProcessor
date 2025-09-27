# Tiled JSON PreProcessor

**TiledPreProcessor** is a Python module that makes it easy to preprocess .json files exported from the Tiled Map Editor.

It allows you to extract useful information from layers and objects (including shapes like polygons and polylines) and save this structured data in a new JSON file.

The module's main purpose is to assist in reading, organizing, and storing data exported from Tiled, allowing developers to focus on the information needed to create and use maps within a game. This way, you don't need to worry about the technical details of Tiled's .json format—the module already delivers the data ready for use.

#

> [!IMPORTANT]
> This module was developed to be used outside of your project's main code. In other words, it serves as a tool for preprocessing map data before integrating it into your game.
> If you wish to incorporate **TiledPreProcessor** directly into your game's main code, you'll need to make the necessary adjustments to integrate it correctly into the program's flow.

#

> [!NOTE]
> Currently, the program only processes **object layers**, extracting data from both the **objects** themselves and any associated **images**.
> Support for additional layer types <ins>may be implemented in the future</ins>.
