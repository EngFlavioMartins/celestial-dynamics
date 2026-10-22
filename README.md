# Celestial dynamics

<p align="center">
  <a href="https://github.com/EngFlavioMartins/celestial-dynamics/actions/workflows/tests.yml"><img src="https://github.com/EngFlavioMartins/celestial-dynamics/actions/workflows/tests.yml/badge.svg" alt="Python checks"></a>
  <a href="https://doi.org/10.1590/1806-9126-rbef-2017-0174"><img src="https://img.shields.io/badge/paper-10.1590%2F1806--9126--rbef--2017--0174-1F6FEB" alt="paper: 10.1590/1806-9126-rbef-2017-0174"></a>
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/python-3.10%2B-3776AB?logo=python&logoColor=white" alt="python: 3.10+"></a>
  <a href="https://github.com/EngFlavioMartins/celestial-dynamics/blob/HEAD/LICENSE"><img src="https://img.shields.io/badge/license-Apache%202.0-2E7D32" alt="license: Apache 2.0"></a>
  <a href="https://engflaviomartins.github.io/#celestial-dynamics"><img src="https://img.shields.io/badge/website-research%20page-15212B" alt="website: research page"></a>
</p>

**Orbits, Lagrange points and Poincaré sections of the restricted three-body problem.**

<p align="center"><img src="docs/assets/animation.webp" width="560" alt="An orbit around the Earth traced out on the Earth-Moon effective-potential landscape, with the zero-velocity curve and the five Lagrange points"></p>

A small Python exploration of the planar circular restricted three-body problem (think Earth, Moon and a spacecraft): trajectories in the rotating frame, the five Lagrange points, zero-velocity curves and Poincaré sections. It accompanies the review by Martins & Zanotello (2018).

## Run it

```bash
git clone https://github.com/EngFlavioMartins/celestial-dynamics.git
cd celestial-dynamics
python run.py
```

`run.py` computes an Earth-Moon orbit and its Poincaré section and saves them to `outputs/demo/dynamics.png`. The first time, it installs what it needs into a private `.venv` folder (a minute or so); after that it starts at once. All you need is Python 3.10 or newer.

<details>
<summary>Prefer conda?</summary>

```bash
conda env create -f environment.yml
conda activate celestial-dynamics
python -m celestial_dynamics.cli
```

</details>

**Next:** Try `python run.py --jacobi 3.1` for another energy level. The equations are in [docs/method.md](docs/method.md).

## Figure and animation

<p align="center"><img src="docs/assets/render.webp" width="560" alt="Effective-potential landscape of the Earth-Moon system with a computed rosette orbit in the Earth's well, the zero-velocity curve and the five labelled Lagrange points"></p>

The effective potential of the Earth-Moon system with one orbit (amber), the zero-velocity curve and the five Lagrange points. The surface height is −log Ω, a display transform that keeps the wells, saddles and hills in place.

```bash
sh scripts/render/make_figure.sh          # the figure
python scripts/render/make_animation.py   # the animation at the top
```

Both need [ParaView](https://www.paraview.org/download/); the figure also needs LaTeX.

## Cite

This code accompanies the review below. If you use it, please cite:

```bibtex
@article{martins2018threebody,
  author  = {Martins, Flavio A. C. and Zanotello, M.},
  title   = {Mec{\^a}nica Celeste e a Teoria dos Sistemas Din{\^a}micos: Uma Revis{\~a}o do Problema Circular Restrito de Tr{\^e}s Corpos},
  journal = {Revista Brasileira de Ensino de F{\'\i}sica},
  volume  = {40},
  number  = {2},
  pages   = {e2310},
  year    = {2018},
  doi     = {10.1590/1806-9126-rbef-2017-0174}
}
```

GitHub's **Cite this repository** button (from [CITATION.cff](CITATION.cff)) gives the same reference in other formats.

## Licence

[Apache 2.0](LICENSE): you are free to use, change and share this code, also commercially. If you pass it on, keep the [NOTICE](NOTICE) file with it; it says where the code comes from and how to cite it.

The bundled IBM Plex Sans fonts use the [SIL Open Font Licence](src/celestial_dynamics/fonts/OFL.txt).
