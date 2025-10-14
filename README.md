# Looped Editor Themes

This repo contains Looped Automation Editor themes for Visual Studio Code.

## Using in development mode

1. Clone this repo.

2. Start the VS Code debugger, you can do this by pressing `F5` or by going to the Run tab and clicking on `Start Debugging`.

3. Make changes to the `themes/looped-dark.json` file or other theme files.


### Using the template builder

You need to have python and uv installed.

Run the following command to start the template builder:

```bash
uv run watch.py
```

This will compile the themes in the `src/themes` folder and output them as json files to the `themes` folder.