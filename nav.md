site_name: note
site_description: 学习笔记
site_url: https://note.malinkang.com/
site_author: malinkang
## Repository
repo_name: malinkang/note
repo_url: https://github.com/malinkang/note

# Copyright
copyright: Copyright &copy; 2013 - 2021 malinkang

theme:
  name: null
  custom_dir: !ENV [THEME_DIR, "material"]
  logo: https://avatars.githubusercontent.com/u/3365208?v=4
  # Don't include MkDocs' JavaScript
  include_search_page: false
  search_index_only: true

  # Default values, taken from mkdocs_theme.yml
  language: en
  
  features:
    - content.code.annotate-code
    - navigation.tabs
    - navigation.top
  palette:
    - scheme: default
      primary: light-blue
      accent: light-blue
      toggle:
        icon: material/toggle-switch-off-outline
        name: Switch to dark mode
    - scheme: slate
      primary: red
      accent: red
      toggle:
        icon: material/toggle-switch
        name: Switch to light mode
  icon:
    logo: logo
  font:
    text: Roboto
    code: Roboto Mono

extra:
  social:
    - icon: fontawesome/brands/github
      link: https://github.com/malinkang
    - icon: fontawesome/brands/twitter
      link: https://twitter.com/malinkang
    - icon: fontawesome/brands/instagram
      link: https://instagram.com/malinkang
    - icon: fontawesome/brands/telegram
      link: https://t.me/malinkang
    - icon: fontawesome/brands/weibo
      link: https://weibo.com/malinkang
    - icon: fontawesome/brands/medium
      link: https://medium.com/malinkang

# Extensions
markdown_extensions:
  - abbr
  - admonition
  - attr_list
  - def_list
  - footnotes
  - meta
  - md_in_html
  - toc:
      permalink: true
  - pymdownx.arithmatex:
      generic: true
  - pymdownx.betterem:
      smart_enable: all
  - pymdownx.caret
  - pymdownx.details
  - pymdownx.emoji:
      emoji_generator: !!python/name:materialx.emoji.to_svg
      emoji_index: !!python/name:materialx.emoji.twemoji
  - pymdownx.highlight:
      anchor_linenums: true
  - pymdownx.inlinehilite
  - pymdownx.keys
  - pymdownx.magiclink:
      repo_url_shorthand: true
      user: squidfunk
      repo: mkdocs-material
  - pymdownx.mark
  - pymdownx.smartsymbols
  - pymdownx.superfences:
      custom_fences:
        - name: mermaid
          class: mermaid
          format: !!python/name:pymdownx.superfences.fence_code_format
  - pymdownx.tabbed:
      alternate_style: true
  - pymdownx.tasklist:
      custom_checkbox: true
  - pymdownx.tilde

nav:
