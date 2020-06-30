# Image2Commons
Deze repo bevat Python scripts voor het uploaden van de Beeldbank van Het Utrechts Archief naar Wikimedia Commons.
De code is generiek opgezet en hierdoor hopelijk ook geschikt voor andere archieven of GLAM-instellingen.

## Werkwijze
1. Maak een tabel (CSV bestand) met relevante metadata van de te uploaden afbeeldingen.
2. Download of kopieer de afbeeldingen die je wilt uploaden naar je computer.
3. Maak een template voor Wikimedia Commons (zie `templates/` map. Binnen het template kun je gebruik maken van Mediawiki en Liquid syntax.
4. Login op Commons met het volgende commando `./login2commons You@YourBot BotPassword`. Er wordt een Session Cookie bewaard in de huidige map
5. Voer het `./img2commons` script uit. Het script heeft vier parameters:
   * CSV_FILE - de tabel met metadata van afbeeldingen die je wilt uploaden
   * META_TEMPLATE_FILE - template voor de metadata per afbeelding
   * LOCAL_IMAGE_TEMPLATE - mini template voor de bestandsnaam op je computer
   * REMOTE_IMAGE_TEMPLATE - mini template hoe het bestand remote moet gaan heten. Gebruik een leesbare en duidelijke beschrijvende naam.

Voorbeeld:
```
./img2commons csv/queryResults-1row.csv  templates/hua-photograph  templates/hua-local-file  templates/hua-remote-file
```

## Licentie
Dit script is vrij beschikbaar via de CC0 1.0 Publiek Domein Verklaring.
Bij vragen of opmerkingen mag je me mailen r.companje@hetutrechtsarchief.nl

## SPARQL query om de CSV te produceren
<https://data.netwerkdigitaalerfgoed.nl/hetutrechtsarchief/Beeldbank-voor-Wikimedia/sparql/Beeldbank-voor-Wikimedia>
```SPARQL
PREFIX dct: <http://purl.org/dc/terms/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX v: <https://archief.io/veld#>
PREFIX id: <https://archief.io/id/>
PREFIX licentie: <https://archief.io/def/fnc_lic#>

SELECT ?GUID, ?Catalogusnummer, ?Beschrijving, ?notities, group_concat(distinct ?spatial,"|") as ?spatials, group_concat(distinct ?cat,"|") as ?categorieen, ?Datering_vroegst, ?Datering_laatst, ?licentie, ?Auteursrechthouder, ?Vervaardiger, ?cxtwd_uitgdruk, ?Afmeting, ?Afmeting_2

WHERE {
  ?foto v:Deelcollectie <https://archief.io/def/Deelcollectie#Nederlandse-Spoorwegen> .
  BIND(REPLACE(str(?foto), "https://archief.io/id/", "") AS ?GUID)

  OPTIONAL { ?foto v:Catalogusnummer ?Catalogusnummer }
  OPTIONAL { ?foto v:Beschrijving ?_Beschrijving 
    BIND(REPLACE(?_Beschrijving, "<ZR>"," ") as ?Beschrijving)
  }
  #OPTIONAL { ?foto v:LBTWD ?LBTWD } # let op LBTWD ipv THWTW - komt maar 3x voor in FOT_DOC_2
  #OPTIONAL { ?foto v:THTWD ?THTWD } # let op THTWD ipv THWTW - komt niet voor in FOT_DOC_2
  OPTIONAL { ?foto v:THWTW ?trefwoord . ?trefwoord skos:closeMatch ?cat . }
  OPTIONAL { ?foto v:Afmeting ?Afmeting }
  OPTIONAL { ?foto v:Afmeting_2 ?Afmeting_2 }
  OPTIONAL { ?foto v:Datering_vroegst ?Datering_vroegst }
  OPTIONAL { ?foto v:Datering_laatst ?Datering_laatst }
  OPTIONAL { ?foto v:Auteursrechthouder/rdfs:label ?Auteursrechthouder }
  OPTIONAL { ?foto v:Vervaardiger/rdfs:label ?Vervaardiger }

  #opmerkingen etc.
  OPTIONAL { ?foto v:Opmerkingen ?Opmerkingen }
  OPTIONAL { ?foto v:Opschrift ?Opschrift }
  OPTIONAL { ?foto v:Opschrift_2 ?Opschrift_2 }
  BIND(REPLACE(CONCAT(?Opmerkingen, " ", ?Opschrift, " ", ?Opschrift_2),"<ZR>"," ") AS ?notities)

  #licentie etc.
  ?foto v:fnc_lic ?licentieURI .
  ?foto v:fnc_lic/rdfs:label ?licentie .

  OPTIONAL {?foto dct:spatial ?spatial
    FILTER strstarts(xsd:string(?spatial), "http://www.wikidata.org/entity/")
  }

  FILTER (?licentieURI IN (licentie:Publiek-Domein-10, licentie:CC0-10, licentie:CC-BY-40 )) 
} 
LIMIT 5000
OFFSET 0
```