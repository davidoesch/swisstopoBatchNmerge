

<!--
*** Sharing is Caring
*** 
*** 
*** 
-->



<!-- PROJECT SHIELDS -->
<!--
*** I'm using markdown "reference style" links for readability.
*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).
*** See the bottom of this document for the declaration of the reference variables
*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->
[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]
[![LinkedIn][linkedin-shield]][linkedin-url]




<!-- PROJECT LOGO -->
<br />
<p align="center">
  

  <h3 align="center">swisstopoBatchNmerge</h3>

  <p align="center">
    PC / Mac / Linux Anwendung für den Download von swisstopo Landeskarten Luftbilder Höhenmodellen
  </p>
  </p>
 
<div align="center">
 
| **Link** 	| **Typ** 	| **Betriebssystem** 	|
|:---:	|:---:	|:---:	|
| <a href="https://github.com/davidoesch/swisstopoBatchNmerge/blob/master/dist/swisstopoBatchNmerge.exe">Download</a> 	| .exe 	| [![Windows](https://svgshare.com/i/ZhY.svg)](https://github.com/davidoesch/swisstopoBatchNmerge/tree/master/dist) 	|
| <a href="#keine-installation">Installation</a> 	| ![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54) 	| [![Windows](https://svgshare.com/i/ZhY.svg)](https://github.com/davidoesch/swisstopoBatchNmerge/#keine-installation) [![macOS](https://svgshare.com/i/ZjP.svg)](https://github.com/davidoesch/swisstopoBatchNmerge/#keine-installation) [![Linux](https://svgshare.com/i/Zhy.svg)](https://github.com/davidoesch/swisstopoBatchNmerge/#keine-installation) 	|
</div>

   <p align="center">
    ·
    <a href="https://github.com/davidoesch/swisstopoBatchNmerge/issues">Report Bug</a>
    ·
    <a href="https://github.com/davidoesch/swisstopoBatchNmerge/issues">Request Feature</a>
  </p>
</p>




<!-- TABLE OF CONTENTS -->
<details open="open">
  <summary>Inhalt</summary>
  <ol>
    <li>
      <a href="#das-projekt">Das Projekt</a>
    </li>
    <li>
      <a href="#getting-started">Getting started</a>
      <ul>
        <li><a href="#voraussetzungen">Voraussetzung</a></li>
        <li><a href="#keine-installation">(Keine) Installation</a></li>
      </ul>
    </li>
    <li><a href="#beispiele">Beispiele</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgements">Acknowledgements</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## Das Projekt

![Product Name Screen Shot][product-screenshot]

Ein einfaches graphisches Werkzeug um die aktuellsten swisstopo Karten und Höhenmodell und Luftbilder für ein Gebiet (die Grösse des Fenster durch ziehen anpassen) als ein File richtig zugeschnitten zu beziehen - ist umgesetzt.

Des weiteren können die über [swisstopo website](https://www.swisstopo.admin.ch/de/geodata.html) Werkzeuge erstellten  Listen von DownloadLinks (CSV) via Kommando Zeile einfache bezogen zusammengeführt und zurechtgeschnitten werden.

Hauptfunktionen:
* Herunterladen und zusammenführen in einem Schritt. Der "fehlende letzte Schritt "  für das CSV von swisstopo
* Einfach: keine Installation nötig , graphisches Nutzerinterface   :smile:
* Automatisierter Datenbezug: über die Command Line kann eine Vielzahl von verschiedenen Datenbezügen gemacht werden

Voraussetzung: es handelt sich um Rohdatenbezug: der Speicherplatzbedarf kann je nach gewähltem Perimeter und Produkt gross sein. Für Anwendungen bei denen keine hohen Auflösungen benötigt werden, ist mit Vorteil der [PDF Export](https://help.geo.admin.ch/?ids=41&lang=de) von [map.geo.admin.ch](https://map.geo.admin.ch) oder einer der  entsprechenden api.geo.admin.ch Dienste zu nutzen.

Eine Liste häufig verwendeter Ressourcen, die ich hilfreich finde, ist in den acknowledgements aufgeführt.

#### Limitierung (current version)
- Zusammenführen und ausschneiden nur für Landeskarte , Luftbild/Swissimage und Höhenmodell/Swissalti möglich

<!-- GETTING STARTED -->
## Getting Started

Um swisstopoBatchNmerge local zu nutzen, folge diesen einfachen Schritten

### Voraussetzungen

- Windows 10  
- Mac & Linux , python 3.*

### (Keine) Installation

#### .EXE / Direkt ausführbar

Windows: .EXE -Binaries
1. Download der Datei: 
    - [swisstopoBatchNmerge.exe](https://github.com/davidoesch/swisstopoBatchNmerge/raw/master/dist/swisstopoBatchNmerge.exe)
2. Doppelklick auf  swisstopoBatchNmerge.exe


####  Ptyhon 3.* 

MAC / LINUX / Windows

1. Clone the repo
   ```sh
   git clone https://github.com/davidoesch/swisstopoBatchNmerge.git
   ```
2. Install pip packages
   ```sh
   python -m pip install -r requirements.txt 
   ```
   GDAL
   Windows: GDAL: follow this guide  https://opensourceoptions.com/blog/how-to-install-gdal-for-python-with-pip-on-windows/ folegndes wheel file hat unter WIN10 funktioniert GDAL-3.4.3-cp310-cp310-win_amd64.whl on Win10
   LINUX: https://pypi.org/project/GDAL/
   
4. plug&pray `swisstopoBatchNmerge.py`
   ```PY
   python swisstopoBatchNmerge.py
   ```



<!-- USAGE EXAMPLES -->
## Beispiele
Für WINDOWS / DOS. Für MAC LINUX jeweils `python swisstopoBatchNmerge.py` anstatt `swisstopoBatchNmerge.exe` einsetzen

### GUI starten
   ```PY
   swisstopoBatchNmerge.exe
   ```
### PROXY 
Falls du über einen PROXY (meist in Firmennetzwerken der Fall) Zugang hast, musst du den Proxy definieren

   ```PY
   swisstopoBatchNmerge.exe --PROXY http://proxy_url:proxy_port
   ```
### CSV 
Ein Liste mit einer Download URL des geo.admin.ch STAC item pro Zeile wird  abgearbeitet: heruntergeladen und zusammengeführt. 
Optionen --noMERGE 1 --PROXY http://proxy_url:proxy_port

   ```PY
   swisstopoBatchNmerge.exe --CSV "C:\Downloads\ch.swisstopo.swissimage-dop10-5H5DQOGd.csv" --noGUI 1 
   ```
### PRODUKT und PERIMETER (Vierreck) via URL
Via STAC API Aufruf kann ein swisstopo Produkt über einen viereckigen Ausschnitt bezogen werden.
- Produkte (collection): [Identifier](https://stacindex.org/catalogs/datageoadminch#/?t=collections) zB ch.swisstopo.landeskarte-farbe-10 
- Perimeter (bbox): Rechteck: Koordinatenpaar unten links (Lower left LON LAT) und oben rechts (UR LON LAT) zB  7.43,46.95,7.69,47.10 
Optionen --noMERGE 1 --noCROP 1 --PROXY http://proxy_url:proxy_port

   ```PY
   swisstopoBatchNmerge.exe --URL "https://data.geo.admin.ch/api/stac/v0.9/collections/ch.swisstopo.pixelkarte-farbe-pk50.noscale/items?bbox=7.43,46.95,7.69,47.10" --noGUI 1 
   ```
### PRODUKT und GEMEINDE 
Via StAC API und geo.admin API Aufruf kann ein swisstopo Produkt über einen Gemeinde bezogen werden.
- LOCATION : Offizieler Gemeindenamen zB "Trimmis" 
- PRODUCT: (collection): [Identifier](https://stacindex.org/catalogs/datageoadminch#/?t=collections) zB ch.swisstopo.pixelkarte-farbe-pk50.noscale 
Optionen --noMERGE 1 --noCROP 1 --PROXY http://proxy_url:proxy_port

   ```PY
   swisstopoBatchNmerge.exe --LOCATION "Trimmis" --PRODUCT "ch.swisstopo.pixelkarte-farbe-pk50.noscale" --noGUI 1 
   ```
 ### --noMERGE 
 Mit --noMERGE 1 werden die Datein nur heruntergeladen, aber nicht zusammengesetzt
 
 ### --noCROP 
 Mit --noCROP 1 werden die Datein heruntergeladen,  zusammengesetzt, aber nicht auf die BBOX oder die Gemeinde zugeschnitten
 

<!-- ROADMAP -->
## Roadmap

Siehe [open issues](https://github.com/davidoesch/swisstopoBatchNmerge/issues) bzgl liste von geplanten features (oder issues (von denen es viele hat.... )).



<!-- CONTRIBUTING -->
## Contributing

Beiträge sind das, was die Open-Source-Gemeinschaft zu einem so grossartigen Ort des Lernens, der Inspiration und der Kreativität macht. Jeder Beitrag, den du leistest, wird **dankbar geschätzt**.

1. Forke das Project
2. Erstelle  deine Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Committe deine Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push in deine Branch (`git push origin feature/AmazingFeature`)
5. Öffne ein Pull Request

## Ausführbare binaries /EXE

Die WINDOWS Version wurde mit pyinstaller realisiert. pyinstaller und gdal - das ist [so ein Sache](https://stackoverflow.com/questions/56472933/pyinstaller-executable-fails).
Lösungsschritte

1. Install pip packages
   ```sh
   pip install pyinstaller 
   ```
2. pyinstaller initial ausführen
   ```sh
   pyinstaller --noconfirm --onefile --console --add-data "<PythonPfad>/Lib/site-packages/osgeo;osgeo/" --add-data "<PythonPfad>/Lib/site-packages/customtkinter;customtkinter/"  "swisstopoBatchNmerge.py" 
   ```
3. Die Datei (`swisstopoBatchNmerge.spec`) for der Zeile (`pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher`) mit ergänzen
   ```sh
   from PyInstaller.building.datastruct import TOC
   x = 'cp310-win_amd64.pyd'
   datas_upd = TOC()

   for d in a.datas:
      if x not in d[0] and x not in d[1]:
          datas_upd.append(d)

   a.datas = datas_upd
   ```
4. pyinstaller zum zweiten mal ausführen
   ```sh
   pyinstaller swisstopoBatchNmerge.spec 
   ```
<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE` for more information.



<!-- CONTACT -->
## Contact

David Oesch - [@davidoesch](https://twitter.com/davidoesch)

Project Link: [https://github.com/davidoesch/swisstopoBatchNmerge](https://github.com/davidoesch/swisstopoBatchNmerge)



<!-- ACKNOWLEDGEMENTS -->
## Acknowledgements
* [geo.admin.ch STAC API](https://www.geo.admin.ch/stac-api)
* [geo.admin.ch REST API SEARCH](https://api3.geo.admin.ch/services/sdiservices.html#search)
* [geo.admin.ch REST API FEATURE RESSOURCE](https://api3.geo.admin.ch/services/sdiservices.html#feature-resource)
* [swisstopo Open Data ](https://www.swisstopo.admin.ch/de/geodata.html)
* [swisstopo Nutzungsbedingungen für kostenlose Geodaten und Geodienste (OGD)](https://www.swisstopo.admin.ch/de/home/meta/konditionen/geodaten/ogd.html)






<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/davidoesch/swisstopoBatchNmerge.svg?style=for-the-badge
[contributors-url]: https://github.com/davidoesch/swisstopoBatchNmerge/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/davidoesch/swisstopoBatchNmerge.svg?style=for-the-badge
[forks-url]: https://github.com/davidoesch/swisstopoBatchNmerge/network/members
[stars-shield]: https://img.shields.io/github/stars/davidoesch/swisstopoBatchNmerge.svg?style=for-the-badge
[stars-url]: https://github.com/davidoesch/swisstopoBatchNmerge/stargazers
[issues-shield]: https://img.shields.io/github/issues/davidoesch/swisstopoBatchNmerge.svg?style=for-the-badge
[issues-url]: https://github.com/davidoesch/swisstopoBatchNmerge/issues
[license-shield]: https://img.shields.io/github/license/davidoesch/swisstopoBatchNmerge.svg?style=for-the-badge
[license-url]: https://github.com/davidoesch/swisstopoBatchNmerge/blob/master/LICENSE.md
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://linkedin.com/in/davidoesch
[product-screenshot]: images/Animation1.gif
