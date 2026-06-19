# 🎈 Stiftsmodel vers 25

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://blank-app-template.streamlit.app/)

### How to run it on your own machine

Prerequisite: install `uv` if you don't already have it.

```
$ curl -LsSf https://astral.sh/uv/install.sh | sh
```

1. Sync the dependencies

   ```
   $ uv sync
   ```

2. Run the app

   ```
   $ uv run streamlit run streamlit_app.py
   ```
Notes from Lars Dyhr, Dycon on June 2026:
- tried to install it on dev10 AWS c2 instance, but failed to get it running properly in its virtual container. Was following this tutorial
https://q-viper.github.io/2022/07/17/deploying-streamlit-app-with-custom-domain-in-apache2/#step-9-create-the-streamlit-project
And did get it proxy but failed to get any output from the py script.
- Then switched to try a hosted python solution using https://streamlit.io/ and a public repo on github, where I imported the code into.
- Problems was an outdated way of declaring dependencies (requirements.txt) - which should be in pyproject.toml. But even when deps where declared there some modules were not working.
- geopanda was one of the problems, that got solved (eventually) by making a direct command in the streamlit codespaces terminal (Github dev):uv add "geopandas @ git+https://github.com/geopandas/geopandas" - which finally added it to the uv.lock file
Other references sites used https://docs.astral.sh/uv/concepts/projects/dependencies/#adding-dependencies
- Currently hosted on a Free hosting plan on:
- https://stiftsmodel.streamlit.app/ - via https://share.streamlit.io/ (from my Github Account https://github.com/codespaces/)
- 
- 
